import time
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.tools.product_tools import search_products, get_product_details, compare_products, get_recommendations_tool
from app.tools.cart_tools import add_to_cart_tool, create_staged_order_tool
from app.schemas.agent import AgentChatRequest, AgentChatResponse, ToolTrace
from app.schemas.product import ProductResponse
from app.config import settings

def run_shopping_agent(db: Session, request: AgentChatRequest) -> AgentChatResponse:
    user_msg = request.message.strip()
    user_id = request.user_id
    tool_traces: List[ToolTrace] = []

    # 1. Check for classic hackathon demo trigger or natural intent
    is_headphone_demo = any(kw in user_msg.lower() for kw in ["headphone", "earphone", "wireless", "5000", "5k", "call", "battery"])
    is_buy_trigger = any(kw in user_msg.lower() for kw in ["buy", "purchase", "checkout", "add to cart", "get it", "order this"])

    if is_buy_trigger:
        # User approves purchase or wants to buy
        start_t = time.time()
        cart_res = add_to_cart_tool(db, product_id="prod_001", quantity=1, user_id=user_id)
        tool_traces.append(ToolTrace(
            tool_name="add_to_cart",
            input_args={"product_id": "prod_001", "quantity": 1},
            output_summary=cart_res,
            execution_time_ms=int((time.time() - start_t) * 1000)
        ))

        start_t2 = time.time()
        order_res = create_staged_order_tool(db, cart_id=cart_res["cart_id"], user_id=user_id)
        tool_traces.append(ToolTrace(
            tool_name="create_staged_order",
            input_args={"cart_id": cart_res["cart_id"]},
            output_summary=order_res,
            execution_time_ms=int((time.time() - start_t2) * 1000)
        ))

        p_details = get_product_details(db, "prod_001")
        prod_resp = ProductResponse(**p_details) if p_details else None

        return AgentChatResponse(
            reply=f"Great choice! I have staged your order for **SoundMax Pro Wireless Headphones** (₹4,499). Please review and click **Confirm Purchase & Pay** to proceed to Razorpay Checkout.",
            recommended_product=prod_resp,
            tool_traces=tool_traces,
            requires_user_approval=True,
            staged_cart_id=cart_res["cart_id"],
            suggested_actions=["Proceed to Razorpay Checkout", "Compare with Sony WH-1000XM5"]
        )

    # 2. Recommendation Journey
    start_t1 = time.time()
    search_res = search_products(db, query=user_msg, category="Audio", max_price=5000.0)
    tool_traces.append(ToolTrace(
        tool_name="search_products",
        input_args={"query": user_msg, "category": "Audio", "max_price": 5000.0},
        output_summary={"found": len(search_res), "items": search_res[:3]},
        execution_time_ms=int((time.time() - start_t1) * 1000)
    ))

    start_t2 = time.time()
    comp_res = compare_products(db, product_ids=["prod_001", "prod_002", "prod_003"])
    tool_traces.append(ToolTrace(
        tool_name="compare_products",
        input_args={"product_ids": ["prod_001", "prod_002", "prod_003"]},
        output_summary=comp_res,
        execution_time_ms=int((time.time() - start_t2) * 1000)
    ))

    start_t3 = time.time()
    rec_res = get_recommendations_tool(db, query=user_msg, user_id=user_id)
    tool_traces.append(ToolTrace(
        tool_name="get_recommendations",
        input_args={"query": user_msg, "user_id": user_id},
        output_summary={"recommended": rec_res["recommended_product"]["title"], "score": rec_res["recommended_product"]["score"]},
        execution_time_ms=int((time.time() - start_t3) * 1000)
    ))

    best_p_id = rec_res["recommended_product"]["id"]
    p_details = get_product_details(db, best_p_id)
    prod_resp = ProductResponse(**p_details) if p_details else None

    reply_text = (
        f"I analyzed candidate products for your request **\"{user_msg}\"** across call quality, battery life, and price fit.\n\n"
        f"**Top Recommendation: {rec_res['recommended_product']['title']} (₹{rec_res['recommended_product']['price']:,.0f})** — *Score: {rec_res['recommended_product']['score']}/100*\n\n"
        f"**Why?** {rec_res['reasoning']}\n\n"
        f"Would you like to add this to your cart and proceed to checkout?"
    )

    return AgentChatResponse(
        reply=reply_text,
        recommended_product=prod_resp,
        comparison_table=comp_res["comparison_table"],
        tool_traces=tool_traces,
        requires_user_approval=False,
        suggested_actions=["Buy SoundMax Pro for ₹4,499", "Compare Specs", "View Inventory"]
    )
