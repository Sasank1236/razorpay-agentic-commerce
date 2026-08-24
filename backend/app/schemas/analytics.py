from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import datetime

class KPISummary(BaseModel):
    total_revenue: float
    total_orders: int
    conversion_rate: float
    avg_order_value: float
    ai_assisted_sales: float
    abandoned_carts_count: int
    abandoned_revenue_at_risk: float

class RevenueTrendItem(BaseModel):
    date: str
    revenue: float
    orders: int
    ai_revenue: float

class AgentActionLogResponse(BaseModel):
    id: str
    agent_type: str
    action_name: str
    input_params: Optional[Dict[str, Any]] = None
    output_summary: Optional[Dict[str, Any]] = None
    execution_time_ms: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True
