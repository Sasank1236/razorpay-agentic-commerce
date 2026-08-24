from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.order import CartResponse, CartItemCreate, CartItemResponse, OrderResponse, OrderCreateRequest
from app.tools.cart_tools import get_or_create_cart, add_to_cart_tool, create_staged_order_tool
from app.models import Cart, Order, Product, Inventory

router = APIRouter(prefix="/orders", tags=["Orders & Cart"])

@router.get("/cart/{user_id}", response_model=CartResponse)
def get_cart(user_id: str, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, user_id)
    items_resp = []
    subtotal = 0.0
    for item in cart.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first() if prod else None
        p_resp = None
        if prod:
            p_resp = {
                "id": prod.id,
                "title": prod.title,
                "description": prod.description,
                "category": prod.category,
                "brand": prod.brand,
                "price": prod.price,
                "original_price": prod.original_price,
                "rating": prod.rating,
                "review_count": prod.review_count,
                "specs": prod.specs,
                "tags": prod.tags,
                "image_url": prod.image_url,
                "stock_quantity": inv.stock_quantity if inv else 50
            }
        items_resp.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "product": p_resp
        })
        subtotal += item.quantity * item.unit_price

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "status": cart.status,
        "items": items_resp,
        "subtotal": subtotal
    }

@router.post("/cart/{user_id}/items")
def add_item_to_cart(user_id: str, body: CartItemCreate, db: Session = Depends(get_db)):
    res = add_to_cart_tool(db, product_id=body.product_id, quantity=body.quantity, user_id=user_id)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@router.post("/stage", response_model=OrderResponse)
def stage_order(body: OrderCreateRequest, db: Session = Depends(get_db)):
    cart = get_or_create_cart(db, body.user_id)
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    res = create_staged_order_tool(db, cart_id=cart.id, user_id=body.user_id)
    order = db.query(Order).filter(Order.id == res["order_id"]).first()

    items_resp = []
    for item in order.items:
        items_resp.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.price
        })

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_amount": order.total_amount,
        "currency": order.currency,
        "status": order.status,
        "razorpay_order_id": order.razorpay_order_id,
        "items": items_resp
    }

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    items_resp = []
    for item in order.items:
        items_resp.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.price
        })
    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_amount": order.total_amount,
        "currency": order.currency,
        "status": order.status,
        "razorpay_order_id": order.razorpay_order_id,
        "items": items_resp
    }
