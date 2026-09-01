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

class WorkflowStep(BaseModel):
    step_number: int
    step_name: str
    status: str # completed, in_progress, pending
    detail_message: str
    execution_time_ms: int = 0

class AINegotiatedOffer(BaseModel):
    coupon_code: str
    discount_percent: float
    original_price: float
    offer_price: float
    savings: float
    reasoning: str
    valid_seconds: int = 600

class CustomerMemoryProfile(BaseModel):
    preferred_brands: List[str] = []
    avoid_traits: List[str] = []
    primary_use_cases: List[str] = []
    budget_ceiling: float = 5000.0
    memory_summary: str = ""

class AgentChatResponse(BaseModel):
    reply: str
    recommended_product: Optional[ProductResponse] = None
    comparison_table: Optional[Dict[str, Any]] = None
    tool_traces: List[ToolTrace] = []
    workflow_steps: List[WorkflowStep] = []
    requires_user_approval: bool = False
    staged_cart_id: Optional[str] = None
    staged_order_id: Optional[str] = None
    coupon_applied: Optional[str] = None
    original_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    final_amount: Optional[float] = None
    negotiated_offer: Optional[AINegotiatedOffer] = None
    memory_profile: Optional[CustomerMemoryProfile] = None
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
