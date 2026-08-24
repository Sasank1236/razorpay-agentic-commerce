import time
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Cart, CartItem, Product, Order, OrderItem
from app.tools.product_tools import log_agent_action

def get_or_create_cart(db: Session, user_id: str = "user_customer_01") -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id, Cart.status == "active").first()
    if not cart:
        cart = Cart(id=f"cart_{uuid.uuid4().hex[:8]}", user_id=user_id, status="active")
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def add_to_cart_tool(db: Session, product_id: str, quantity: int = 1, user_id: str = "user_customer_01") -> Dict[str, Any]:
    start_time = time.time()
    cart = get_or_create_cart(db, user_id)
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        return {"error": "Product not found"}

    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            id=f"ci_{uuid.uuid4().hex[:8]}",
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=product.price
        )
        db.add(item)

    db.commit()
    db.refresh(cart)

    subtotal = sum(i.quantity * i.unit_price for i in cart.items)
    out = {
        "cart_id": cart.id,
        "added_product": product.title,
        "quantity": quantity,
        "unit_price": product.price,
        "cart_items_count": sum(i.quantity for i in cart.items),
        "cart_subtotal": subtotal
    }
    log_agent_action(db, "customer", "add_to_cart", {"product_id": product_id, "quantity": quantity}, out, start_time)
    return out

def create_staged_order_tool(db: Session, cart_id: str, user_id: str = "user_customer_01") -> Dict[str, Any]:
    start_time = time.time()
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart or not cart.items:
        # Fallback to active cart
        cart = get_or_create_cart(db, user_id)

    total_amount = sum(i.quantity * i.unit_price for i in cart.items)
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    order = Order(
        id=order_id,
        user_id=user_id,
        total_amount=total_amount,
        currency="INR",
        status="created"
    )
    db.add(order)
    db.commit()

    for item in cart.items:
        oi = OrderItem(
            id=f"oi_{uuid.uuid4().hex[:8]}",
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.unit_price
        )
        db.add(oi)
    
    db.commit()

    out = {
        "order_id": order.id,
        "total_amount": total_amount,
        "status": "staged_pending_approval",
        "items_count": len(cart.items)
    }
    log_agent_action(db, "customer", "create_staged_order", {"cart_id": cart.id}, out, start_time)
    return out
