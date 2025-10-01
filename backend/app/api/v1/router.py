"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import assets, credits, health, portfolio, metadata

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    assets.router,
    prefix="/assets",
    tags=["Assets"]
)

api_router.include_router(
    credits.router,
    prefix="/credits",
    tags=["Credits"]
)

api_router.include_router(
    portfolio.router,
    prefix="/portfolio",
    tags=["Portfolio"]
)

api_router.include_router(
    metadata.router,
    prefix="/metadata",
    tags=["Metadata"]
)