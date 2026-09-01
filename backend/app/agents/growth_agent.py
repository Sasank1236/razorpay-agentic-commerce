import time
from typing import List
from sqlalchemy.orm import Session
from app.tools.growth_tools import (
    analyze_commerce_metrics_tool, detect_growth_opportunities_tool,
    measure_campaign_performance_tool
)
from app.schemas.agent import MerchantGrowthResponse, MerchantGrowthInsight, ToolTrace, CampaignFeedbackLoop

def run_growth_agent(db: Session) -> MerchantGrowthResponse:
    tool_traces: List[ToolTrace] = []

    # 1. Analyze commerce metrics
    start_t1 = time.time()
    metrics_res = analyze_commerce_metrics_tool(db)
    tool_traces.append(ToolTrace(
        tool_name="analyze_commerce_metrics",
        input_args={},
        output_summary=metrics_res["metrics"],
        execution_time_ms=int((time.time() - start_t1) * 1000)
    ))

    # 2. Detect growth opportunities & AI cart recovery
    start_t2 = time.time()
    opps_res = detect_growth_opportunities_tool(db)
    tool_traces.append(ToolTrace(
        tool_name="detect_growth_opportunities",
        input_args={},
        output_summary={"detected_insights_count": len(opps_res)},
        execution_time_ms=int((time.time() - start_t2) * 1000)
    ))

    # 3. Measure closed-loop campaign feedback & outcomes
    start_t3 = time.time()
    feedback_res = measure_campaign_performance_tool(db)
    tool_traces.append(ToolTrace(
        tool_name="measure_campaign_performance",
        input_args={},
        output_summary={"measured_campaigns_count": len(feedback_res)},
        execution_time_ms=int((time.time() - start_t3) * 1000)
    ))

    insights = [MerchantGrowthInsight(
        title=opp["title"],
        metric_highlight=opp["metric_highlight"],
        description=opp["description"],
        impact_estimate=opp["impact_estimate"],
        recommended_action=opp["recommended_action"],
        analysis_tree=opp.get("analysis_tree"),
        campaign_payload=opp["campaign_payload"]
    ) for opp in opps_res]

    feedback_loops = [CampaignFeedbackLoop(**f) for f in feedback_res]

    return MerchantGrowthResponse(
        insights=insights,
        metrics_summary=metrics_res["metrics"],
        campaign_feedback_loops=feedback_loops,
        tool_traces=tool_traces
    )
