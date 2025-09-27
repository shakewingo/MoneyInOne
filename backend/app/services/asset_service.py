"""Asset management service with business logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asset import Asset, AssetType
from app.models.user import User
from app.models.schemas import AssetCreate, AssetUpdate, AssetResponse
from app.services.exceptions import NotFoundError, ValidationError


class AssetService:
    """Service for asset management operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize asset service with database session."""
        self.db = db_session
    
    async def get_assets(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        asset_type_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
    ) -> tuple[List[Asset], int]:
        """Get assets for a user with optional filtering and pagination."""
        # Build query
        query = (
            select(Asset)
            .options(selectinload(Asset.asset_type))
            .where(Asset.user_id == user_id)
        )
        
        # Apply filters
        if asset_type_id:
            query = query.where(Asset.asset_type_id == asset_type_id)
        
        if tags:
            # Filter assets that have any of the specified tags
            for tag in tags:
                query = query.where(Asset.tags.any(tag))
        
        # Get total count
        count_query = select(func.count(Asset.id)).where(Asset.user_id == user_id)
        if asset_type_id:
            count_query = count_query.where(Asset.asset_type_id == asset_type_id)
        
        total_count_result = await self.db.execute(count_query)
        total_count = total_count_result.scalar() or 0
        
        # Apply pagination and execute
        query = query.offset(skip).limit(limit).order_by(Asset.created_at.desc())
        result = await self.db.execute(query)
        assets = result.scalars().all()
        
        return list(assets), total_count
    
    async def get_asset_by_id(self, asset_id: UUID, user_id: UUID) -> Asset:
        """Get a specific asset by ID, ensuring it belongs to the user."""
        query = (
            select(Asset)
            .options(selectinload(Asset.asset_type))
            .where(Asset.id == asset_id, Asset.user_id == user_id)
        )
        result = await self.db.execute(query)
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise NotFoundError(f"Asset with ID {asset_id} not found")
        
        return asset
    
    async def create_asset(self, asset_data: AssetCreate, user_id: UUID) -> Asset:
        """Create a new asset for the user."""
        # Verify user exists
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        if not user_result.scalar_one_or_none():
            raise NotFoundError(f"User with ID {user_id} not found")
        
        # Verify asset type exists
        asset_type_query = select(AssetType).where(AssetType.id == asset_data.asset_type_id)
        asset_type_result = await self.db.execute(asset_type_query)
        if not asset_type_result.scalar_one_or_none():
            raise NotFoundError(f"Asset type with ID {asset_data.asset_type_id} not found")
        
        # Create asset
        asset = Asset(
            user_id=user_id,
            asset_type_id=asset_data.asset_type_id,
            name=asset_data.name,
            symbol=asset_data.symbol,
            quantity=asset_data.quantity,
            purchase_price=asset_data.purchase_price,
            purchase_currency=asset_data.purchase_currency,
            purchase_date=asset_data.purchase_date,
            attributes=asset_data.attributes,
            tags=asset_data.tags,
        )
        
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        
        # Load relationships
        await self.db.refresh(asset, ["asset_type"])
        
        return asset
    
    async def update_asset(
        self, 
        asset_id: UUID, 
        asset_data: AssetUpdate, 
        user_id: UUID
    ) -> Asset:
        """Update an existing asset."""
        # Get the asset
        asset = await self.get_asset_by_id(asset_id, user_id)
        
        # Update fields that are provided
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)
        
        await self.db.commit()
        await self.db.refresh(asset)
        
        # Load relationships
        await self.db.refresh(asset, ["asset_type"])
        
        return asset
    
    async def delete_asset(self, asset_id: UUID, user_id: UUID) -> None:
        """Delete an asset."""
        asset = await self.get_asset_by_id(asset_id, user_id)
        await self.db.delete(asset)
        await self.db.commit()
    
    async def get_asset_types(self) -> List[AssetType]:
        """Get all available asset types."""
        query = select(AssetType).order_by(AssetType.is_default.desc(), AssetType.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())
