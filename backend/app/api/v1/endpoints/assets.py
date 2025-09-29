"""Simplified asset management endpoints."""

import uuid
import logging
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.schemas import (
    AssetCreate, AssetUpdate, AssetResponse, SuccessResponse
)
from app.services.finance_service import FinanceService
from app.services.exceptions import AssetNotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=SuccessResponse)
async def create_asset(
    asset_data: AssetCreate,
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new asset."""
    try:
        service = FinanceService(db)
        asset_id = await service.create_asset(device_id, asset_data)
        
        # Get the created asset to return in response
        created_asset = await service.get_asset_by_id(asset_id, device_id)
        
        return SuccessResponse(
            message="Asset created successfully",
            data=created_asset
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=Dict[str, List[AssetResponse]])
async def get_assets_grouped(
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all assets grouped by category."""
    try:
        service = FinanceService(db)
        assets = await service.get_assets_grouped_by_category(device_id)
        return assets
    except Exception as e:
        logger.error(f"Error fetching grouped assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: uuid.UUID,
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific asset by ID."""
    try:
        service = FinanceService(db)
        asset = await service.get_asset_by_id(asset_id, device_id)
        return asset
    except AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except Exception as e:
        logger.error(f"Error fetching asset {asset_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{asset_id}", response_model=SuccessResponse)
async def update_asset(
    asset_id: uuid.UUID,
    asset_data: AssetUpdate,
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Update an existing asset."""
    try:
        service = FinanceService(db)
        await service.update_asset(asset_id, device_id, asset_data)
        
        # Get the updated asset to return in response
        updated_asset = await service.get_asset_by_id(asset_id, device_id)
        
        return SuccessResponse(
            message="Asset updated successfully",
            data=updated_asset
        )
    except AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating asset {asset_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{asset_id}", response_model=SuccessResponse)
async def delete_asset(
    asset_id: uuid.UUID,
    device_id: str = Query(..., description="Device identifier"),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete an asset."""
    try:
        service = FinanceService(db)
        await service.delete_asset(asset_id, device_id)
        
        return SuccessResponse(message="Asset deleted successfully")
    except AssetNotFoundError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except Exception as e:
        logger.error(f"Error deleting asset {asset_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))