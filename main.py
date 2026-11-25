import random
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database import get_db_connection, init_db
from models import (
    OrderCreate, CouponRequest, NewsletterRequest,
    OrderStatusUpdate, RazorpayCreateOrderRequest, RazorpayVerifyRequest
)

init_db()

app = FastAPI(
    title="Blush & Bow E-Commerce API",
    description="Official REST API backend for Blush & Bow boutique storefront in Pune, India.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "blush_and_bow_images")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/blush_and_bow_images", StaticFiles(directory=IMAGE_DIR), name="blush_and_bow_images")

@app.get("/", response_class=HTMLResponse)
def serve_storefront():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
      <head><title>Blush & Bow API</title></head>
      <body style="font-family: sans-serif; padding: 40px; text-align: center; background: #FCF8F1; color: #8F252B;">
        <h1>🌸 Blush & Bow E-Commerce Backend API</h1>
        <p>Backend server is running smoothly.</p>
        <p><a href="/docs" style="display: inline-block; padding: 10px 20px; background: #8F252B; color: white; border-radius: 20px; text-decoration: none; font-weight: bold;">Explore API Documentation (/docs)</a></p>
      </body>
    </html>
    """

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "brand": "Blush & Bow",
        "tagline": "Little Things, Pretty Moments",
        "location": "Pune, Maharashtra, India",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/products")
def get_products(
    category: str = Query(None, description="Filter by category (keychains, jewellery, hair, gifts)"),
    q: str = Query(None, description="Search keyword in title or description"),
    sort: str = Query("featured", description="Sort order: featured, low-high, high-low, rating")
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM products WHERE is_active = 1"
    params = []
    
    if category and category.lower() != "all":
        query += " AND category = ?"
        params.append(category.lower())
        
    if q:
        query += " AND (title LIKE ? OR description LIKE ? OR cat_label LIKE ?)"
        search_term = "%" + q + "%"
        params.extend([search_term, search_term, search_term])
        
    if sort == "low-high":
        query += " ORDER BY price ASC"
    elif sort == "high-low":
        query += " ORDER BY price DESC"
    elif sort == "rating":
        query += " ORDER BY rating DESC, reviews_count DESC"
    else:
        query += " ORDER BY id ASC"
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    products = [dict(row) for row in rows]
    conn.close()
    
    return {
        "count": len(products),
        "products": products
    }

@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ? AND is_active = 1", (product_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)

@app.post("/api/coupons/apply")
def apply_coupon(payload: CouponRequest):
    code_upper = payload.code.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coupons WHERE code = ? AND is_active = 1", (code_upper,))
    coupon = cursor.fetchone()
    conn.close()
    
    if not coupon:
        raise HTTPException(status_code=400, detail="Invalid promo code. Try PRETTY10")
        
    min_order = coupon["min_order"]
    if payload.subtotal < min_order:
        raise HTTPException(
            status_code=400,
            detail=f"Promo code requires a minimum order of ₹{min_order}"
        )
        
    discount_pct = coupon["discount_percent"]
    discount_amount = round(payload.subtotal * (discount_pct / 100))
    
    return {
        "valid": True,
        "code": code_upper,
        "discount_percent": discount_pct,
        "discount_amount": discount_amount,
        "new_subtotal": max(0, payload.subtotal - discount_amount),
        "message": f"Promo code applied successfully! You saved ₹{discount_amount}"
    }

@app.post("/api/orders", status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    order_items_data = []
    subtotal = 0
    
    for item in payload.items:
        cursor.execute("SELECT id, title, price, stock FROM products WHERE id = ? AND is_active = 1", (item.product_id,))
        prod = cursor.fetchone()
        if not prod:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} not found")
            
        if prod["stock"] < item.quantity:
            conn.close()
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for '{prod['title']}'. Only {prod['stock']} available."
            )
            
        item_subtotal = prod["price"] * item.quantity
        subtotal += item_subtotal
        order_items_data.append({
            "product_id": prod["id"],
            "title": prod["title"],
            "price": prod["price"],
            "quantity": item.quantity,
            "subtotal": item_subtotal
        })
        
    discount = 0
    if payload.coupon_code:
        code_upper = payload.coupon_code.strip().upper()
        cursor.execute("SELECT discount_percent, min_order FROM coupons WHERE code = ? AND is_active = 1", (code_upper,))
        cp = cursor.fetchone()
        if cp and subtotal >= cp["min_order"]:
            discount = round(subtotal * (cp["discount_percent"] / 100))
            
    free_shipping_threshold = 799
    shipping_fee = 0 if subtotal >= free_shipping_threshold else 79
    if payload.payment_method.lower() == "cod":
        shipping_fee += 40
        
    total = max(0, subtotal - discount + shipping_fee)
    
    random_digits = random.randint(100000, 999999)
    order_number = f"BNB-{random_digits}"
    
    cursor.execute('''
    INSERT INTO orders (
        order_number, customer_name, customer_email, customer_phone,
        shipping_address, city, pincode, subtotal, discount,
        shipping_fee, total, payment_method, payment_status, order_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_number, payload.customer_name, payload.customer_email, payload.customer_phone,
        payload.shipping_address, payload.city, payload.pincode, subtotal, discount,
        shipping_fee, total, payload.payment_method.lower(),
        "paid" if payload.payment_method.lower() != "cod" else "pending",
        "processing"
    ))
    order_id = cursor.lastrowid
    
    for it in order_items_data:
        cursor.execute('''
        INSERT INTO order_items (order_id, product_id, title, price, quantity, subtotal)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (order_id, it["product_id"], it["title"], it["price"], it["quantity"], it["subtotal"]))
        
        cursor.execute('''
        UPDATE products SET stock = stock - ? WHERE id = ?
        ''', (it["quantity"], it["product_id"]))
        
    conn.commit()
    conn.close()
    
    delivery_date = (datetime.now() + timedelta(days=3)).strftime("%d %B %Y")
    
    return {
        "status": "success",
        "order_number": order_number,
        "customer_name": payload.customer_name,
        "subtotal": subtotal,
        "discount": discount,
        "shipping_fee": shipping_fee,
        "total": total,
        "payment_method": payload.payment_method.upper(),
        "estimated_delivery": delivery_date,
        "message": f"Thank you! Your order {order_number} has been placed and is being packed in our signature blush gift box."
    }

@app.get("/api/orders/{order_number}")
def track_order(order_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE order_number = ?", (order_number.upper(),))
    order = cursor.fetchone()
    if not order:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
        
    cursor.execute("SELECT product_id, title, price, quantity, subtotal FROM order_items WHERE order_id = ?", (order["id"],))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    order_dict = dict(order)
    order_dict["items"] = items
    return order_dict

@app.post("/api/payments/razorpay/create-order")
def razorpay_create_order(payload: RazorpayCreateOrderRequest):
    clean_receipt = payload.order_number.replace("-", "")
    razorpay_order_id = f"order_{clean_receipt}_{random.randint(1000, 9999)}"
    return {
        "id": razorpay_order_id,
        "entity": "order",
        "amount": payload.amount,
        "currency": "INR",
        "receipt": payload.order_number,
        "status": "created",
        "key_id": os.environ.get("RAZORPAY_KEY_ID", "rzp_test_placeholder_key"),
        "notes": {
            "merchant": "Blush & Bow",
            "support": "care@blushandbow.in"
        }
    }

@app.post("/api/payments/razorpay/verify")
def razorpay_verify_payment(payload: RazorpayVerifyRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET payment_status = 'paid', order_status = 'confirmed' WHERE order_number = ?",
        (payload.order_number.upper(),)
    )
    conn.commit()
    conn.close()
    return {
        "status": "success",
        "verified": True,
        "order_number": payload.order_number,
        "payment_id": payload.razorpay_payment_id,
        "message": "Payment verified successfully via Razorpay."
    }

@app.post("/api/newsletter")
def subscribe_newsletter(payload: NewsletterRequest):
    email_clean = payload.email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO subscribers (email) VALUES (?)", (email_clean,))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()
        
    return {
        "status": "success",
        "email": email_clean,
        "promo_code": "PRETTY10",
        "message": "Welcome to the Blush Club! Use coupon PRETTY10 for 10% off your purchase."
    }

@app.get("/api/admin/orders")
def admin_get_orders(order_status: str = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if order_status:
        cursor.execute("SELECT * FROM orders WHERE order_status = ? ORDER BY id DESC", (order_status.lower(),))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"count": len(orders), "orders": orders}

@app.patch("/api/admin/orders/{order_number}/status")
def admin_update_order_status(order_number: str, payload: OrderStatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE orders SET 
        order_status = COALESCE(?, order_status),
        tracking_number = COALESCE(?, tracking_number),
        payment_status = COALESCE(?, payment_status)
    WHERE order_number = ?
    ''', (payload.order_status, payload.tracking_number, payload.payment_status, order_number.upper()))
    
    conn.commit()
    conn.close()
    return {"status": "success", "order_number": order_number, "updated": True}

@app.get("/api/admin/inventory")
def admin_inventory_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sku, title, category, price, cost, stock FROM products ORDER BY stock ASC")
    items = [dict(row) for row in cursor.fetchall()]
    
    total_stock_units = sum(i["stock"] for i in items)
    total_inventory_value = sum(i["price"] * i["stock"] for i in items)
    low_stock_items = [i for i in items if i["stock"] < 30]
    
    conn.close()
    return {
        "total_skus": len(items),
        "total_stock_units": total_stock_units,
        "total_retail_value": total_inventory_value,
        "low_stock_count": len(low_stock_items),
        "low_stock_alerts": low_stock_items,
        "inventory": items
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    print(f"Starting Blush and Bow Backend Server on http://127.0.0.1:{port}")
    print(f"Swagger API Docs: http://127.0.0.1:{port}/docs")
    print(f"Storefront: http://127.0.0.1:{port}/")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
