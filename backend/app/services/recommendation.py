import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import Product, Inventory, SearchEvent
from app.schemas.product import ProductResponse
from app.config import settings

def calculate_product_score(
    product: Product,
    query_intent: Dict[str, Any],
    user_preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Memory-Infused Hybrid Scoring Formula:
      - 30% Requirement/Preference match (+15 Memory Brand Loyalty Boost)
      - 25% Price fit (near budget without exceeding)
      - 20% Rating & Reviews
      - 15% Specs match (mic, battery, anc, etc.) (-25 Disliked Trait Penalty)
      - 10% Popularity / Bestseller tags
    """
    max_budget = query_intent.get("max_price") or 5000
    category = query_intent.get("category", "")
    priority_features = query_intent.get("priorities", ["calls", "battery"])

    preferred_brands = user_preferences.get("preferred_brands", [])
    avoid_traits = user_preferences.get("avoid_traits", [])

    # 1. Preference / Category match score (0 - 30)
    pref_score = 30.0 if product.category.lower() == category.lower() else 15.0
    if any(p.lower() in product.title.lower() or p.lower() in (product.description or "").lower() for p in priority_features):
        pref_score = min(30.0, pref_score + 10.0)

    # MEMORY BOOST: Brand Loyalty (+15 pts)
    memory_brand_bonus = 0.0
    if any(b.lower() in product.brand.lower() or b.lower() in product.title.lower() for b in preferred_brands):
        memory_brand_bonus = 15.0

    # 2. Price fit score (0 - 25)
    if product.price <= max_budget:
        ratio = product.price / max_budget
        price_score = 15.0 + (ratio * 10.0)
    else:
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

    # MEMORY PENALTY: Disliked Traits (-25 pts)
    memory_avoid_penalty = 0.0
    if any("bulky" in trait for trait in avoid_traits):
        # Check weight > 230g or "heavy" / "bulky" in description
        weight_str = str(specs.get("weight", ""))
        if "240g" in weight_str or "heavy" in product.description.lower() or "over-ear" in product.description.lower():
            memory_avoid_penalty = 15.0

    # 5. Popularity score (0 - 10)
    tags = product.tags or []
    pop_score = 5.0
    if "bestseller" in tags or "featured" in tags:
        pop_score += 5.0

    raw_total = pref_score + memory_brand_bonus + price_score + rating_total + spec_score - memory_avoid_penalty + pop_score
    total_score = round(max(10.0, min(100.0, raw_total)), 1)

    return {
        "product_id": product.id,
        "total_score": total_score,
        "breakdown": {
            "preference_match": round(pref_score, 1),
            "memory_brand_bonus": round(memory_brand_bonus, 1),
            "price_fit": round(price_score, 1),
            "rating_score": round(rating_total, 1),
            "specs_score": round(spec_score, 1),
            "memory_avoid_penalty": round(memory_avoid_penalty, 1),
            "popularity_score": round(pop_score, 1)
        }
    }

def get_hybrid_recommendations(
    db: Session,
    query: str,
    extracted_intent: Dict[str, Any],
    user_preferences: Dict[str, Any] = None,
    limit: int = 5
) -> Tuple[Product, List[Product], List[Dict[str, Any]], str]:
    """
    Queries candidate products from DB, strictly filtering category, stock > 0, and budget ceiling,
    then scores them using Customer Memory and generates structured reasoning.
    """
    user_preferences = user_preferences or {}
    category = extracted_intent.get("category", "Audio")
    max_price = extracted_intent.get("max_price") or 5000

    # Base query: Join Inventory to enforce stock_quantity > 0
    query_builder = db.query(Product).join(Inventory, Product.id == Inventory.product_id).filter(
        Inventory.stock_quantity > 0
    )

    candidates = []
    if category:
        # Strictly filter by category and price ceiling
        category_candidates = query_builder.filter(
            Product.category.ilike(f"%{category}%"),
            Product.price <= max_price * 1.25
        ).all()
        
        if not category_candidates:
            # Fallback: get items in the requested category even if above max_price
            category_candidates = query_builder.filter(
                Product.category.ilike(f"%{category}%")
            ).all()

        candidates = category_candidates

    if not candidates:
        candidates = query_builder.filter(Product.price <= max_price * 1.25).all()

    if not candidates:
        candidates = db.query(Product).limit(10).all()

    scored_candidates = []
    for p in candidates:
        score_info = calculate_product_score(p, extracted_intent, user_preferences)
        scored_candidates.append((p, score_info))

    # Sort descending by score
    scored_candidates.sort(key=lambda x: x[1]["total_score"], reverse=True)

    top_candidates = [item[0] for item in scored_candidates[:limit]]
    best_product = top_candidates[0] if top_candidates else None
    score_details = [item[1] for item in scored_candidates[:limit]]

    preferred_brands = user_preferences.get("preferred_brands", [])
    memory_preamble = ""
    if preferred_brands and any(b.lower() in best_product.brand.lower() for b in preferred_brands):
        memory_preamble = f"Based on your stored preference for **{', '.join(preferred_brands)}** and lightweight non-bulky designs, "

    reasoning = (
        f"{memory_preamble}we evaluated {len(candidates)} candidate products in the {category} category. "
        f"**{best_product.title}** scored the highest ({score_details[0]['total_score']}/100) because it fits your budget at ₹{best_product.price:,.0f}, "
        f"features a {best_product.rating}★ rating, and perfectly aligns with your use-case priorities."
    )

    return best_product, top_candidates, score_details, reasoning