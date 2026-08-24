import datetime
from sqlalchemy import Column, String, Float, Integer, Text, JSON, DateTime, ForeignKey, Boolean
from app.db.database import Base

class SearchEvent(Base):
    __tablename__ = "search_events"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    query = Column(Text, nullable=False)
    extracted_intent = Column(JSON, nullable=True) # e.g. {"category": "Audio", "max_price": 5000}
    results_count = Column(Integer, default=0)
    converted_to_cart = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ProductView(Base):
    __tablename__ = "product_views"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    duration_seconds = Column(Integer, default=5)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    query = Column(Text, nullable=True)
    recommended_product_id = Column(String, ForeignKey("products.id"), nullable=False)
    shortlisted_ids = Column(JSON, nullable=True)
    score_breakdown = Column(JSON, nullable=True)
    reasoning = Column(Text, nullable=False)
    accepted = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(String, primary_key=True, index=True)
    agent_type = Column(String, nullable=False) # customer, merchant_growth
    action_name = Column(String, nullable=False) # e.g. search_products, compare_products, recommend, razorpay_order
    input_params = Column(JSON, nullable=True)
    output_summary = Column(JSON, nullable=True)
    execution_time_ms = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_segment = Column(String, nullable=False) # e.g. "Headphone searchers", "Abandoned Cart > 5000"
    discount_percent = Column(Float, default=0.0)
    target_product_id = Column(String, nullable=True)
    status = Column(String, default="active") # draft, active, completed
    metrics = Column(JSON, nullable=True) # e.g. {"impressions": 120, "conversions": 18, "revenue": 81000}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
