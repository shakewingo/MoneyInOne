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
from app.models.credit import Credit, CreditType
from app.models.schemas import (
    AssetCreate, AssetUpdate, AssetResponse, PortfolioSummary, 
    AssetBreakdown, CreditBreakdown, Currency, AssetCategory, CreditCategory,
    CreditCreate, CreditUpdate, CreditResponse
)
from app.services.exceptions import (
    AssetNotFoundError, UserNotFoundError, AssetTypeNotFoundError, ValidationError, CreditNotFoundError
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
    
    async def _get_or_create_credit_type(self, category: str) -> CreditType:
        """Get or create credit type for category."""
        result = await self.db.execute(
            select(CreditType).where(CreditType.category == category)
        )
        credit_type = result.scalar_one_or_none()
        
        if not credit_type:
            credit_type = CreditType(
                name=category.replace("_", " ").title(),
                category=category,
                is_default=True
            )
            self.db.add(credit_type)
            await self.db.commit()
            await self.db.refresh(credit_type)
            logger.info(f"Created new credit type: {category}")
        
        return credit_type
    
    # Asset CRUD Operations
    async def create_asset(self, device_id: str, asset_data: AssetCreate) -> uuid.UUID:
        """Create a new asset."""
        user = await self._get_or_create_user(device_id)
        asset_type = await self._get_or_create_asset_type(asset_data.category)
        
        asset = Asset(
            user_id=user.id,
            asset_type_id=asset_type.id,
            name=asset_data.name,
            category=asset_data.category,
            amount=asset_data.amount,
            currency=asset_data.currency,
            purchase_date=asset_data.purchase_date,
            notes=asset_data.notes,
            symbol=asset_data.symbol,
            shares=asset_data.shares
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
    
    # Credit CRUD Operations
    async def create_credit(self, device_id: str, credit_data: CreditCreate) -> uuid.UUID:
        """Create a new credit."""
        user = await self._get_or_create_user(device_id)
        credit_type = await self._get_or_create_credit_type(credit_data.category)
        
        credit = Credit(
            user_id=user.id,
            credit_type_id=credit_type.id,
            name=credit_data.name,
            category=credit_data.category,
            amount=credit_data.amount,
            currency=credit_data.currency,
            issue_date=credit_data.issue_date,
            notes=credit_data.notes
        )
        
        self.db.add(credit)
        await self.db.commit()
        await self.db.refresh(credit)
        
        logger.info(f"Created credit {credit.id} for user {user.id}")
        return credit.id
    
    async def get_credit_by_id(self, credit_id: uuid.UUID, device_id: str) -> CreditResponse:
        """Get a specific credit by ID."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Credit)
            .options(selectinload(Credit.credit_type))
            .where(and_(Credit.id == credit_id, Credit.user_id == user.id))
        )
        credit = result.scalar_one_or_none()
        
        if not credit:
            raise CreditNotFoundError(f"Credit {credit_id} not found")
        
        return CreditResponse(**credit.to_dict())
    
    async def get_credits_grouped_by_category(self, device_id: str) -> Dict[str, List[CreditResponse]]:
        """Get all credits grouped by category."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Credit)
            .options(selectinload(Credit.credit_type))
            .where(Credit.user_id == user.id)
            .order_by(Credit.created_at.desc())
        )
        credits = result.scalars().all()
        
        grouped_credits: Dict[str, List[CreditResponse]] = {}
        
        for credit in credits:
            category = credit.category
            if category not in grouped_credits:
                grouped_credits[category] = []
            
            credit_response = CreditResponse(**credit.to_dict())
            grouped_credits[category].append(credit_response)
        
        return grouped_credits
    
    async def update_credit(
        self,
        credit_id: uuid.UUID,
        device_id: str,
        credit_data: CreditUpdate
    ) -> None:
        """Update an existing credit."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Credit)
            .where(and_(Credit.id == credit_id, Credit.user_id == user.id))
        )
        credit = result.scalar_one_or_none()
        
        if not credit:
            raise CreditNotFoundError(f"Credit {credit_id} not found")
        
        # Update fields
        update_data = credit_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(credit, field, value)
        
        await self.db.commit()
        logger.info(f"Updated credit {credit_id}")
    
    async def delete_credit(self, credit_id: uuid.UUID, device_id: str) -> None:
        """Delete a credit."""
        user = await self._get_or_create_user(device_id)
        
        result = await self.db.execute(
            select(Credit).where(and_(Credit.id == credit_id, Credit.user_id == user.id))
        )
        credit = result.scalar_one_or_none()
        
        if not credit:
            raise CreditNotFoundError(f"Credit {credit_id} not found")
        
        await self.db.delete(credit)
        await self.db.commit()
        logger.info(f"Deleted credit {credit_id}")
    
    # Portfolio Operations
    async def get_portfolio_summary(
        self, 
        device_id: str, 
        base_currency: str = "USD"
    ) -> PortfolioSummary:
        """Get portfolio summary with breakdown by category."""
        user = await self._get_or_create_user(device_id)
        
        # Get asset breakdown
        asset_result = await self.db.execute(
            select(Asset.category, func.sum(Asset.amount), func.count(Asset.id))
            .where(Asset.user_id == user.id)
            .group_by(Asset.category)
        )
        
        asset_category_data = asset_result.fetchall()
        asset_summary = {}
        
        for category, total_amount, count in asset_category_data:
            asset_summary[category] = AssetBreakdown(
                total_amount=total_amount,
                count=count
            )
        
        # Get credit breakdown
        credit_result = await self.db.execute(
            select(Credit.category, func.sum(Credit.amount), func.count(Credit.id))
            .where(Credit.user_id == user.id)
            .group_by(Credit.category)
        )
        
        credit_category_data = credit_result.fetchall()
        credit_summary = {}
        
        for category, total_amount, count in credit_category_data:
            credit_summary[category] = CreditBreakdown(
                total_amount=total_amount,
                count=count
            )
        
        # Calculate net summary (assets - credits by currency)
        # Get all assets by currency
        asset_currency_result = await self.db.execute(
            select(Asset.currency, func.sum(Asset.amount))
            .where(Asset.user_id == user.id)
            .group_by(Asset.currency)
        )
        
        # Get all credits by currency  
        credit_currency_result = await self.db.execute(
            select(Credit.currency, func.sum(Credit.amount))
            .where(Credit.user_id == user.id)
            .group_by(Credit.currency)
        )
        
        asset_by_currency = {currency: amount for currency, amount in asset_currency_result.fetchall()}
        credit_by_currency = {currency: amount for currency, amount in credit_currency_result.fetchall()}
        
        # Calculate net amounts
        all_currencies = set(asset_by_currency.keys()) | set(credit_by_currency.keys())
        net_summary = {}
        
        for currency in all_currencies:
            asset_total = asset_by_currency.get(currency, Decimal('0'))
            credit_total = credit_by_currency.get(currency, Decimal('0'))
            net_summary[currency] = asset_total - credit_total
        
        return PortfolioSummary(
            base_currency=base_currency,
            asset_summary=asset_summary,
            credit_summary=credit_summary,
            net_summary=net_summary,
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
        return [category for category in AssetCategory]
    
    async def get_credit_categories(self) -> List[str]:
        """Get list of supported credit categories."""
        return [category for category in CreditCategory]
    
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
    
    async def ensure_default_credit_types(self) -> None:
        """Ensure default credit types exist in database."""
        default_types = [
            ("Credit Card", "credit_card"),
            ("Loan", "loan"),
            ("Mortgage", "mortgage"),
            ("Line of Credit", "line_of_credit"),
            ("Other", "other"),
        ]
        
        for name, category in default_types:
            result = await self.db.execute(
                select(CreditType).where(CreditType.category == category)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                credit_type = CreditType(
                    name=name,
                    category=category,
                    is_default=True
                )
                self.db.add(credit_type)
        
        await self.db.commit()
        logger.info("Ensured default credit types exist")
