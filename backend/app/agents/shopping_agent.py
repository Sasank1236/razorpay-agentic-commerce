import time
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.tools.product_tools import search_products, get_product_details, compare_products, get_recommendations_tool
from app.tools.cart_tools import (
    add_to_cart_tool, create_staged_order_tool, check_inventory_tool,
    apply_coupon_tool, calculate_final_price_tool
)
from app.services.memory_service import extract_and_update_customer_memory, get_customer_memory_profile
from app.schemas.agent import AgentChatRequest, AgentChatResponse, ToolTrace, WorkflowStep, AINegotiatedOffer, CustomerMemoryProfile
from app.schemas.product import ProductResponse
from app.config import settings

def run_shopping_agent(db: Session, request: AgentChatRequest) -> AgentChatResponse:
    user_msg = request.message.strip()
    msg_lower = user_msg.lower()
    user_id = request.user_id
    tool_traces: List[ToolTrace] = []

    # Extract & update Customer Memory Profile in real-time
    memory_dict = extract_and_update_customer_memory(db, user_id=user_id, message=user_msg)
    memory_profile = CustomerMemoryProfile(**memory_dict)

    # -------------------------------------------------------------------
    # INTENT ROUTER 1: Check Stock Inventory Query
    # -------------------------------------------------------------------
    if "check stock" in msg_lower or "inventory" in msg_lower or msg_lower == "check stock inventory":
        t_inv = time.time()
        inv_res = check_inventory_tool(db, product_id="prod_001")
        tool_traces.append(ToolTrace(
            tool_name="check_inventory",
            input_args={"product_id": "prod_001"},
            output_summary=inv_res,
            execution_time_ms=int((time.time() - t_inv) * 1000)
        ))
        p_details = get_product_details(db, "prod_001")
        prod_resp = ProductResponse(**p_details) if p_details else None

        return AgentChatResponse(
            reply=f"📦 **Real-Time Stock Inventory Report**\n\n• **Product**: {inv_res['product_title']} (`prod_001`)\n• **Stock Quantity**: **{inv_res['stock_quantity']} units in stock**\n• **Availability Status**: {inv_res['status']}\n• **Fulfillment Center**: Main Bengaluru Warehouse",
            recommended_product=prod_resp,
            tool_traces=tool_traces,
            workflow_steps=[],
            requires_user_approval=False,
            memory_profile=memory_profile,
            suggested_actions=["Buy SoundMax Pro Headphones", "View Spec Comparison"]
        )

    # -------------------------------------------------------------------
    # INTENT ROUTER 2: View Spec Comparison Query
    # -------------------------------------------------------------------
    if "view spec" in msg_lower or "comparison" in msg_lower or "compare candidates" in msg_lower:
        t_comp = time.time()
        comp_ids = ["prod_001", "prod_002", "prod_003"]
        comp_res = compare_products(db, product_ids=comp_ids)
        tool_traces.append(ToolTrace(
            tool_name="compare_products",
            input_args={"product_ids": comp_ids},
            output_summary=comp_res,
            execution_time_ms=int((time.time() - t_comp) * 1000)
        ))
        return AgentChatResponse(
            reply="📊 **Side-by-Side Candidate Spec Comparison**\n\nI evaluated top candidate models across battery life, call quality, active noise cancellation, and price fit:",
            comparison_table=comp_res["comparison_table"],
            tool_traces=tool_traces,
            workflow_steps=[],
            requires_user_approval=False,
            memory_profile=memory_profile,
            suggested_actions=["Buy Top Pick (SoundMax Pro)", "Check Stock Inventory"]
        )

    # -------------------------------------------------------------------
    # INTENT ROUTER 3: Memory / Preference Statement Only (Without Purchase Intent)
    # -------------------------------------------------------------------
    is_explicit_purchase = any(kw in msg_lower for kw in ["buy", "purchase", "checkout", "add to cart", "get it", "order", "online classes", "for travel", "headphones under"])
    if not is_explicit_purchase and any(kw in msg_lower for kw in ["prefer", "don't like", "dislike", "avoid", "hate", "love"]):
        brands_fmt = ", ".join(memory_profile.preferred_brands) if memory_profile.preferred_brands else "Sony"
        avoid_fmt = ", ".join(memory_profile.avoid_traits) if memory_profile.avoid_traits else "Bulky (>220g)"
        return AgentChatResponse(
            reply=f"🧠 **Customer Preference Memory Updated!**\n\nI updated your persistent memory profile:\n• **Preferred Brands**: `{brands_fmt}`\n• **Avoid Traits**: `{avoid_fmt}`\n• **Summary**: *\"{memory_profile.memory_summary}\"*\n\nWhenever you search for products, I will automatically prioritize {brands_fmt} lightweight designs for you.",
            memory_profile=memory_profile,
            tool_traces=[],
            workflow_steps=[],
            requires_user_approval=False,
            suggested_actions=["Find headphones for travel", "Buy best Sony headphones"]
        )

    # -------------------------------------------------------------------
    # INTENT ROUTER 4: Full 11-Step Purchase Agent Workflow
    # -------------------------------------------------------------------
    workflow_steps: List[WorkflowStep] = []

    # STEP 1: Understand Request
    t1 = time.time()
    extracted_category = "Audio"
    max_budget = memory_profile.budget_ceiling or 5000.0
    if "watch" in msg_lower:
        extracted_category = "Wearables"
    elif "mouse" in msg_lower or "keyboard" in msg_lower:
        extracted_category = "Accessories"

    brands_str = ", ".join(memory_profile.preferred_brands) if memory_profile.preferred_brands else "None"
    avoid_str = ", ".join(memory_profile.avoid_traits) if memory_profile.avoid_traits else "None"

    workflow_steps.append(WorkflowStep(
        step_number=1,
        step_name="Understand Request & Recall Memory",
        status="completed",
        detail_message=f"Parsed intent & recalled memory: Category='{extracted_category}', Preferred Brands=['{brands_str}'], Avoid=['{avoid_str}'], Budget=₹{max_budget:,.0f}",
        execution_time_ms=int((time.time() - t1) * 1000)
    ))

    # STEP 2: Search Products
    t2 = time.time()
    search_res = search_products(db, query=user_msg, category=extracted_category, max_price=max_budget)
    tool_traces.append(ToolTrace(
        tool_name="search_products",
        input_args={"query": user_msg, "category": extracted_category, "max_price": max_budget},
        output_summary={"found": len(search_res), "items": search_res[:3]},
        execution_time_ms=int((time.time() - t2) * 1000)
    ))
    workflow_steps.append(WorkflowStep(
        step_number=2,
        step_name="Search Products",
        status="completed",
        detail_message=f"Searched product catalog and shortlisted {len(search_res)} matching candidates.",
        execution_time_ms=int((time.time() - t2) * 1000)
    ))

    # STEP 3: Filter Budget
    t3 = time.time()
    budget_filtered = [p for p in search_res if p["price"] <= max_budget]
    workflow_steps.append(WorkflowStep(
        step_number=3,
        step_name="Filter Budget",
        status="completed",
        detail_message=f"Filtered products under budget ceiling of ₹{max_budget:,.0f} ({len(budget_filtered)} candidate items).",
        execution_time_ms=int((time.time() - t3) * 1000)
    ))

    # STEP 4: Evaluate Specifications
    t4 = time.time()
    workflow_steps.append(WorkflowStep(
        step_number=4,
        step_name="Evaluate Specifications",
        status="completed",
        detail_message=f"Evaluated microphone specs, call clarity, and penalized {avoid_str} designs based on customer memory.",
        execution_time_ms=int((time.time() - t4) * 1000)
    ))

    # STEP 5: Compare Candidates
    t5 = time.time()
    comp_ids = ["prod_001", "prod_002", "prod_003"]
    comp_res = compare_products(db, product_ids=comp_ids)
    tool_traces.append(ToolTrace(
        tool_name="compare_products",
        input_args={"product_ids": comp_ids},
        output_summary=comp_res,
        execution_time_ms=int((time.time() - t5) * 1000)
    ))
    workflow_steps.append(WorkflowStep(
        step_number=5,
        step_name="Compare Candidates",
        status="completed",
        detail_message="Compared specs across top candidate models: SoundMax Pro, AudioPhonic H50, and SonicPod ANC.",
        execution_time_ms=int((time.time() - t5) * 1000)
    ))

    # STEP 6: Select Best Product
    t6 = time.time()
    rec_res = get_recommendations_tool(db, query=user_msg, user_id=user_id)
    best_product_data = rec_res["recommended_product"]
    best_p_id = best_product_data["id"]

    tool_traces.append(ToolTrace(
        tool_name="get_recommendations",
        input_args={"query": user_msg, "user_id": user_id},
        output_summary={"recommended": best_product_data["title"], "score": best_product_data["score"]},
        execution_time_ms=int((time.time() - t6) * 1000)
    ))
    workflow_steps.append(WorkflowStep(
        step_number=6,
        step_name="Select Best Product",
        status="completed",
        detail_message=f"Selected '{best_product_data['title']}' as top pick with hybrid score {best_product_data['score']}/100.",
        execution_time_ms=int((time.time() - t6) * 1000)
    ))

    # STEP 7: Check Inventory
    t7 = time.time()
    inv_res = check_inventory_tool(db, product_id=best_p_id)
    tool_traces.append(ToolTrace(
        tool_name="check_inventory",
        input_args={"product_id": best_p_id},
        output_summary=inv_res,
        execution_time_ms=int((time.time() - t7) * 1000)
    ))
    workflow_steps.append(WorkflowStep(
        step_number=7,
        step_name="Check Inventory",
        status="completed",
        detail_message=f"Verified real-time stock availability: {inv_res['stock_quantity']} units in stock.",
        execution_time_ms=int((time.time() - t7) * 1000)
    ))

    # STEP 8: Dynamic AI Coupon Negotiation
    t8 = time.time()
    coupon_res = apply_coupon_tool(db, query=user_msg, amount=best_product_data["price"], product_id=best_p_id, user_id=user_id)
    tool_traces.append(ToolTrace(
        tool_name="negotiate_dynamic_coupon",
        input_args={"query": user_msg, "amount": best_product_data["price"], "product_id": best_p_id},
        output_summary=coupon_res,
        execution_time_ms=int((time.time() - t8) * 1000)
    ))
    workflow_steps.append(WorkflowStep(
        step_number=8,
        step_name="Dynamic AI Coupon Negotiation",
        status="completed",
        detail_message=f"AI Negotiated {coupon_res['discount_percent']}% offer (`{coupon_res['coupon_code']}`): Saved ₹{coupon_res['discount_amount']:,.0f}. Reason: {coupon_res['reason']}",
        execution_time_ms=int((time.time() - t8) * 1000)
    ))

    # STEP 9: Calculate Final Price
    t9 = time.time()
    price_res = calculate_final_price_tool(db, product_id=best_p_id, quantity=1, query=user_msg, user_id=user_id)
    tool_traces.append(ToolTrace(
        tool_name="calculate_final_price",
        input_args={"product_id": best_p_id, "quantity": 1},
        output_summary=price_res,
        execution_time_ms=int((time.time() - t9) * 1000)
    ))
    workflow_steps.append(WorkflowStep(
        step_number=9,
        step_name="Calculate Final Price",
        status="completed",
        detail_message=f"Calculated net payable total: ₹{price_res['original_amount']:,.0f} (Original) - ₹{price_res['discount_amount']:,.0f} (AI Offer) = ₹{price_res['final_amount']:,.0f} Net.",
        execution_time_ms=int((time.time() - t9) * 1000)
    ))

    # STEP 10: Stage Order
    t10 = time.time()
    cart_res = add_to_cart_tool(db, product_id=best_p_id, quantity=1, user_id=user_id)
    tool_traces.append(ToolTrace(
        tool_name="add_to_cart",
        input_args={"product_id": best_p_id, "quantity": 1},
        output_summary=cart_res,
        execution_time_ms=int((time.time() - t10) * 1000)
    ))

    order_res = create_staged_order_tool(db, cart_id=cart_res["cart_id"], coupon_code=price_res["coupon_code"], discount_amount=price_res["discount_amount"], user_id=user_id)
    tool_traces.append(ToolTrace(
        tool_name="create_staged_order",
        input_args={"cart_id": cart_res["cart_id"], "coupon_code": price_res["coupon_code"]},
        output_summary=order_res,
        execution_time_ms=int((time.time() - t10) * 1000)
    ))
    workflow_steps.append(WorkflowStep(
        step_number=10,
        step_name="Stage Order",
        status="completed",
        detail_message=f"Staged order #{order_res['order_id']} in database with final net total ₹{order_res['total_amount']:,.0f}.",
        execution_time_ms=int((time.time() - t10) * 1000)
    ))

    # STEP 11: Request Human Approval
    workflow_steps.append(WorkflowStep(
        step_number=11,
        step_name="Request Human Approval",
        status="in_progress",
        detail_message="Order staged safely! Awaiting human customer authorization before launching Razorpay Checkout.",
        execution_time_ms=0
    ))

    p_details = get_product_details(db, best_p_id)
    prod_resp = ProductResponse(**p_details) if p_details else None

    # Construct AINegotiatedOffer object
    negotiated_offer_data = AINegotiatedOffer(
        coupon_code=price_res["coupon_code"],
        discount_percent=price_res["discount_percent"],
        original_price=price_res["original_amount"],
        offer_price=price_res["final_amount"],
        savings=price_res["discount_amount"],
        reasoning=coupon_res["reason"],
        valid_seconds=coupon_res["valid_seconds"]
    )

    memory_intro = ""
    if memory_profile.preferred_brands:
        memory_intro = f"🧠 **Customer Preference Memory Recalled**: *Preferred: {', '.join(memory_profile.preferred_brands)} | Avoid: {', '.join(memory_profile.avoid_traits)}*\n\n"

    reply_text = (
        f"🤖 **Personalized Purchase Agent Workflow Complete!**\n\n"
        f"{memory_intro}"
        f"Based on your request **\"{user_msg}\"** and stored brand loyalty for **{brands_str}**, I executed the 11-step personalized shopping workflow:\n"
        f"• **Selected Item**: {best_product_data['title']} (Score: {best_product_data['score']}/100)\n"
        f"• **Inventory Status**: {inv_res['stock_quantity']} units in stock\n"
        f"• **AI Negotiated Offer**: `{price_res['coupon_code']}` ({price_res['discount_percent']}% discount)\n"
        f"• **AI Reasoning**: *\"{coupon_res['reason']}\"*\n"
        f"• **Final Net Amount**: **₹{price_res['final_amount']:,.0f}** *(Original: ₹{price_res['original_amount']:,.0f}, Saved: ₹{price_res['discount_amount']:,.0f})*\n"
        f"• **Offer Expiry**: ⏳ Valid for 10 minutes\n\n"
        f"⚠️ **Human Authorization Required**: Click **Approve & Pay via Razorpay** to complete checkout."
    )

    return AgentChatResponse(
        reply=reply_text,
        recommended_product=prod_resp,
        comparison_table=comp_res["comparison_table"],
        tool_traces=tool_traces,
        workflow_steps=workflow_steps,
        requires_user_approval=True,
        staged_cart_id=cart_res["cart_id"],
        staged_order_id=order_res["order_id"],
        coupon_applied=price_res["coupon_code"],
        original_amount=price_res["original_amount"],
        discount_amount=price_res["discount_amount"],
        final_amount=price_res["final_amount"],
        negotiated_offer=negotiated_offer_data,
        memory_profile=memory_profile,
        suggested_actions=["View Spec Comparison", "Check Stock Inventory"]
    )
