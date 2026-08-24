from fastapi import APIRouter
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.payments import router as payments_router
from app.api.agents import router as agents_router
from app.api.analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(products_router)
api_router.include_router(orders_router)
api_router.include_router(payments_router)
api_router.include_router(agents_router)
api_router.include_router(analytics_router)
