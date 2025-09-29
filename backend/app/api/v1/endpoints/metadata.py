"""Simplified metadata endpoints."""

import logging
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.schemas import MetadataResponse, CurrencyInfo
from app.services.finance_service import FinanceService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=MetadataResponse)
async def get_metadata(
    db: AsyncSession = Depends(get_db_session)
):
    """Get application metadata including currencies and asset categories."""
    try:
        service = FinanceService(db)
        
        # Get currencies and categories
        currencies_data = await service.get_currencies()
        asset_categories = await service.get_asset_categories()
        
        # Convert to proper schema format
        currencies = [CurrencyInfo(**currency) for currency in currencies_data]
        
        return MetadataResponse(
            currencies=currencies,
            asset_categories=asset_categories
        )
    except Exception as e:
        logger.error(f"Error fetching metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/currencies", response_model=List[CurrencyInfo])
async def get_currencies(
    db: AsyncSession = Depends(get_db_session)
):
    """Get list of supported currencies."""
    try:
        service = FinanceService(db)
        currencies_data = await service.get_currencies()
        return [CurrencyInfo(**currency) for currency in currencies_data]
    except Exception as e:
        logger.error(f"Error fetching currencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[str])
async def get_asset_categories(
    db: AsyncSession = Depends(get_db_session)
):
    """Get list of supported asset categories."""
    try:
        service = FinanceService(db)
        categories = await service.get_asset_categories()
        return categories
    except Exception as e:
        logger.error(f"Error fetching asset categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))