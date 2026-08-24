import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="customer") # customer, merchant
    preferences = Column(JSON, nullable=True) # e.g. {"preferred_categories": ["Audio"], "avg_order_val": 3500}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
