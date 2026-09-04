import json
import re
from typing import Dict, Any, Optional
from app.config import settings

def extract_intent_with_gemini(query: str) -> Optional[Dict[str, Any]]:
    """Calls Google Gemini API for structured intent extraction."""
    if not settings.GEMINI_API_KEY:
        return None
    try:
        import httpx
        model_name = settings.GEMINI_MODEL or "gemini-3.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
        
        prompt = (
            "You are an AI Commerce Intent Extractor for an e-commerce platform.\n"
            "Extract structured JSON with keys:\n"
            "- category: string or null (Must be one of 'Laptops', 'Audio', 'Wearables', 'Accessories', 'Smartphones', 'Smart Home', or null if query spans multiple or general categories)\n"
            "- max_price: float or null (extracted numeric budget/price ceiling in INR. DO NOT parse ordinal generation terms like '2nd gen', '3rd gen', or RAM sizes like '16GB' as price!)\n"
            "- intent_type: string ('discovery' if user is asking to suggest/find/show/compare, 'buy' if user explicitly wants to buy/checkout/order/proceed)\n"
            "- target_product_name: string or null (if specific model like 'google nest mini' mentioned)\n\n"
            f"User Query: {query}\n"
            "Respond strictly with valid JSON only."
        )
        
        body = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.0
            }
        }
        
        resp = httpx.post(url, json=body, timeout=12.0)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                    raw_text = re.sub(r"\s*```$", "", raw_text)
                parsed = json.loads(raw_text)
                
                category = parsed.get("category")
                if category not in ["Laptops", "Audio", "Wearables", "Accessories", "Smartphones", "Smart Home"]:
                    category = None

                intent_type = parsed.get("intent_type", "discovery")
                q_lower = query.lower()
                if any(k in q_lower for k in ["buy", "checkout", "order", "purchase", "pay"]):
                    intent_type = "buy"

                max_price = parsed.get("max_price")
                if max_price is not None:
                    try:
                        max_price = float(max_price)
                    except (ValueError, TypeError):
                        max_price = None

                return {
                    "category": category,
                    "max_price": max_price,
                    "intent_type": intent_type,
                    "target_product_name": parsed.get("target_product_name")
                }
    except Exception as e:
        print(f"Google Gemini LLM Intent Extraction notice: {e}")
    return None

def extract_intent_with_llm(query: str) -> Dict[str, Any]:
    """
    Uses Google Gemini (or OpenAI / intelligent regex fallback) to extract:
      - category: Laptops, Audio, Wearables, Accessories, Smartphones, Smart Home, or None
      - max_price: float or None
      - intent_type: 'discovery' (suggest/find/show) or 'buy' (buy/checkout/order)
    """
    q_lower = query.lower()
    
    # 1. Try Google Gemini API
    gemini_result = extract_intent_with_gemini(query)
    if gemini_result:
        return gemini_result

    # 2. Try OpenAI API if configured
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
                            "You are an AI Commerce Intent Extractor for an e-commerce platform.\n"
                            "Extract structured JSON with keys:\n"
                            "- category: string or null (Must be one of 'Laptops', 'Audio', 'Wearables', 'Accessories', 'Smartphones', 'Smart Home', or null if query spans multiple or general categories)\n"
                            "- max_price: float or null (extracted numeric budget/price ceiling in INR. DO NOT parse ordinal generation terms like '2nd gen', '3rd gen', or RAM sizes like '16GB' as price!)\n"
                            "- intent_type: string ('discovery' if user is asking to suggest/find/show/compare, 'buy' if user explicitly wants to buy/checkout/order/proceed)\n"
                            "- target_product_name: string or null (if specific model like 'google nest mini' mentioned)\n\n"
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
            
            category = parsed.get("category")
            if category not in ["Laptops", "Audio", "Wearables", "Accessories", "Smartphones", "Smart Home"]:
                category = None

            intent_type = parsed.get("intent_type", "discovery")
            if any(k in q_lower for k in ["buy", "checkout", "order", "purchase", "pay"]):
                intent_type = "buy"

            max_price = parsed.get("max_price")
            if max_price is not None:
                try:
                    max_price = float(max_price)
                except (ValueError, TypeError):
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
    category = None
    if re.search(r'\b(smart home|smart-home|smarthome|home automation|alexa|echo|nest|bulb|bulbs|plug|plugs|camera|cameras|security|doorbell|smart strip|hue|wipro|tp-link)\b', q_lower):
        category = "Smart Home"
    elif re.search(r'\b(laptop|laptops|macbook|macbooks|notebook|notebooks|ultrabook|ultrabooks|pc|computer|computers)\b', q_lower):
        category = "Laptops"
    elif re.search(r'\b(watch|watches|smartwatch|smartwatches|fitness|band|bands|amoled watch|fitbit|garmin|amazfit|apple watch|galaxy watch)\b', q_lower):
        category = "Wearables"
    elif re.search(r'\b(phone|phones|mobile|mobiles|smartphone|smartphones|iphone|iphones|galaxy)\b', q_lower):
        category = "Smartphones"
    elif re.search(r'\b(mouse|mice|keyboard|keyboards|ssd|powerbank|charger|cooling pad|hub|microphone|mic)\b', q_lower):
        category = "Accessories"
    elif re.search(r'\b(headphone|headphones|earbud|earbuds|earphone|earphones|audio|headset|headsets|speaker|speakers|soundbar|anc|tws|airpods)\b', q_lower):
        category = "Audio"

    # Determine intent type
    intent_type = "discovery"
    if any(k in q_lower for k in ["buy", "checkout", "order", "purchase", "pay", "buy best", "buy the best"]):
        intent_type = "buy"

    # Extract price (strip ordinals like 2nd, 3rd, 1st, 16gb, 512gb)
    clean_q = re.sub(r'\b\d+(st|nd|rd|th|in|inch|gb|tb)\b', '', q_lower)
    max_price = None

    num_match = re.search(r'(?:under|below|less than|<|budget of|price below|price under|rs\.?|₹)\s*(\d+)\s*(k|000)?\b', clean_q)
    if not num_match:
        # Match standalone price numbers like 5000, 20000, 60000 or numbers followed by k (e.g. 5k, 20k, 60k)
        num_match = re.search(r'\b(\d{4,6})\b|\b(\d+)\s*k\b', clean_q)

    if num_match:
        try:
            val_str = num_match.group(1) or num_match.group(2)
            if val_str:
                val = float(val_str)
                matched_text = clean_q[num_match.start():num_match.end()+2]
                if 'k' in matched_text or val < 500:
                    val *= 1000.0
                if val >= 1000:
                    max_price = val
        except Exception:
            pass

    return {
        "category": category,
        "max_price": max_price,
        "intent_type": intent_type,
        "target_product_name": None
    }
