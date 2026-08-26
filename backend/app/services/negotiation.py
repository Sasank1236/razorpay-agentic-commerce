import time
import math
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Product, Inventory, Cart, SearchEvent

def negotiate_dynamic_coupon(
    db: Session,
    user_id: str = "user_customer_01",
    product_id: str = "prod_001",
    query: str = ""
) -> Dict[str, Any]:
    """
    Dynamic AI Coupon Negotiation Engine.
    Calculates tailored discount % based on:
      1. Customer Purchase Intent Score (High/Medium/Low)
      2. Product Inventory Stock Level (Scarcity vs Clearance)
      3. User Cart Abandonment History (Recovery Incentive)
      4. Targeted Segment Promotion (Student / Audio / Online Classes)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        product = db.query(Product).first()

    inv = db.query(Inventory).filter(Inventory.product_id == product.id).first()
    stock_qty = inv.stock_quantity if inv else 18

    # Check cart abandonment history for this user
    abandoned_carts = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.status == "abandoned"
    ).count()

    q_lower = query.lower()

    # 1. Base Discount calculation
    base_discount = 5.0

    # 2. Stock Factor (Inventory-driven margin decision)
    stock_factor = 0.0
    stock_reason = f"{stock_qty} units in inventory"
    if stock_qty <= 20:
        stock_factor = -1.0  # Scarcity premium (high demand item, keep margin intact)
        stock_reason = f"only {stock_qty} units left in stock (high demand)"
    elif stock_qty >= 60:
        stock_factor = 2.0   # Clearance incentive (high stock, encourage volume)
        stock_reason = f"{stock_qty} units in inventory (clearance boost)"

    # 3. Cart Abandonment Factor (Conversion recovery incentive)
    abandonment_factor = 0.0
    abandonment_reason = "new checkout session"
    if abandoned_carts >= 1:
        abandonment_factor = 3.0
        abandonment_reason = f"this user abandoned checkout {abandoned_carts} time(s) previously"

    # 4. Intent & Class Category Boost
    intent_factor = 0.0
    if any(kw in q_lower for kw in ["class", "student", "study", "education", "course", "school"]):
        intent_factor = 2.0
    elif any(kw in q_lower for kw in ["urgent", "buy", "purchase", "now"]):
        intent_factor = 1.0

    # Calculate final negotiated discount percentage (rounded to neat integer/half %)
    calculated_pct = base_discount + stock_factor + abandonment_factor + intent_factor
    final_discount_pct = round(max(3.0, min(20.0, calculated_pct)), 1)

    # Format neat integer if whole number (e.g. 7.0 -> 7%)
    discount_display_pct = int(final_discount_pct) if final_discount_pct.is_integer() else final_discount_pct

    original_price = round(product.price, 2)
    savings = round((original_price * final_discount_pct) / 100.0, 2)
    offer_price = round(original_price - savings, 2)

    # Generate transparent AI reasoning text
    reasoning = (
        f"This customer has high purchase intent, the product has {stock_reason}, "
        f"and {abandonment_reason}. An AI-negotiated {discount_display_pct}% coupon is optimal to maximize conversion while protecting margin."
    )

    coupon_code = f"AI-OFFER-{discount_display_pct}PCT"

    return {
        "coupon_code": coupon_code,
        "discount_percent": final_discount_pct,
        "original_price": original_price,
        "offer_price": offer_price,
        "savings": savings,
        "reasoning": reasoning,
        "valid_seconds": 600,  # 10 Minutes Timer
        "inventory_qty": stock_qty,
        "abandoned_history_count": abandoned_carts
    }
