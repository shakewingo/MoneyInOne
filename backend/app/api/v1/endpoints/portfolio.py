"""Simplified portfolio endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.schemas import PortfolioSummary
from app.services.finance_service import FinanceService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    device_id: str = Query(..., description="Device identifier"),
    base_currency: str = Query("USD", description="Base currency for calculations"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get portfolio summary with breakdown by asset category."""
    try:
        service = FinanceService(db)
        summary = await service.get_portfolio_summary(device_id, base_currency)
        return summary
    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))