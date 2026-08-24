from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Product, Inventory
from app.schemas.product import ProductResponse, ProductCompareRequest, ProductCompareResponse
from app.tools.product_tools import compare_products, search_products

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = None,
    query: Optional[str] = None,
    max_price: Optional[float] = None,
    limit: int = 150,
    db: Session = Depends(get_db)
):
    q = db.query(Product)
    if category and category != "All":
        q = q.filter(Product.category.ilike(f"%{category}%"))
    if max_price:
        q = q.filter(Product.price <= max_price)
    if query:
        q = q.filter(
            Product.title.ilike(f"%{query}%") | Product.description.ilike(f"%{query}%") | Product.brand.ilike(f"%{query}%")
        )
    
    products = q.limit(limit).all()
    out = []
    for p in products:
        inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
        out.append(ProductResponse(
            id=p.id,
            title=p.title,
            description=p.description,
            category=p.category,
            brand=p.brand,
            price=p.price,
            original_price=p.original_price,
            rating=p.rating,
            review_count=p.review_count,
            specs=p.specs,
            tags=p.tags,
            image_url=p.image_url,
            stock_quantity=inv.stock_quantity if inv else 50
        ))
    return out

@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
    return ProductResponse(
        id=p.id,
        title=p.title,
        description=p.description,
        category=p.category,
        brand=p.brand,
        price=p.price,
        original_price=p.original_price,
        rating=p.rating,
        review_count=p.review_count,
        specs=p.specs,
        tags=p.tags,
        image_url=p.image_url,
        stock_quantity=inv.stock_quantity if inv else 50
    )

@router.post("/compare", response_model=ProductCompareResponse)
def compare_products_endpoint(body: ProductCompareRequest, db: Session = Depends(get_db)):
    if not body.product_ids:
        raise HTTPException(status_code=400, detail="Must provide product_ids")
    res = compare_products(db, body.product_ids)
    products = db.query(Product).filter(Product.id.in_(body.product_ids)).all()
    
    p_responses = []
    for p in products:
        inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
        p_responses.append(ProductResponse(
            id=p.id,
            title=p.title,
            description=p.description,
            category=p.category,
            brand=p.brand,
            price=p.price,
            original_price=p.original_price,
            rating=p.rating,
            review_count=p.review_count,
            specs=p.specs,
            tags=p.tags,
            image_url=p.image_url,
            stock_quantity=inv.stock_quantity if inv else 50
        ))

    return ProductCompareResponse(
        products=p_responses,
        comparison_table=res["comparison_table"],
        best_match_id=res["best_match_id"],
        reasoning=f"Product '{res['best_match_title']}' scored highest overall due to rating and feature balance."
    )
