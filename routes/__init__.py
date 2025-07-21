# routes/__init__.py

from fastapi import APIRouter
from routes.product import router as product_router
from routes.order import router as order_router
from routes.health import router as health_router

# Main API router that includes all route modules
api_router = APIRouter()

# Include route modules
api_router.include_router(product_router)
api_router.include_router(order_router)
api_router.include_router(health_router)

# Export the combined router
__all__ = ["api_router"]
