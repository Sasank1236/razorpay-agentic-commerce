from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ProductBase(BaseModel):
    title: str
    description: str
    category: str
    brand: str
    price: float
    original_price: Optional[float] = None
    rating: float = 4.0
    review_count: int = 0
    specs: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str
    stock_quantity: Optional[int] = 50

    class Config:
        from_attributes = True

class ProductCompareRequest(BaseModel):
    product_ids: List[str]

class ProductCompareResponse(BaseModel):
    products: List[ProductResponse]
    comparison_table: Dict[str, Any]
    best_match_id: str
    reasoning: str
