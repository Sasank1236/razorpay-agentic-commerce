import uuid
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Order, Payment, Inventory, Cart
from app.schemas.payment import CreateRazorpayOrderRequest, RazorpayOrderResponse, VerifyPaymentRequest, VerifyPaymentResponse
from app.services.razorpay_service import razorpay_service
from app.config import settings
from app.tools.product_tools import log_agent_action

router = APIRouter(prefix="/payments", tags=["Payments & Razorpay"])

@router.post("/create-order", response_model=RazorpayOrderResponse)
def create_razorpay_order_endpoint(body: CreateRazorpayOrderRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    order = db.query(Order).filter(Order.id == body.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Internal order not found")

    # Payment Safety: Calculate amount strictly from trusted backend database (converted to paise)
    amount_in_paisa = int(round(order.total_amount * 100))

    if amount_in_paisa < 100:
        raise HTTPException(status_code=400, detail="Minimum payment amount is 100 paise (₹1.00)")

    try:
        rp_order = razorpay_service.create_order(
            internal_order_id=order.id,
            amount_in_paisa=amount_in_paisa,
            currency=order.currency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Razorpay order creation failed: {str(e)}")

    order.razorpay_order_id = rp_order["id"]
    db.commit()

    # Record Payment initiation
    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if not payment:
        payment = Payment(
            id=f"pay_{uuid.uuid4().hex[:8]}",
            order_id=order.id,
            razorpay_order_id=rp_order["id"],
            amount=order.total_amount,
            currency=order.currency,
            status="created"
        )
        db.add(payment)
        db.commit()

    log_agent_action(db, "payment_service", "create_razorpay_order", {"internal_order_id": order.id, "amount": order.total_amount}, {"razorpay_order_id": rp_order["id"]}, start_time)

    return RazorpayOrderResponse(
        razorpay_order_id=rp_order["id"],
        amount=order.total_amount,
        amount_in_paisa=amount_in_paisa,
        currency=order.currency,
        key_id=settings.RAZORPAY_KEY_ID,
        order_id=order.id
    )

@router.post("/verify", response_model=VerifyPaymentResponse)
def verify_payment_endpoint(body: VerifyPaymentRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    order = db.query(Order).filter(Order.id == body.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not body.razorpay_order_id or not body.razorpay_payment_id or not body.razorpay_signature:
        raise HTTPException(status_code=400, detail="Missing required payment verification parameters")

    is_valid = razorpay_service.verify_payment_signature(
        razorpay_order_id=body.razorpay_order_id,
        razorpay_payment_id=body.razorpay_payment_id,
        razorpay_signature=body.razorpay_signature
    )

    if not is_valid:
        payment = db.query(Payment).filter(Payment.order_id == order.id).first()
        if payment:
            payment.status = "failed"
            payment.error_details = {"error": "Invalid signature"}
            db.commit()
        raise HTTPException(status_code=400, detail="Invalid Razorpay signature. Payment verification failed.")

    # Payment Success Workflow
    order.status = "paid"
    
    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if payment:
        payment.razorpay_payment_id = body.razorpay_payment_id
        payment.razorpay_signature = body.razorpay_signature
        payment.status = "captured"

    # Reduce inventory for purchased order items
    for oi in order.items:
        inv = db.query(Inventory).filter(Inventory.product_id == oi.product_id).first()
        if inv and inv.stock_quantity >= oi.quantity:
            inv.stock_quantity -= oi.quantity

    # Mark active cart as converted
    active_cart = db.query(Cart).filter(Cart.user_id == order.user_id, Cart.status == "active").first()
    if active_cart:
        active_cart.status = "converted"

    db.commit()

    log_agent_action(db, "payment_service", "verify_payment_success", {"order_id": order.id, "razorpay_payment_id": body.razorpay_payment_id}, {"order_status": "PAID"}, start_time)

    return VerifyPaymentResponse(
        success=True,
        message="Payment verified successfully! Order has been placed.",
        order_id=order.id,
        payment_id=body.razorpay_payment_id
    )