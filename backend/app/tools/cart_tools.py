import time
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Cart, CartItem, Product, Inventory, Order, OrderItem
from app.tools.product_tools import log_agent_action
from app.services.negotiation import negotiate_dynamic_coupon

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
    
    stock = inv.stock_quantity if inv else 18
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

def apply_coupon_tool(db: Session, query: str, amount: float, product_id: str = "prod_001", user_id: str = "user_customer_01") -> Dict[str, Any]:
    start_time = time.time()
    
    # Call Dynamic AI Coupon Negotiation Engine
    negotiation_res = negotiate_dynamic_coupon(db, user_id=user_id, product_id=product_id, query=query)

    out = {
        "coupon_code": negotiation_res["coupon_code"],
        "discount_percent": negotiation_res["discount_percent"],
        "discount_amount": negotiation_res["savings"],
        "original_amount": negotiation_res["original_price"],
        "final_amount": negotiation_res["offer_price"],
        "reason": negotiation_res["reasoning"],
        "valid_seconds": negotiation_res["valid_seconds"],
        "inventory_qty": negotiation_res["inventory_qty"],
        "abandoned_history_count": negotiation_res["abandoned_history_count"]
    }
    log_agent_action(db, "customer", "negotiate_dynamic_coupon", {"query": query, "product_id": product_id, "original_amount": amount}, out, start_time)
    return out

def calculate_final_price_tool(db: Session, product_id: str, quantity: int = 1, query: str = "", user_id: str = "user_customer_01") -> Dict[str, Any]:
    start_time = time.time()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}

    original_amount = round(product.price * quantity, 2)
    coupon_res = apply_coupon_tool(db, query=query, amount=original_amount, product_id=product_id, user_id=user_id)

    out = {
        "product_id": product_id,
        "product_title": product.title,
        "unit_price": product.price,
        "quantity": quantity,
        "original_amount": original_amount,
        "coupon_code": coupon_res["coupon_code"],
        "discount_percent": coupon_res["discount_percent"],
        "discount_amount": coupon_res["discount_amount"],
        "reasoning": coupon_res["reason"],
        "valid_seconds": coupon_res["valid_seconds"],
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

def create_staged_order_tool(db: Session, cart_id: str, coupon_code: Optional[str] = None, discount_amount: float = 0.0, user_id: str = "user_customer_01") -> Dict[str, Any]:
    start_time = time.time()
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart or not cart.items:
        cart = get_or_create_cart(db, user_id)

    raw_total = sum(i.quantity * i.unit_price for i in cart.items)
    
    # Calculate final total after discount
    final_total = max(1.0, round(raw_total - discount_amount, 2))
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
        "discount_amount": discount_amount,
        "coupon_code": coupon_code,
        "total_amount": final_total,
        "status": "staged_pending_approval",
        "items_count": len(cart.items)
    }
    log_agent_action(db, "customer", "create_staged_order", {"cart_id": cart.id, "coupon_code": coupon_code}, out, start_time)
    return out
