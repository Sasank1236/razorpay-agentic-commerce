from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas.product import ProductResponse

class ChatMessage(BaseModel):
    role: str # user, assistant, system, tool
    content: str

class AgentChatRequest(BaseModel):
    user_id: str = "user_customer_01"
    message: str
    conversation_history: Optional[List[ChatMessage]] = []

class ToolTrace(BaseModel):
    tool_name: str
    input_args: Dict[str, Any]
    output_summary: Any
    execution_time_ms: int

class AgentChatResponse(BaseModel):
    reply: str
    recommended_product: Optional[ProductResponse] = None
    comparison_table: Optional[Dict[str, Any]] = None
    tool_traces: List[ToolTrace] = []
    requires_user_approval: bool = False
    staged_cart_id: Optional[str] = None
    suggested_actions: Optional[List[str]] = []

class MerchantGrowthInsight(BaseModel):
    title: str
    metric_highlight: str
    description: str
    impact_estimate: str
    recommended_action: str
    campaign_payload: Dict[str, Any]

class MerchantGrowthResponse(BaseModel):
    insights: List[MerchantGrowthInsight]
    metrics_summary: Dict[str, Any]
    tool_traces: List[ToolTrace] = []
