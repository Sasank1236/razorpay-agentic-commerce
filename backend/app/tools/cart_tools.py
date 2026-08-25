import time
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Cart, CartItem, Product, Inventory, Order, OrderItem
from app.tools.product_tools import log_agent_action

def get_or_create_cart(db: Session, user_id: str = "user_customer_01") -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id, Cart.status == "active").first()
    if not cart:
        cart = Cart(id=f"cart_{uuid.uuid4().hex[:8]}", user_id=user_id, status="active")
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def check_inventory_tool(db: Session, product_id: str) -> Dict[str, Any]:
    start_time = time.time()
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    product = db.query(Product).filter(Product.id == product_id).first()
    
    stock = inv.stock_quantity if inv else 50
    is_available = stock > 0

    out = {
        "product_id": product_id,
        "product_title": product.title if product else "Unknown Product",
        "stock_quantity": stock,
        "is_available": is_available,
        "status": "In Stock" if is_available else "Out of Stock"
    }
    log_agent_action(db, "customer", "check_inventory", {"product_id": product_id}, out, start_time)
    return out

def apply_coupon_tool(db: Session, query: str, amount: float) -> Dict[str, Any]:
    start_time = time.time()
    q_lower = query.lower()

    # Determine best applicable coupon code based on shopping intent
    coupon_code = "RAZORBUY5"
    discount_pct = 5.0
    reason = "5% instant AI Commerce discount applied"

    if any(kw in q_lower for kw in ["class", "student", "study", "education", "course", "school"]):
        coupon_code = "STUDENT10"
        discount_pct = 10.0
        reason = "10% Student & Online Class learning discount applied"
    elif any(kw in q_lower for kw in ["headphone", "audio", "call", "mic"]):
        coupon_code = "AUDIO5"
        discount_pct = 5.0
        reason = "5% Audio & Call clarity promotion applied"

    discount_amount = round((amount * discount_pct) / 100.0, 2)
    final_amount = round(amount - discount_amount, 2)

    out = {
        "coupon_code": coupon_code,
        "discount_percent": discount_pct,
        "discount_amount": discount_amount,
        "original_amount": amount,
        "final_amount": final_amount,
        "reason": reason
    }
    log_agent_action(db, "customer", "apply_coupon", {"query": query, "amount": amount}, out, start_time)
    return out

def calculate_final_price_tool(db: Session, product_id: str, quantity: int = 1, query: str = "") -> Dict[str, Any]:
    start_time = time.time()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}

    original_amount = round(product.price * quantity, 2)
    coupon_res = apply_coupon_tool(db, query=query, amount=original_amount)

    out = {
        "product_id": product_id,
        "product_title": product.title,
        "unit_price": product.price,
        "quantity": quantity,
        "original_amount": original_amount,
        "coupon_code": coupon_res["coupon_code"],
        "discount_percent": coupon_res["discount_percent"],
        "discount_amount": coupon_res["discount_amount"],
        "shipping_fee": 0.0,
        "final_amount": coupon_res["final_amount"]
    }
    log_agent_action(db, "customer", "calculate_final_price", {"product_id": product_id, "quantity": quantity}, out, start_time)
    return out

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

def create_staged_order_tool(db: Session, cart_id: str, coupon_code: Optional[str] = None, user_id: str = "user_customer_01") -> Dict[str, Any]:
    start_time = time.time()
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart or not cart.items:
        cart = get_or_create_cart(db, user_id)

    raw_total = sum(i.quantity * i.unit_price for i in cart.items)
    
    # Calculate discount if coupon applied
    discount = 0.0
    if coupon_code == "STUDENT10":
        discount = round(raw_total * 0.10, 2)
    elif coupon_code in ["AUDIO5", "RAZORBUY5"]:
        discount = round(raw_total * 0.05, 2)

    final_total = max(1.0, round(raw_total - discount, 2))
    order_id = f"ord_{uuid.uuid4().hex[:8]}"

    order = Order(
        id=order_id,
        user_id=user_id,
        total_amount=final_total,
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
        "original_amount": raw_total,
        "discount_amount": discount,
        "coupon_code": coupon_code,
        "total_amount": final_total,
        "status": "staged_pending_approval",
        "items_count": len(cart.items)
    }
    log_agent_action(db, "customer", "create_staged_order", {"cart_id": cart.id, "coupon_code": coupon_code}, out, start_time)
    return out
