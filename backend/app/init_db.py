#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models.base import Base
from app.models import User, Asset, AssetType, Credit, CreditType  # Import all models

logger = logging.getLogger(__name__)


async def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=True,
    )
    
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()


async def init_default_data():
    """Initialize default data."""
    from app.core.database import AsyncSessionLocal
    from app.services.finance_service import FinanceService
    
    logger.info("Initializing default data...")
    
    async with AsyncSessionLocal() as session:
        service = FinanceService(session)
        
        # Create default asset and credit types
        await service.ensure_default_asset_types()
        await service.ensure_default_credit_types()
        
        logger.info("Default data initialized successfully!")


async def main():
    """Main initialization function."""
    try:
        await create_tables()
        await init_default_data()
        logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)