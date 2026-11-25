from pydantic import BaseModel
from typing import List, Optional

class CartItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str
    city: str
    pincode: str
    items: List[CartItem]
    coupon_code: Optional[str] = None
    payment_method: str = "upi"

class CouponRequest(BaseModel):
    code: str
    subtotal: int

class NewsletterRequest(BaseModel):
    email: str

class OrderStatusUpdate(BaseModel):
    order_status: Optional[str] = None
    tracking_number: Optional[str] = None
    payment_status: Optional[str] = None

class RazorpayCreateOrderRequest(BaseModel):
    order_number: str
    amount: int

class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    order_number: str
