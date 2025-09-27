"""Health check endpoints."""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session

router = APIRouter()


@router.get("/")
async def basic_health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "service": "MoneyInOne API",
    }


@router.get("/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Detailed health check including database connectivity."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "service": "MoneyInOne API",
        "checks": {},
    }

    # Database connectivity check
    try:
        result = await db.execute("SELECT 1 as health_check")
        row = result.fetchone()
        if row and row[0] == 1:
            health_status["checks"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful",
            }
        else:
            health_status["checks"]["database"] = {
                "status": "unhealthy",
                "message": "Database query returned unexpected result",
            }
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }
        health_status["status"] = "unhealthy"

    # Configuration check
    health_status["checks"]["configuration"] = {
        "status": "healthy",
        "debug_mode": settings.debug,
        "api_version": settings.api_version,
    }

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
