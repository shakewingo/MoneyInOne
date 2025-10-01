"""Market data endpoints for real-time price updates."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.finance_service import FinanceService
from app.models.schemas import SuccessResponse
from app.services.exceptions import AssetNotFoundError

router = APIRouter(prefix="/market-data", tags=["Market Data"])


@router.post("/refresh-prices", response_model=SuccessResponse)
async def refresh_all_prices(
    x_device_id: str = Header(..., description="Device ID for user identification"),
    db: AsyncSession = Depends(get_db_session)
):
    """Refresh market prices for all market-tracked assets."""
    try:
        finance_service = FinanceService(db)
        result = await finance_service.refresh_prices(x_device_id)
        
        return SuccessResponse(
            message=f"Price refresh completed: {result['updated']} updated, {result['failed']} failed, {result['skipped']} skipped",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price refresh failed: {str(e)}")


@router.post("/refresh-prices/assets", response_model=SuccessResponse)
async def refresh_specific_assets(
    asset_ids: List[uuid.UUID],
    x_device_id: str = Header(..., description="Device ID for user identification"),
    db: AsyncSession = Depends(get_db_session)
):
    """Refresh market prices for specific assets."""
    try:
        finance_service = FinanceService(db)
        result = await finance_service.refresh_prices(x_device_id, asset_ids)
        
        return SuccessResponse(
            message=f"Price refresh completed for {len(asset_ids)} assets: {result['updated']} updated, {result['failed']} failed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price refresh failed: {str(e)}")


@router.post("/refresh-price/{asset_id}", response_model=SuccessResponse)
async def refresh_single_asset_price(
    asset_id: uuid.UUID,
    x_device_id: str = Header(..., description="Device ID for user identification"),
    db: AsyncSession = Depends(get_db_session)
):
    """Refresh market price for a single asset."""
    try:
        finance_service = FinanceService(db)
        success = await finance_service.refresh_single_asset_price(asset_id, x_device_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found or price update failed")
        
        return SuccessResponse(
            message=f"Asset {asset_id} price updated successfully"
        )
    except AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price refresh failed: {str(e)}")
