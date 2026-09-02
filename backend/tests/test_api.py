import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.tools.product_tools import extract_intent_from_query

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_category_intent_extraction_no_substring_bug():
    # Test 1: "Find headphones for travel" must be Audio, NOT Smartphones!
    intent1 = extract_intent_from_query("Find headphones for travel")
    assert intent1["category"] == "Audio"

    # Test 2: "I need headphones under ₹5,000 for online classes" must be Audio
    intent2 = extract_intent_from_query("I need headphones under ₹5,000 for online classes")
    assert intent2["category"] == "Audio"

    # Test 3: "best smartphones under 20k" must be Smartphones
    intent3 = extract_intent_from_query("best smartphones under 20k")
    assert intent3["category"] == "Smartphones"

    # Test 4: "best low budget laptops" must be Laptops
    intent4 = extract_intent_from_query("best low budget laptops")
    assert intent4["category"] == "Laptops"

def test_recommendation_restricts_category():
    payload = {
        "user_id": "user_customer_01",
        "message": "Find laptops under ₹60,000"
    }
    response = client.post("/api/v1/agents/customer/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_product"] is not None
    assert data["recommended_product"]["category"] == "Laptops"
    assert data["recommended_product"]["price"] <= 60000.0

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

def test_customer_memory_persistence():
    # Session 1: State preferences
    p1 = {
        "user_id": "user_customer_02",
        "message": "I prefer Sony products and I don't like bulky headphones."
    }
    res1 = client.post("/api/v1/agents/customer/chat", json=p1)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["memory_profile"] is not None
    assert "Sony" in data1["memory_profile"]["preferred_brands"]
    assert any("bulky" in t for t in data1["memory_profile"]["avoid_traits"])

    # Session 2: Query for travel using stored memory
    p2 = {
        "user_id": "user_customer_02",
        "message": "Find headphones for travel."
    }
    res2 = client.post("/api/v1/agents/customer/chat", json=p2)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["memory_profile"] is not None
    assert "Sony" in data2["memory_profile"]["preferred_brands"]

def test_agent_cart_recovery_flow():
    # 1. Fetch merchant growth insights
    res1 = client.get("/api/v1/agents/merchant/growth")
    assert res1.status_code == 200
    data1 = res1.json()
    recovery_insight = next((item for item in data1["insights"] if "Cart Recovery" in item["title"]), None)
    assert recovery_insight is not None
    assert recovery_insight["analysis_tree"] is not None
    assert "High" in recovery_insight["analysis_tree"]["product_demand"]
    assert "RECOVER5" in recovery_insight["campaign_payload"]["coupon_code"]

    # 2. Activate recovery campaign
    payload = recovery_insight["campaign_payload"]
    res2 = client.post("/api/v1/agents/merchant/campaign", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] in ["success", "activated"]

def test_closed_loop_campaign_feedback():
    # 1. Fetch merchant growth insights & feedback loops
    res1 = client.get("/api/v1/agents/merchant/growth")
    assert res1.status_code == 200
    data1 = res1.json()
    assert "campaign_feedback_loops" in data1
    assert len(data1["campaign_feedback_loops"]) >= 1
    feedback = data1["campaign_feedback_loops"][0]
    assert feedback["pre_conversion_rate"] == 9.2
    assert feedback["post_conversion_rate"] == 12.8
    assert feedback["conversion_lift_percent"] == 39.1
    assert feedback["revenue_generated"] == 18450.0
    assert "Optimize discount" in feedback["recommended_adjustment"]

    # 2. Execute optimization campaign (5% -> 3%)
    opt_payload = {
        "action_type": "optimize_discount",
        "campaign_id": feedback["campaign_id"],
        "discount_percent": 3.0
    }
    res2 = client.post("/api/v1/agents/merchant/campaign", json=opt_payload)
    assert res2.status_code == 200
    assert res2.json()["status"] == "success"

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
