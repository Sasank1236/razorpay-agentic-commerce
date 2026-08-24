from typing import Optional, Dict, Any
from pydantic import BaseModel

class CreateRazorpayOrderRequest(BaseModel):
    order_id: str

class RazorpayOrderResponse(BaseModel):
    razorpay_order_id: str
    amount: float
    amount_in_paisa: int
    currency: str
    key_id: str
    order_id: str

class VerifyPaymentRequest(BaseModel):
    order_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class VerifyPaymentResponse(BaseModel):
    success: bool
    message: str
    order_id: str
    payment_id: str
