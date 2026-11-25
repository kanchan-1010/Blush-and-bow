import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from starlette.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    print("==================================================")
    print("🧪 RUNNING BLUSH & BOW BACKEND API TEST SUITE")
    print("==================================================")
    
    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("✅ 1. GET /api/health passed:", res.json()["status"])
    
    # 2. Image assets are publicly accessible
    res = client.get("/blush_and_bow_images/03_Store_Product_Images/102_Pastel_Blossom_Daisy_Rainbow_Keychains.jpeg")
    assert res.status_code == 200, f"Image asset route failed: {res.text}"
    print("✅ 2. GET /blush_and_bow_images/... passed: product image is served")

    # 3. Get Products
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0, "No products returned"
    print(f"✅ 3. GET /api/products passed: {data['count']} active products found")
    
    # 4. Filter Products by Category
    res = client.get("/api/products?category=keychains")
    assert res.status_code == 200
    kc_data = res.json()
    print(f"✅ 3. GET /api/products?category=keychains passed: {kc_data['count']} keychains found")
    
    # 5. Search Products
    res = client.get("/api/products?q=teddy")
    assert res.status_code == 200
    search_data = res.json()
    assert search_data["count"] >= 1
    print(f"✅ 5. GET /api/products?q=teddy passed: found '{search_data['products'][0]['title']}'")

    # 5b. Rainbow cloud keychain must be available
    res = client.get("/api/products?q=rainbow")
    assert res.status_code == 200
    rainbow_data = res.json()
    assert any("Rainbow Cloud" in p["title"] for p in rainbow_data["products"]), "Rainbow cloud product not found in catalog"
    print("✅ 5b. GET /api/products?q=rainbow passed: rainbow cloud keychain is available")
    
    # 6. Apply Promo Code
    res = client.post("/api/coupons/apply", json={"code": "PRETTY10", "subtotal": 1000})
    assert res.status_code == 200
    coupon_data = res.json()
    assert coupon_data["discount_amount"] == 100
    print(f"✅ 5. POST /api/coupons/apply passed: Saved ₹{coupon_data['discount_amount']} with code PRETTY10")
    
    # 7. Place Order
    sample_order = {
        "customer_name": "Radhika Sharma",
        "customer_email": "radhika.sharma@example.com",
        "customer_phone": "+91 98765 43210",
        "shipping_address": "Flat 402, Rosewood Heights, Baner",
        "city": "Pune",
        "pincode": "411045",
        "items": [
            {"product_id": 1, "quantity": 1},
            {"product_id": 7, "quantity": 2}
        ],
        "coupon_code": "PRETTY10",
        "payment_method": "upi"
    }
    res = client.post("/api/orders", json=sample_order)
    assert res.status_code == 201, f"Order creation failed: {res.text}"
    order_data = res.json()
    order_num = order_data["order_number"]
    print(f"✅ 7. POST /api/orders passed: Created Order {order_num} (Total: ₹{order_data['total']})")
    
    # 8. Track Order
    res = client.get(f"/api/orders/{order_num}")
    assert res.status_code == 200
    track_data = res.json()
    assert track_data["customer_name"] == "Radhika Sharma"
    assert len(track_data["items"]) == 2
    print(f"✅ 7. GET /api/orders/{order_num} passed: Status '{track_data['order_status']}', City '{track_data['city']}'")
    
    # 9. Razorpay Order Integration
    res = client.post("/api/payments/razorpay/create-order", json={
        "order_number": order_num,
        "amount": order_data["total"] * 100
    })
    assert res.status_code == 200
    rzp_data = res.json()
    print(f"✅ 9. POST /api/payments/razorpay/create-order passed: Gateway Order ID {rzp_data['id']}")
    
    # 10. Newsletter Subscription
    res = client.post("/api/newsletter", json={"email": "radhika.sharma@example.com"})
    assert res.status_code == 200
    news_data = res.json()
    print(f"✅ 9. POST /api/newsletter passed: promo code '{news_data['promo_code']}' granted")
    
    # 11. Admin Inventory Summary
    res = client.get("/api/admin/inventory")
    assert res.status_code == 200
    inv_data = res.json()
    print(f"✅ 11. GET /api/admin/inventory passed: {inv_data['total_skus']} SKUs, Total Value: ₹{inv_data['total_retail_value']:,}")
    
    print("==================================================")
    print("🎉 ALL 11 TEST CASES PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
