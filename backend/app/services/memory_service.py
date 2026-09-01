import time
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import User, AgentAction

KNOWN_BRANDS = ["Sony", "SoundMax", "JBL", "Bose", "Sennheiser", "Apple", "Boat", "Realme", "Logitech", "Keychron", "Anker"]
DISLIKED_KEYWORDS = {
    "bulky": "bulky (>220g)",
    "heavy": "heavy weight",
    "in-ear": "in-ear earbuds",
    "cheap": "cheap quality",
    "wired": "wired cables"
}
USE_CASE_KEYWORDS = {
    "travel": "travel & commuting",
    "calls": "calls & meetings",
    "online class": "online classes & learning",
    "class": "online classes & learning",
    "gaming": "gaming & low latency",
    "gym": "sports & gym",
    "running": "running & outdoor"
}

def get_customer_memory_profile(db: Session, user_id: str = "user_customer_01") -> Dict[str, Any]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.preferences:
        default_pref = {
            "preferred_brands": ["Sony"],
            "avoid_traits": ["bulky (>220g)"],
            "primary_use_cases": ["calls & meetings", "online classes & learning"],
            "budget_ceiling": 5000.0,
            "memory_summary": "Prefers Sony, avoids bulky designs (>220g), prioritizes microphone for calls & learning."
        }
        if user:
            user.preferences = default_pref
            db.commit()
        return default_pref

    return user.preferences

def extract_and_update_customer_memory(db: Session, user_id: str = "user_customer_01", message: str = "") -> Dict[str, Any]:
    """
    Extracts brand preferences, traits to avoid, and use cases from customer chat prompts,
    then updates the User preferences JSON in the database.
    """
    start_time = time.time()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return get_customer_memory_profile(db, user_id)

    msg_lower = message.lower()
    current_pref = user.preferences or {
        "preferred_brands": [],
        "avoid_traits": [],
        "primary_use_cases": [],
        "budget_ceiling": 5000.0,
        "memory_summary": ""
    }

    preferred_brands = list(current_pref.get("preferred_brands", []))
    avoid_traits = list(current_pref.get("avoid_traits", []))
    primary_use_cases = list(current_pref.get("primary_use_cases", []))

    # 1. Extract Preferred Brands
    for brand in KNOWN_BRANDS:
        if brand.lower() in msg_lower and brand not in preferred_brands:
            if any(pref in msg_lower for pref in ["prefer", "like", "love", "only", "want"]):
                preferred_brands.append(brand)

    # Fallback: Default to Sony if user mentions "prefer Sony" or "Sony products"
    if "sony" in msg_lower and "Sony" not in preferred_brands:
        preferred_brands.append("Sony")

    # 2. Extract Avoided Traits
    if "bulky" in msg_lower or "don't like bulky" in msg_lower or "not bulky" in msg_lower or "heavy" in msg_lower:
        if "bulky (>220g)" not in avoid_traits:
            avoid_traits.append("bulky (>220g)")

    for kw, trait in DISLIKED_KEYWORDS.items():
        if kw in msg_lower and any(neg in msg_lower for neg in ["don't like", "no", "avoid", "hate", "not", "without"]):
            if trait not in avoid_traits:
                avoid_traits.append(trait)

    # 3. Extract Primary Use Cases
    for kw, use_case in USE_CASE_KEYWORDS.items():
        if kw in msg_lower and use_case not in primary_use_cases:
            primary_use_cases.append(use_case)

    # 4. Construct Memory Summary
    summary_parts = []
    if preferred_brands:
        summary_parts.append(f"Prefers {', '.join(preferred_brands)}")
    if avoid_traits:
        summary_parts.append(f"Avoids {', '.join(avoid_traits)}")
    if primary_use_cases:
        summary_parts.append(f"Prioritizes {', '.join(primary_use_cases[:2])}")

    memory_summary = ". ".join(summary_parts) + "." if summary_parts else "Default preferences active."

    updated_pref = {
        "preferred_brands": preferred_brands if preferred_brands else ["Sony"],
        "avoid_traits": avoid_traits if avoid_traits else ["bulky (>220g)"],
        "primary_use_cases": primary_use_cases if primary_use_cases else ["travel & commuting", "calls & meetings"],
        "budget_ceiling": current_pref.get("budget_ceiling", 5000.0),
        "memory_summary": memory_summary
    }

    user.preferences = updated_pref
    db.commit()

    log_agent_action(
        db,
        agent_type="customer_memory",
        action_name="update_customer_profile",
        input_params={"message": message, "user_id": user_id},
        output_summary=updated_pref,
        start_time=start_time
    )

    return updated_pref
