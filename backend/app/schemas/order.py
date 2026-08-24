from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas.product import ProductResponse

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: str
    product_id: str
    quantity: int
    unit_price: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: str
    user_id: str
    status: str
    items: List[CartItemResponse] = []
    subtotal: float = 0.0

    class Config:
        from_attributes = True

class OrderCreateRequest(BaseModel):
    user_id: str = "user_customer_01"
    cart_id: Optional[str] = None
    items: Optional[List[CartItemCreate]] = None

class OrderResponse(BaseModel):
    id: str
    user_id: str
    total_amount: float
    currency: str
    status: str
    razorpay_order_id: Optional[str] = None
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True
