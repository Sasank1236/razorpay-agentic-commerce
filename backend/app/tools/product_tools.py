import time
import uuid
import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Product, Inventory, User, AgentAction, SearchEvent
from app.services.recommendation import get_hybrid_recommendations
from app.services.memory_service import get_customer_memory_profile
from app.services.llm_intent_service import extract_intent_with_llm

def log_agent_action(db: Session, agent_type: str, action_name: str, input_params: Any, output_summary: Any, start_time: float):
    exec_time = int((time.time() - start_time) * 1000)
    action = AgentAction(
        id=f"act_{uuid.uuid4().hex[:8]}",
        agent_type=agent_type,
        action_name=action_name,
        input_params=input_params if isinstance(input_params, dict) else {"raw": str(input_params)},
        output_summary=output_summary if isinstance(output_summary, (dict, list)) else {"summary": str(output_summary)},
        execution_time_ms=exec_time
    )
    db.add(action)
    db.commit()

def extract_intent_from_query(query: str, memory_ceiling: float = 5000.0) -> Dict[str, Any]:
    llm_intent = extract_intent_with_llm(query)
    category = llm_intent["category"]
    max_price = llm_intent["max_price"]

    return {
        "category": category,
        "max_price": max_price,
        "intent_type": llm_intent.get("intent_type", "discovery"),
        "target_product_name": llm_intent.get("target_product_name"),
        "priorities": ["calls", "battery", "performance", "display", "mic"]
    }

def search_products(db: Session, query: str, category: Optional[str] = None, max_price: Optional[float] = None, user_id: str = "user_customer_01") -> List[Dict[str, Any]]:
    start_time = time.time()
    q = db.query(Product)
    
    if category:
        q = q.filter(Product.category.ilike(f"%{category}%"))
    if max_price:
        q = q.filter(Product.price <= max_price * 1.25)

    stop_words = {"suggest", "some", "below", "under", "price", "find", "show", "me", "the", "best", "good", "for", "a", "an", "is", "of", "in", "and"}
    keywords = [kw for kw in re.findall(r'\b\w+\b', query.lower()) if kw not in stop_words and len(kw) > 1]
    
    results = q.all()
    filtered = []
    
    for p in results:
        text = f"{p.title} {p.description} {p.brand} {p.category}".lower()
        if any(kw in text for kw in keywords) or not keywords:
            filtered.append(p)

    candidates = filtered if filtered else results
    out = [{
        "id": p.id,
        "title": p.title,
        "category": p.category,
        "price": p.price,
        "rating": p.rating,
        "brand": p.brand,
        "description": p.description,
        "specs": p.specs,
        "image_url": p.image_url
    } for p in candidates[:8]]

    search_evt = SearchEvent(
        id=f"se_{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        query=query,
        extracted_intent={"category": category, "max_price": max_price},
        results_count=len(out)
    )
    db.add(search_evt)

    log_agent_action(db, "customer", "search_products", {"query": query, "category": category, "max_price": max_price}, {"found_count": len(out), "products": out}, start_time)
    return out

def get_product_details(db: Session, product_id: str) -> Optional[Dict[str, Any]]:
    start_time = time.time()
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        return None
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    out = {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "category": p.category,
        "brand": p.brand,
        "price": p.price,
        "original_price": p.original_price,
        "rating": p.rating,
        "specs": p.specs,
        "tags": p.tags,
        "image_url": p.image_url,
        "stock_quantity": inv.stock_quantity if inv else 50
    }
    log_agent_action(db, "customer", "get_product_details", {"product_id": product_id}, {"title": p.title, "price": p.price}, start_time)
    return out

def compare_products(db: Session, product_ids: List[str]) -> Dict[str, Any]:
    start_time = time.time()
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    
    comparison_matrix = {}
    for p in products:
        comparison_matrix[p.title] = {
            "id": p.id,
            "price": f"₹{p.price:,.0f}",
            "rating": f"{p.rating}★",
            "battery": (p.specs or {}).get("battery", (p.specs or {}).get("cpu", "Standard")),
            "mic": (p.specs or {}).get("mic", (p.specs or {}).get("ram", "Good")),
            "anc": "Yes" if (p.specs or {}).get("anc") else "Standard",
            "brand": p.brand
        }

    best_p = max(products, key=lambda x: x.rating) if products else None
    out = {
        "comparison_table": comparison_matrix,
        "best_match_id": best_p.id if best_p else "",
        "best_match_title": best_p.title if best_p else ""
    }
    log_agent_action(db, "customer", "compare_products", {"product_ids": product_ids}, out, start_time)
    return out

def get_recommendations_tool(db: Session, query: str, user_id: str = "user_customer_01") -> Dict[str, Any]:
    start_time = time.time()
    
    intent = extract_intent_from_query(query)
    user_preferences = get_customer_memory_profile(db, user_id)
    
    best_p, top_candidates, scores, reasoning = get_hybrid_recommendations(db, query, intent, user_preferences, limit=4)
    
    out = {
        "recommended_product": {
            "id": best_p.id,
            "title": best_p.title,
            "price": best_p.price,
            "rating": best_p.rating,
            "specs": best_p.specs,
            "image_url": best_p.image_url,
            "score": scores[0]["total_score"] if scores else 94.0
        },
        "shortlisted": [{
            "id": p.id,
            "title": p.title,
            "price": p.price,
            "rating": p.rating,
            "score": scores[idx]["total_score"] if idx < len(scores) else 80.0
        } for idx, p in enumerate(top_candidates)],
        "reasoning": reasoning
    }

    log_agent_action(db, "customer", "get_recommendations", {"query": query, "user_id": user_id}, {"recommended_title": best_p.title, "score": out["recommended_product"]["score"]}, start_time)
    return out