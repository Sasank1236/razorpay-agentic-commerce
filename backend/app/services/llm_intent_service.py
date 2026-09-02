import json
import re
from typing import Dict, Any, Optional
from app.config import settings

def extract_intent_with_llm(query: str) -> Dict[str, Any]:
    """
    Uses OpenAI GPT-4o-mini (or intelligent regex fallback) to extract:
      - category: Laptops, Audio, Wearables, Accessories, Smartphones, Smart Home
      - max_price: float or None
      - intent_type: 'discovery' (suggest/find/show) or 'buy' (buy/checkout/order)
    """
    q_lower = query.lower()
    
    # Check if OpenAI API Key is configured and valid
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith("sk-"):
        try:
            import openai
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI Commerce Intent Extractor. "
                            "Extract structured JSON with keys:\n"
                            "- category: string (one of 'Laptops', 'Audio', 'Wearables', 'Accessories', 'Smartphones', 'Smart Home')\n"
                            "- max_price: float or null (extracted numeric price ceiling in INR)\n"
                            "- intent_type: string ('discovery' if user is asking to suggest/find/show/compare, 'buy' if user explicitly wants to buy/checkout/order/proceed)\n"
                            "- target_product_name: string or null (if specific model mentioned)\n\n"
                            "Respond strictly with valid JSON only."
                        )
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            parsed = json.loads(raw_content)
            
            # Sanitize outputs
            category = parsed.get("category", "Audio")
            if category not in ["Laptops", "Audio", "Wearables", "Accessories", "Smartphones", "Smart Home"]:
                category = "Audio"

            intent_type = parsed.get("intent_type", "discovery")
            if any(k in q_lower for k in ["buy", "checkout", "order", "purchase", "pay"]):
                intent_type = "buy"

            max_price = parsed.get("max_price")
            if max_price is not None:
                try:
                    max_price = float(max_price)
                except ValueError:
                    max_price = None

            return {
                "category": category,
                "max_price": max_price,
                "intent_type": intent_type,
                "target_product_name": parsed.get("target_product_name")
            }
        except Exception as e:
            print(f"OpenAI LLM Intent Extraction notice: using intelligent fallback parser: {e}")

    # -------------------------------------------------------------------
    # Fallback Parser (Regex & Keyword Token Matching)
    # -------------------------------------------------------------------
    category = "Audio"
    if re.search(r'\b(laptop|laptops|macbook|macbooks|notebook|notebooks|ultrabook|ultrabooks|pc|computer|computers)\b', q_lower):
        category = "Laptops"
    elif re.search(r'\b(headphone|headphones|earbud|earbuds|earphone|earphones|audio|headset|headsets|speaker|speakers|soundbar|anc)\b', q_lower):
        category = "Audio"
    elif re.search(r'\b(watch|watches|smartwatch|smartwatches|fitness|band|bands|amoled watch)\b', q_lower):
        category = "Wearables"
    elif re.search(r'\b(phone|phones|mobile|mobiles|smartphone|smartphones|iphone|iphones|galaxy)\b', q_lower):
        category = "Smartphones"
    elif re.search(r'\b(mouse|mice|keyboard|keyboards|ssd|powerbank|charger|cooling pad|hub|microphone|mic)\b', q_lower):
        category = "Accessories"
    elif re.search(r'\b(alexa|echo|nest|bulb|bulbs|plug|plugs|camera|cameras|security)\b', q_lower):
        category = "Smart Home"

    # Determine intent type
    intent_type = "discovery"
    if any(k in q_lower for k in ["buy", "checkout", "order", "purchase", "pay", "buy best", "buy the best"]):
        intent_type = "buy"

    # Extract price
    max_price = None
    num_match = re.search(r'(?:under|below|less than|<|budget of|price below|price under|rs\.?|₹)?\s*(\d+)\s*(k|000)?', q_lower)
    if num_match:
        try:
            val = float(num_match.group(1))
            unit = num_match.group(2)
            if unit == 'k' or val < 500:
                val *= 1000.0
            if val >= 1000:
                max_price = val
        except Exception:
            pass

    if max_price is None:
        max_price = 60000.0 if category == "Laptops" else 5000.0

    return {
        "category": category,
        "max_price": max_price,
        "intent_type": intent_type,
        "target_product_name": None
    }
