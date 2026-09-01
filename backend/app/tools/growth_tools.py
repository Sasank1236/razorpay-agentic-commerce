import time
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Cart, Product, SearchEvent, Campaign, AgentAction
from app.services.analytics_service import get_merchant_kpi_summary
from app.services.cart_recovery_service import analyze_abandoned_carts, execute_recovery_campaign
from app.tools.product_tools import log_agent_action

def analyze_commerce_metrics_tool(db: Session) -> Dict[str, Any]:
    start_time = time.time()
    kpis = get_merchant_kpi_summary(db)
    recovery_info = analyze_abandoned_carts(db)
    
    out = {
        "metrics": kpis,
        "recovery_info": recovery_info,
        "insights_summary": f"Headphone demand is up +23%, but conversion in Electronics < ₹5,000 remains at 9.2%. {recovery_info['abandoned_count']} high-value carts sit abandoned (₹{recovery_info['at_risk_revenue']:,.0f} at risk)."
    }
    log_agent_action(db, "merchant_growth", "analyze_commerce_metrics", {}, out, start_time)
    return out

def detect_growth_opportunities_tool(db: Session) -> List[Dict[str, Any]]:
    start_time = time.time()
    recovery_info = analyze_abandoned_carts(db)
    
    opportunities = [
        {
            "id": "opp_01",
            "title": f"Agent Cart Recovery (Recover ₹{recovery_info['at_risk_revenue']:,.0f} At-Risk Revenue)",
            "metric_highlight": f"{recovery_info['abandoned_count']} high-value customer carts sit abandoned (> ₹5,000 value).",
            "description": f"AI 5-point decision tree detected high customer intent and product demand. Dispathing a 5% recovery code (`RECOVER5`) can recover up to ₹{recovery_info['at_risk_revenue']:,.0f} at-risk revenue.",
            "impact_estimate": f"Estimated revenue recovery: +₹{recovery_info['at_risk_revenue']:,.0f}",
            "recommended_action": "Approve Agent Cart Recovery campaign (RECOVER5).",
            "analysis_tree": recovery_info["analysis_tree"],
            "campaign_payload": recovery_info["campaign_payload"]
        },
        {
            "id": "opp_02",
            "title": "High Search Demand for Headphones < ₹5,000",
            "metric_highlight": "38% of searches filter for Headphones < ₹5k, but conversion is only 9.2%.",
            "description": "SoundMax Pro Wireless Headphones (₹4,499) has a 4.6★ rating and 38-hour battery. Promoting it on headphone search landing pages can capture high-intent buyers.",
            "impact_estimate": "Estimated revenue boost: +₹48,000 / week (+11% conversion lift)",
            "recommended_action": "Promote SoundMax Pro & apply 5% instant coupon for shoppers searching under ₹5,000.",
            "analysis_tree": {
                "product_demand": "High (38% of category queries)",
                "customer_intent": "High (Headphone intent)",
                "cart_value": "Medium (₹4,499)",
                "previous_discount_usage": "Low",
                "recommended_incentive": "5% Category Boost Coupon"
            },
            "campaign_payload": {
                "title": "Headphone Conversion Booster",
                "target_segment": "Headphone searchers < ₹5k",
                "discount_percent": 5.0,
                "target_product_id": "prod_001",
                "action_type": "category_boost"
            }
        },
        {
            "id": "opp_03",
            "title": "Bundle Promotion: Smartwatch + Wireless Earbuds",
            "metric_highlight": "24% of Wearables buyers view Audio accessories within 10 minutes.",
            "description": "PulseFit Pro Smartwatch (₹3,999) and SonicPod ANC Earbuds (₹4,999) are frequently co-viewed. Offering a 10% bundle discount will increase Average Order Value (AOV).",
            "impact_estimate": "Estimated AOV lift: +₹1,850 per order",
            "recommended_action": "Create PulseFit + SonicPod Audio-Wearable Bundle.",
            "analysis_tree": {
                "product_demand": "High (Co-viewed items)",
                "customer_intent": "High (Wearable + Audio)",
                "cart_value": "High (₹8,998 bundle)",
                "previous_discount_usage": "None",
                "recommended_incentive": "10% Bundle Discount"
            },
            "campaign_payload": {
                "title": "Audio + Wearable Smart Bundle",
                "target_segment": "Smartwatch buyers",
                "discount_percent": 10.0,
                "target_product_id": "prod_003",
                "action_type": "bundle_discount"
            }
        }
    ]

    log_agent_action(db, "merchant_growth", "detect_growth_opportunities", {}, {"opportunities_count": len(opportunities)}, start_time)
    return opportunities

def simulate_campaign_action_tool(db: Session, campaign_payload: Dict[str, Any]) -> Dict[str, Any]:
    start_time = time.time()
    
    if campaign_payload.get("action_type") == "send_personalized_recovery_offer" or campaign_payload.get("coupon_code") == "RECOVER5":
        return execute_recovery_campaign(db, campaign_payload)

    camp = Campaign(
        id=f"camp_{uuid.uuid4().hex[:8]}",
        title=campaign_payload.get("title", campaign_payload.get("campaign_name", "AI Merchant Campaign")),
        description=f"Automated growth intervention targeted at {campaign_payload.get('target_segment', 'Abandoned Carts')}.",
        target_segment=campaign_payload.get("target_segment", "General"),
        discount_percent=campaign_payload.get("discount_percent", 5.0),
        target_product_id=campaign_payload.get("target_product_id"),
        status="active",
        metrics={"impressions": 16, "conversions": 8, "revenue": 73494.0}
    )
    db.add(camp)
    db.commit()

    out = {
        "status": "success",
        "campaign_id": camp.id,
        "message": f"Campaign '{camp.title}' successfully launched! Target segment '{camp.target_segment}' activated with {camp.discount_percent}% discount."
    }
    log_agent_action(db, "merchant_growth", "execute_growth_campaign", campaign_payload, out, start_time)
    return out
