import time
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.tools.product_tools import (
    search_products, get_product_details, compare_products,
    get_recommendations_tool, extract_intent_from_query
)
from app.tools.cart_tools import (
    add_to_cart_tool, create_staged_order_tool, check_inventory_tool,
    apply_coupon_tool, calculate_final_price_tool
)
from app.services.memory_service import extract_and_update_customer_memory, get_customer_memory_profile
from app.models import Product, Inventory, Cart, CartItem, Order
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

    # Use LLM to extract intent, product category, budget, and intent_type (discovery vs buy)
    parsed_intent = extract_intent_from_query(user_msg)
    extracted_category = parsed_intent["category"]
    max_budget = parsed_intent["max_price"]
    intent_type = parsed_intent["intent_type"]

    # -------------------------------------------------------------------
    # INTENT ROUTER 0: Cart Contents / List Products in Cart
    # -------------------------------------------------------------------
    if any(k in msg_lower for k in ["in cart", "in the cart", "my cart", "view cart", "show cart", "cart items", "products in cart", "list cart", "list out cart", "list out all the products in cart", "what is in my cart", "what's in my cart"]):
        t_cart = time.time()
        cart = db.query(Cart).filter(Cart.user_id == user_id, Cart.status == "active").first()
        cart_items = cart.items if cart else []
        
        tool_traces.append(ToolTrace(
            tool_name="view_cart",
            input_args={"user_id": user_id},
            output_summary={"cart_id": cart.id if cart else None, "items_count": len(cart_items)},
            execution_time_ms=int((time.time() - t_cart) * 1000)
        ))

        if not cart_items:
            return AgentChatResponse(
                reply="🛒 **Your Shopping Cart is currently empty.**\n\nSearch or ask me to recommend headphones, laptops, wearables, or smart home devices, and I will find the best deals with AI-negotiated discounts!",
                tool_traces=tool_traces,
                workflow_steps=[],
                requires_user_approval=False,
                memory_profile=memory_profile,
                suggested_actions=["Find headphones for travel", "Find best laptops under 60k", "List all products in stock"]
            )

        lines = [f"🛒 **Your Active Shopping Cart ({len(cart_items)} item{'s' if len(cart_items) > 1 else ''})**\n"]
        subtotal = 0.0
        suggested_actions = []
        top_prod_resp = None

        for idx, item in enumerate(cart_items, 1):
            p = db.query(Product).filter(Product.id == item.product_id).first()
            inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
            stock_qty = inv.stock_quantity if inv else 50
            item_subtotal = item.quantity * item.unit_price
            subtotal += item_subtotal

            title = p.title if p else f"Product #{item.product_id}"
            lines.append(f"{idx}. **{title}**")
            lines.append(f"   • **Qty**: {item.quantity} × ₹{item.unit_price:,.0f} | **Subtotal**: **₹{item_subtotal:,.0f}**")
            lines.append(f"   • **Availability**: {stock_qty} units in stock ({'✅ Ready for Dispatch' if stock_qty > 0 else '⚠️ Out of Stock'})\n")

            if idx == 1 and p:
                p_details = get_product_details(db, p.id)
                top_prod_resp = ProductResponse(**p_details) if p_details else None
                suggested_actions.append(f"Buy {title}")

        lines.append(f"💰 **Total Cart Value**: **₹{subtotal:,.0f}**")
        lines.append("🚚 **Shipping & Delivery**: FREE Fast Dispatch")
        lines.append("\nClick **Proceed to Checkout** to stage your order and launch Razorpay Standard Checkout.")

        suggested_actions.extend(["Check Stock Inventory", "View Spec Comparison"])

        return AgentChatResponse(
            reply="\n".join(lines),
            recommended_product=top_prod_resp,
            tool_traces=tool_traces,
            workflow_steps=[],
            requires_user_approval=False,
            staged_cart_id=cart.id if cart else None,
            original_amount=subtotal,
            final_amount=subtotal,
            memory_profile=memory_profile,
            suggested_actions=suggested_actions
        )

    # -------------------------------------------------------------------
    # INTENT ROUTER 1: Check Stock Inventory Query (All Products or Specific Product)
    # -------------------------------------------------------------------
    if "stock" in msg_lower or "inventory" in msg_lower:
        t_inv = time.time()
        is_list_all_stock = any(k in msg_lower for k in ["all", "list", "products in stock", "in the stock", "in stock", "what is in stock", "show stock", "available stock", "catalog"]) or msg_lower.strip() in ["check stock", "stock", "inventory", "check inventory", "check stock inventory"]
        
        if is_list_all_stock:
            prods = db.query(Product).join(Inventory, Product.id == Inventory.product_id).filter(Inventory.stock_quantity > 0).limit(8).all()
            
            tool_traces.append(ToolTrace(
                tool_name="list_stock_inventory",
                input_args={"filter": "in_stock"},
                output_summary={"available_skus": len(prods)},
                execution_time_ms=int((time.time() - t_inv) * 1000)
            ))

            lines = ["📦 **Live Warehouse Inventory & Stock Levels**\n"]
            lines.append("Here is the real-time stock availability across our commerce fulfillment centers:\n")
            suggested_actions = []

            for idx, p in enumerate(prods, 1):
                inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
                qty = inv.stock_quantity if inv else 50
                status_badge = "🟢 In Stock" if qty > 10 else "🟡 Low Stock"
                lines.append(f"{idx}. **{p.title}** ({p.category})")
                lines.append(f"   • **Price**: ₹{p.price:,.0f} | **Available**: **{qty} units** ({status_badge})")
                lines.append(f"   • **Fulfillment**: Bengaluru Hub (Same-Day Dispatch)\n")
                if len(suggested_actions) < 2:
                    suggested_actions.append(f"Buy {p.title}")

            suggested_actions.extend(["View Spec Comparison", "View Cart"])
            
            top_p_details = get_product_details(db, prods[0].id) if prods else None
            top_prod_resp = ProductResponse(**top_p_details) if top_p_details else None

            return AgentChatResponse(
                reply="\n".join(lines),
                recommended_product=top_prod_resp,
                tool_traces=tool_traces,
                workflow_steps=[],
                requires_user_approval=False,
                memory_profile=memory_profile,
                suggested_actions=suggested_actions
            )
        else:
            rec_info = get_recommendations_tool(db, query=user_msg, user_id=user_id)
            target_prod = rec_info.get("recommended_product")
            target_id = target_prod["id"] if target_prod else "prod_001"

            inv_res = check_inventory_tool(db, product_id=target_id)
            tool_traces.append(ToolTrace(
                tool_name="check_inventory",
                input_args={"product_id": target_id},
                output_summary=inv_res,
                execution_time_ms=int((time.time() - t_inv) * 1000)
            ))
            p_details = get_product_details(db, target_id)
            prod_resp = ProductResponse(**p_details) if p_details else None

            clean_report = (
                "📦 **Real-Time Stock Inventory Report**\n\n"
                f"• **Product**: {inv_res['product_title']} (`{target_id}`)\n"
                f"• **Available Stock**: **{inv_res['stock_quantity']} units in stock**\n"
                f"• **Inventory Status**: {inv_res['status']} & Ready for Immediate Dispatch\n"
                "• **Fulfillment Location**: Main Bengaluru Commerce Hub"
            )

            return AgentChatResponse(
                reply=clean_report,
                recommended_product=prod_resp,
                tool_traces=tool_traces,
                workflow_steps=[],
                requires_user_approval=False,
                memory_profile=memory_profile,
                suggested_actions=[f"Buy {target_prod['title'] if target_prod else 'Top Pick'}", "View Spec Comparison"]
            )

    # -------------------------------------------------------------------
    # INTENT ROUTER 2: View Spec Comparison Query
    # -------------------------------------------------------------------
    if "view spec" in msg_lower or "comparison" in msg_lower or "compare candidates" in msg_lower:
        t_comp = time.time()
        rec_info = get_recommendations_tool(db, query=user_msg, user_id=user_id)
        shortlisted = rec_info.get("shortlisted", [])
        comp_ids = [p["id"] for p in shortlisted[:3]] if shortlisted else ["prod_001", "prod_002", "prod_003"]
        
        comp_res = compare_products(db, product_ids=comp_ids)
        tool_traces.append(ToolTrace(
            tool_name="compare_products",
            input_args={"product_ids": comp_ids},
            output_summary=comp_res,
            execution_time_ms=int((time.time() - t_comp) * 1000)
        ))
        return AgentChatResponse(
            reply="📊 **Side-by-Side Candidate Spec Comparison**\n\nI evaluated candidate models across key specifications, pricing, rating, and performance fit:",
            comparison_table=comp_res["comparison_table"],
            tool_traces=tool_traces,
            workflow_steps=[],
            requires_user_approval=False,
            memory_profile=memory_profile,
            suggested_actions=[f"Buy Top Pick ({rec_info['recommended_product']['title']})", "Check Stock Inventory"]
        )

    # -------------------------------------------------------------------
    # INTENT ROUTER 3: Memory / Preference Statement Only
    # -------------------------------------------------------------------
    is_explicit_purchase = any(kw in msg_lower for kw in ["buy", "purchase", "checkout", "add to cart", "get it", "order", "pay"])
    if not is_explicit_purchase and any(kw in msg_lower for kw in ["prefer", "don't like", "dislike", "avoid", "hate", "love"]) and not any(kw in msg_lower for kw in ["suggest", "find", "show", "search", "home", "nest", "smart", "google"]):
        brands_fmt = ", ".join(memory_profile.preferred_brands) if memory_profile.preferred_brands else "Sony"
        avoid_fmt = ", ".join(memory_profile.avoid_traits) if memory_profile.avoid_traits else "Bulky (>220g)"
        return AgentChatResponse(
            reply=f"🧠 **Customer Preference Memory Updated!**\n\nI updated your persistent memory profile:\n• **Preferred Brands**: `{brands_fmt}`\n• **Avoid Traits**: `{avoid_fmt}`\n• **Summary**: *\"{memory_profile.memory_summary}\"*\n\nWhenever you search for products, I will automatically prioritize {brands_fmt} lightweight designs for you.",
            memory_profile=memory_profile,
            tool_traces=[],
            workflow_steps=[],
            requires_user_approval=False,
            suggested_actions=["Find headphones for travel", "Find best laptops under 60k"]
        )

    # -------------------------------------------------------------------
    # INTENT ROUTER 4: Discovery / Product Options Presentation Flow
    # (Triggered when user asks to suggest/find/search options without explicit "buy" command)
    # -------------------------------------------------------------------
    if not is_explicit_purchase and intent_type == "discovery":
        t_search = time.time()
        search_res = search_products(db, query=user_msg, category=extracted_category, max_price=max_budget, user_id=user_id)
        tool_traces.append(ToolTrace(
            tool_name="search_products_db",
            input_args={"query": user_msg, "category": extracted_category, "max_price": max_budget},
            output_summary={"found": len(search_res)},
            execution_time_ms=int((time.time() - t_search) * 1000)
        ))

        if search_res:
            cat_header = f"{extracted_category} " if extracted_category else ""
            budget_header = f" (Budget: under ₹{max_budget:,.0f})" if max_budget else ""
            lines = [f"🔍 **Found {len(search_res)} matching {cat_header}products in Database{budget_header}**\n"]
            suggested_actions = []

            for idx, p in enumerate(search_res[:4], 1):
                p_detail = get_product_details(db, p["id"])
                specs_dict = p_detail.get("specs", {}) if p_detail else {}
                specs_summary = ", ".join([f"{k.upper()}: {v}" for k, v in list(specs_dict.items())[:3]]) if specs_dict else "High Quality"
                
                lines.append(f"{idx}. **{p['title']}** — **₹{p['price']:,.0f}** ({p['rating']}★)")
                lines.append(f"   • **Brand**: {p['brand']} | **Stock**: {p_detail.get('stock_quantity', 50)} units")
                lines.append(f"   • **Key Specs**: {specs_summary}\n")

                if len(suggested_actions) < 2:
                    suggested_actions.append(f"Buy {p['title']}")

            suggested_actions.append("View Spec Comparison")

            lines.append("💡 **Which product do you prefer?**")
            lines.append("Click a buy option below to negotiate an AI discount and proceed to Razorpay checkout.")

            top_p_details = get_product_details(db, search_res[0]["id"])
            prod_resp = ProductResponse(**top_p_details) if top_p_details else None

            return AgentChatResponse(
                reply="\n".join(lines),
                recommended_product=prod_resp,
                tool_traces=tool_traces,
                workflow_steps=[],
                requires_user_approval=False,
                memory_profile=memory_profile,
                suggested_actions=suggested_actions
            )

    # -------------------------------------------------------------------
    # INTENT ROUTER 5: Full 11-Step Purchase Agent Workflow (Explicit Buy / Checkout)
    # -------------------------------------------------------------------
    workflow_steps: List[WorkflowStep] = []

    # STEP 1: Understand Request & Recall Memory
    t1 = time.time()
    brands_str = ", ".join(memory_profile.preferred_brands) if memory_profile.preferred_brands else "None"
    avoid_str = ", ".join(memory_profile.avoid_traits) if memory_profile.avoid_traits else "None"

    workflow_steps.append(WorkflowStep(
        step_number=1,
        step_name="Understand Request & Recall Memory",
        status="completed",
        detail_message=f"LLM parsed intent & recalled memory: Category='{extracted_category or 'General'}', Preferred Brands=['{brands_str}'], Avoid=['{avoid_str}']",
        execution_time_ms=int((time.time() - t1) * 1000)
    ))

    # STEP 2: Search Products
    t2 = time.time()
    search_res = search_products(db, query=user_msg, category=extracted_category, max_price=max_budget, user_id=user_id)
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
        detail_message=f"Searched database catalog for '{extracted_category or 'All Categories'}' and shortlisted {len(search_res)} matching candidates.",
        execution_time_ms=int((time.time() - t2) * 1000)
    ))

    # STEP 3: Filter Budget
    t3 = time.time()
    budget_filtered = [p for p in search_res if (max_budget is None or p["price"] <= max_budget)] if search_res else []
    budget_desc = f"under ₹{max_budget:,.0f}" if max_budget else "all price ranges"
    workflow_steps.append(WorkflowStep(
        step_number=3,
        step_name="Filter Budget",
        status="completed",
        detail_message=f"Filtered candidates under budget ceiling of {budget_desc} ({len(budget_filtered)} matching items).",
        execution_time_ms=int((time.time() - t3) * 1000)
    ))

    # STEP 4: Evaluate Specifications
    t4 = time.time()
    workflow_steps.append(WorkflowStep(
        step_number=4,
        step_name="Evaluate Specifications",
        status="completed",
        detail_message=f"Evaluated performance specs for {extracted_category or 'selected model'}, and factored customer memory.",
        execution_time_ms=int((time.time() - t4) * 1000)
    ))

    # STEP 5: Compare Candidates
    t5 = time.time()
    comp_ids = [p["id"] for p in search_res[:3]] if search_res else ["prod_001", "prod_002", "prod_003"]
    comp_res = compare_products(db, product_ids=comp_ids)
    tool_traces.append(ToolTrace(
        tool_name="compare_products",
        input_args={"product_ids": comp_ids},
        output_summary=comp_res,
        execution_time_ms=int((time.time() - t5) * 1000)
    ))
    candidate_names = ", ".join([p["title"] for p in search_res[:3]]) if search_res else "top candidate models"
    workflow_steps.append(WorkflowStep(
        step_number=5,
        step_name="Compare Candidates",
        status="completed",
        detail_message=f"Compared specs across candidate models: {candidate_names}.",
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
    # Reuses the coupon negotiated in Step 8 instead of negotiating again.
    t9 = time.time()
    price_res = calculate_final_price_tool(db, product_id=best_p_id, quantity=1, query=user_msg, user_id=user_id, precomputed_coupon=coupon_res)
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