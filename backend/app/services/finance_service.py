"""Simplified finance service for asset management and portfolio calculations."""

import uuid
import logging
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.asset import Asset, AssetType
from app.models.schemas import (
    AssetCreate, AssetUpdate, AssetResponse, PortfolioSummary, 
    AssetBreakdown, Currency, AssetCategory
)
from app.services.exceptions import (
    AssetNotFoundError, UserNotFoundError, AssetTypeNotFoundError, ValidationError
)

logger = logging.getLogger(__name__)


class FinanceService:
    """Consolidated service for asset management and portfolio calculations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def _get_or_create_user(self, device_id: str) -> User:
        """Get existing user or create new one for device."""
        result = await self.db.execute(
            select(User).where(User.device_id == device_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(device_id=device_id)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Created new user for device: {device_id}")
        
        return user
    
    async def _get_or_create_asset_type(self, category: str) -> AssetType:
        """Get or create asset type for category."""
        result = await self.db.execute(
            select(AssetType).where(AssetType.category == category)
        )
        asset_type = result.scalar_one_or_none()
        
        if not asset_type:
            asset_type = AssetType(
                name=category.replace("_", " ").title(),
                category=category,
                is_default=True
            )
            self.db.add(asset_type)
            await self.db.commit()
            await self.db.refresh(asset_type)
            logger.info(f"Created new asset type: {category}")
        
        return asset_type
    
    # Asset CRUD Operations
    async def create_asset(self, device_id: str, asset_data: AssetCreate) -> uuid.UUID:
        """Create a new asset."""
        user = await self._get_or_create_user(device_id)
        asset_type = await self._get_or_create_asset_type(asset_data.category.value)
        
        asset = Asset(
            user_id=user.id,
            asset_type_id=asset_type.id,
            name=asset_data.name,
            category=asset_data.category.value,
            amount=asset_data.amount,
            currency=asset_data.currency.value,
            purchase_date=asset_data.purchase_date,
            notes=asset_data.notes
        )
        
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        
        logger.info(f"Created asset {asset.id} for user {user.id}")
        return asset.id
    
    async def get_asset_by_id(self, asset_id: uuid.UUID, device_id: str) -> AssetResponse:
        """Get a specific asset by ID."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Asset)
            .options(selectinload(Asset.asset_type))
            .where(and_(Asset.id == asset_id, Asset.user_id == user.id))
        )
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")
        
        return AssetResponse(**asset.to_dict())
    
    async def get_assets_grouped_by_category(self, device_id: str) -> Dict[str, List[AssetResponse]]:
        """Get all assets grouped by category."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Asset)
            .options(selectinload(Asset.asset_type))
            .where(Asset.user_id == user.id)
            .order_by(Asset.created_at.desc())
        )
        assets = result.scalars().all()
        
        grouped_assets: Dict[str, List[AssetResponse]] = {}
        
        for asset in assets:
            category = asset.category
            if category not in grouped_assets:
                grouped_assets[category] = []
            
            asset_response = AssetResponse(**asset.to_dict())
            grouped_assets[category].append(asset_response)
        
        return grouped_assets
    
    async def update_asset(
        self,
        asset_id: uuid.UUID,
        device_id: str,
        asset_data: AssetUpdate
    ) -> None:
        """Update an existing asset."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Asset)
            .where(and_(Asset.id == asset_id, Asset.user_id == user.id))
        )
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")
        
        # Update fields
        update_data = asset_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "currency" and value is not None:
                value = value.value  # Convert enum to string
            elif field == "category" and value is not None:
                value = value.value  # Convert enum to string
            setattr(asset, field, value)
        
        await self.db.commit()
        logger.info(f"Updated asset {asset_id}")
    
    async def delete_asset(self, asset_id: uuid.UUID, device_id: str) -> None:
        """Delete an asset."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Asset).where(and_(Asset.id == asset_id, Asset.user_id == user.id))
        )
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise AssetNotFoundError(f"Asset {asset_id} not found")
        
        await self.db.delete(asset)
        await self.db.commit()
        logger.info(f"Deleted asset {asset_id}")
    
    # Portfolio Operations
    async def get_portfolio_summary(
        self, 
        device_id: str, 
        base_currency: str = "USD"
    ) -> PortfolioSummary:
        """Get portfolio summary with breakdown by category."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Asset.category, func.sum(Asset.amount), func.count(Asset.id))
            .where(Asset.user_id == user.id)
            .group_by(Asset.category)
        )
        
        category_data = result.fetchall()
        asset_breakdown = {}
        
        for category, total_amount, count in category_data:
            asset_breakdown[category] = AssetBreakdown(
                total_amount=total_amount,
                count=count
            )
        
        return PortfolioSummary(
            base_currency=base_currency,
            asset_breakdown=asset_breakdown,
            last_updated=datetime.utcnow()
        )
    
    # Metadata Operations
    async def get_currencies(self) -> List[Dict[str, str]]:
        """Get list of supported currencies."""
        currencies = [
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"},
            {"code": "GBP", "name": "British Pound", "symbol": "£"},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
            {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
            {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
            {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
        ]
        return currencies
    
    async def get_asset_categories(self) -> List[str]:
        """Get list of supported asset categories."""
        return [category.value for category in AssetCategory]
    
    async def ensure_default_asset_types(self) -> None:
        """Ensure default asset types exist in database."""
        default_types = [
            ("Cash", "cash"),
            ("Stock", "stock"),
            ("Cryptocurrency", "crypto"),
            ("Real Estate", "real_estate"),
            ("Other", "other"),
        ]
        
        for name, category in default_types:
            result = await self.db.execute(
                select(AssetType).where(AssetType.category == category)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                asset_type = AssetType(
                    name=name,
                    category=category,
                    is_default=True
                )
                self.db.add(asset_type)
        
        await self.db.commit()
        logger.info("Ensured default asset types exist")
