"""Asset management endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.schemas import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetTypeResponse,
    PaginatedResponse,
    APIResponse,
)
from app.services.asset_service import AssetService
from app.services.exceptions import NotFoundError, ValidationError

router = APIRouter()

# TODO: Replace with actual user authentication
MOCK_USER_ID = UUID("550e8400-e29b-41d4-a716-446655440000")


async def get_asset_service(db: AsyncSession = Depends(get_db_session)) -> AssetService:
    """Dependency to get asset service."""
    return AssetService(db)


@router.get("/", response_model=PaginatedResponse)
async def get_assets(
    skip: int = Query(0, ge=0, description="Number of assets to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of assets to return"),
    asset_type_id: Optional[UUID] = Query(None, description="Filter by asset type"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    service: AssetService = Depends(get_asset_service),
) -> PaginatedResponse:
    """Get all assets for the user with pagination and filtering."""
    try:
        # Parse tags if provided
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None
        
        assets, total_count = await service.get_assets(
            user_id=MOCK_USER_ID,
            skip=skip,
            limit=limit,
            asset_type_id=asset_type_id,
            tags=tag_list,
        )
        
        # Convert to response models
        asset_responses = [AssetResponse.model_validate(asset) for asset in assets]
        
        return PaginatedResponse(
            items=asset_responses,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve assets: {str(e)}")


@router.post("/", response_model=AssetResponse, status_code=201)
async def create_asset(
    asset_data: AssetCreate,
    service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Create a new asset."""
    try:
        asset = await service.create_asset(asset_data, MOCK_USER_ID)
        return AssetResponse.model_validate(asset)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create asset: {str(e)}")


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Get a specific asset by ID."""
    try:
        asset = await service.get_asset_by_id(asset_id, MOCK_USER_ID)
        return AssetResponse.model_validate(asset)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve asset: {str(e)}")


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: UUID,
    asset_update: AssetUpdate,
    service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Update an existing asset."""
    try:
        asset = await service.update_asset(asset_id, asset_update, MOCK_USER_ID)
        return AssetResponse.model_validate(asset)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update asset: {str(e)}")


@router.delete("/{asset_id}", response_model=APIResponse)
async def delete_asset(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
) -> APIResponse:
    """Delete an asset."""
    try:
        await service.delete_asset(asset_id, MOCK_USER_ID)
        return APIResponse(message=f"Asset {asset_id} deleted successfully")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete asset: {str(e)}")


@router.get("/types/", response_model=List[AssetTypeResponse])
async def get_asset_types(
    service: AssetService = Depends(get_asset_service),
) -> List[AssetTypeResponse]:
    """Get all available asset types."""
    try:
        asset_types = await service.get_asset_types()
        return [AssetTypeResponse.model_validate(asset_type) for asset_type in asset_types]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve asset types: {str(e)}")
