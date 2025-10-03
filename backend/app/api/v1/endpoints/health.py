"""Health check endpoints."""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db_session
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "MoneyInOne API",
        "app": settings.app_name,
        "version": settings.app_version
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db_session)):
    """Detailed health check including database connectivity."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "MoneyInOne API",
        "checks": {}
    }
    
    # Database connectivity check
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()  # Remove await - fetchone() is not async
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
    
    # If any check fails, return 503
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/health/database")
async def database_health(db: AsyncSession = Depends(get_db_session)):
    """Database health check with storage and connection info."""
    health_info = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {}
    }
    
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        
        # Get database size (PostgreSQL specific)
        if "postgresql" in settings.database_url:
            result = await db.execute(text("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as size,
                    pg_database_size(current_database()) as size_bytes
            """))
            row = result.fetchone()
            if row:
                health_info["database"]["size"] = row[0]
                health_info["database"]["size_bytes"] = row[1]
        
        # Get connection count
        if "postgresql" in settings.database_url:
            result = await db.execute(text("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database()
            """))
            row = result.fetchone()
            if row:
                health_info["database"]["active_connections"] = row[0]
        
        # Get table counts
        result = await db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM assets) as asset_count,
                (SELECT COUNT(*) FROM credits) as credit_count,
                (SELECT COUNT(*) FROM users) as user_count
        """))
        row = result.fetchone()
        if row:
            health_info["database"]["statistics"] = {
                "assets": row[0],
                "credits": row[1],
                "users": row[2]
            }
        
        health_info["database"]["status"] = "healthy"
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_info["status"] = "unhealthy"
        health_info["database"]["status"] = "unhealthy"
        health_info["database"]["error"] = str(e)
        raise HTTPException(status_code=503, detail=health_info)
    
    return health_info