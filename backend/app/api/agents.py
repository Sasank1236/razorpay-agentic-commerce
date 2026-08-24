from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.agent import AgentChatRequest, AgentChatResponse, MerchantGrowthResponse
from app.agents.shopping_agent import run_shopping_agent
from app.agents.growth_agent import run_growth_agent
from app.tools.growth_tools import simulate_campaign_action_tool

router = APIRouter(prefix="/agents", tags=["AI Agents"])

@router.post("/customer/chat", response_model=AgentChatResponse)
def customer_shopping_agent_endpoint(body: AgentChatRequest, db: Session = Depends(get_db)):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return run_shopping_agent(db, body)

@router.get("/merchant/growth", response_model=MerchantGrowthResponse)
def merchant_growth_agent_endpoint(db: Session = Depends(get_db)):
    return run_growth_agent(db)

@router.post("/merchant/campaign")
def execute_merchant_campaign(payload: Dict[str, Any], db: Session = Depends(get_db)):
    return simulate_campaign_action_tool(db, payload)
