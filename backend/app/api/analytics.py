from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.analytics_service import get_merchant_kpi_summary, get_revenue_trends
from app.schemas.analytics import KPISummary, RevenueTrendItem, AgentActionLogResponse
from app.models import AgentAction

router = APIRouter(prefix="/analytics", tags=["Analytics & Agent Log"])

@router.get("/summary", response_model=KPISummary)
def get_kpi_summary(db: Session = Depends(get_db)):
    kpis = get_merchant_kpi_summary(db)
    return KPISummary(**kpis)

@router.get("/trends", response_model=List[RevenueTrendItem])
def get_revenue_trend_data(db: Session = Depends(get_db)):
    trends = get_revenue_trends(db)
    return [RevenueTrendItem(**t) for t in trends]

@router.get("/timeline", response_model=List[AgentActionLogResponse])
def get_agent_action_timeline(limit: int = 50, db: Session = Depends(get_db)):
    actions = db.query(AgentAction).order_by(AgentAction.timestamp.desc()).limit(limit).all()
    return actions
