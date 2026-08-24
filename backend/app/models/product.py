import datetime
from sqlalchemy import Column, String, Float, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, index=True, nullable=False)
    brand = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    rating = Column(Float, default=4.0)
    review_count = Column(Integer, default=0)
    specs = Column(JSON, nullable=True) # e.g. {"battery": "38h", "mic": "excellent", "noise_cancellation": True}
    tags = Column(JSON, nullable=True) # e.g. ["bestseller", "calls", "long-battery"]
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"), unique=True, nullable=False)
    stock_quantity = Column(Integer, default=50)
    reserved_quantity = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    product = relationship("Product", back_populates="inventory")
