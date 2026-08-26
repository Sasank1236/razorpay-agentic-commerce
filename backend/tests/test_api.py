import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_products_endpoint():
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 100

def test_shopping_agent_chat():
    payload = {
        "user_id": "user_customer_01",
        "message": "I need headphones under ₹5,000 for online classes. Good mic is more important than ANC. Buy the best one."
    }
    response = client.post("/api/v1/agents/customer/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "SoundMax Pro" in data["reply"] or "Purchase Agent Workflow Complete" in data["reply"]
    assert len(data["tool_traces"]) >= 5
    assert len(data["workflow_steps"]) == 11
    assert data["negotiated_offer"] is not None
    assert data["negotiated_offer"]["discount_percent"] > 0
    assert data["negotiated_offer"]["savings"] > 0
    assert "high purchase intent" in data["negotiated_offer"]["reasoning"]
    assert data["requires_user_approval"] is True

def test_merchant_growth_agent():
    response = client.get("/api/v1/agents/merchant/growth")
    assert response.status_code == 200
    data = response.json()
    assert len(data["insights"]) >= 3
    assert "metrics_summary" in data

def test_checkout_and_razorpay_flow():
    # 1. Add product to cart
    add_resp = client.post("/api/v1/orders/cart/user_customer_01/items", json={"product_id": "prod_001", "quantity": 1})
    assert add_resp.status_code == 200

    # 2. Stage order
    stage_resp = client.post("/api/v1/orders/stage", json={"user_id": "user_customer_01"})
    assert stage_resp.status_code == 200
    order_data = stage_resp.json()
    order_id = order_data["id"]

    # 3. Create Razorpay order
    rp_resp = client.post("/api/v1/payments/create-order", json={"order_id": order_id})
    assert rp_resp.status_code == 200
    rp_data = rp_resp.json()
    assert "razorpay_order_id" in rp_data

    # 4. Verify Payment Signature
    verify_resp = client.post("/api/v1/payments/verify", json={
        "order_id": order_id,
        "razorpay_order_id": rp_data["razorpay_order_id"],
        "razorpay_payment_id": "pay_test_123456",
        "razorpay_signature": "valid_test_signature"
    })
    assert verify_resp.status_code == 200
    assert verify_resp.json()["success"] is True
