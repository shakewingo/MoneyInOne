"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import assets, health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
