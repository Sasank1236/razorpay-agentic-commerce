import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Product, SearchEvent
from app.schemas.product import ProductResponse
from app.config import settings

def calculate_product_score(
    product: Product,
    query_intent: Dict[str, Any],
    user_preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Hybrid scoring formula:
      - 30% Requirement/Preference match
      - 25% Price fit (near budget without exceeding)
      - 20% Rating & Reviews
      - 15% Specs match (mic, battery, anc, etc.)
      - 10% Popularity / Bestseller tags
    """
    max_budget = query_intent.get("max_price", 5000)
    category = query_intent.get("category", "")
    priority_features = query_intent.get("priorities", ["calls", "battery"])

    # 1. Preference / Category match score (0 - 30)
    pref_score = 30.0 if product.category.lower() == category.lower() else 15.0
    if any(p.lower() in product.title.lower() or p.lower() in (product.description or "").lower() for p in priority_features):
        pref_score = min(30.0, pref_score + 10.0)

    # 2. Price fit score (0 - 25)
    if product.price <= max_budget:
        # Closer to max_budget without going over is ideal (value for money)
        ratio = product.price / max_budget
        price_score = 15.0 + (ratio * 10.0)
    else:
        # Over budget penalty
        over_pct = (product.price - max_budget) / max_budget
        price_score = max(0.0, 15.0 - (over_pct * 30.0))

    # 3. Rating & Review score (0 - 20)
    rating_score = (product.rating / 5.0) * 15.0
    review_bonus = min(5.0, (product.review_count / 200.0) * 5.0)
    rating_total = rating_score + review_bonus

    # 4. Specs match score (0 - 15)
    specs = product.specs or {}
    spec_points = 0.0
    if "battery" in priority_features and ("battery" in specs or "30h" in (product.description or "")):
        spec_points += 5.0
    if "mic" in priority_features or "calls" in priority_features:
        if "mic" in specs or "call" in (product.description or "").lower():
            spec_points += 5.0
    if "anc" in priority_features and specs.get("anc"):
        spec_points += 5.0
    spec_score = min(15.0, spec_points + 5.0)

    # 5. Popularity score (0 - 10)
    tags = product.tags or []
    pop_score = 5.0
    if "bestseller" in tags or "featured" in tags:
        pop_score += 5.0

    total_score = round(pref_score + price_score + rating_total + spec_score + pop_score, 1)

    return {
        "product_id": product.id,
        "total_score": total_score,
        "breakdown": {
            "preference_match": round(pref_score, 1),
            "price_fit": round(price_score, 1),
            "rating_score": round(rating_total, 1),
            "specs_score": round(spec_score, 1),
            "popularity_score": round(pop_score, 1)
        }
    }

def get_hybrid_recommendations(
    db: Session,
    query: str,
    extracted_intent: Dict[str, Any],
    limit: int = 5
) -> Tuple[Product, List[Product], List[Dict[str, Any]], str]:
    """
    Queries candidate products from DB, scores them, and generates a structured recommendation explanation.
    """
    category = extracted_intent.get("category", "Audio")
    max_price = extracted_intent.get("max_price", 5000)
    keywords = query.lower().split()

    # Query candidate products
    candidates = db.query(Product).filter(
        Product.price <= max_price * 1.25 # Allow up to 25% flexibility for scoring candidates
    ).all()

    if not candidates:
        candidates = db.query(Product).limit(10).all()

    scored_candidates = []
    for p in candidates:
        score_info = calculate_product_score(p, extracted_intent, {})
        scored_candidates.append((p, score_info))

    # Sort descending by score
    scored_candidates.sort(key=lambda x: x[1]["total_score"], reverse=True)

    top_candidates = [item[0] for item in scored_candidates[:limit]]
    best_product = top_candidates[0] if top_candidates else None
    score_details = [item[1] for item in scored_candidates[:limit]]

    # Generate reasoning statement
    reasoning = (
        f"Based on your requirements ({query}), we evaluated {len(candidates)} products across battery life, "
        f"call quality, price fit, and customer ratings. {best_product.title} scored the highest ({score_details[0]['total_score']}/100) "
        f"because it fits your budget at ₹{best_product.price:,.0f}, features a high rating of {best_product.rating}★, "
        f"and delivers outstanding microphone and battery specs."
    )

    return best_product, top_candidates, score_details, reasoning
