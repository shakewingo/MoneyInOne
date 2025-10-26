"""Simplified finance service for asset management and portfolio calculations."""

import uuid
import logging
from decimal import Decimal
from typing import List, Dict, Optional, TypeVar, Generic, Callable, Union
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.asset import Asset, AssetType
from app.models.credit import Credit, CreditType
from app.models.schemas import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    PortfolioSummary,
    AssetBreakdown,
    CreditBreakdown,
    AssetCategoryBreakdown,
    CreditCategoryBreakdown,
    Currency,
    AssetCategory,
    CreditCategory,
    CreditCreate,
    CreditUpdate,
    CreditResponse,
)
from app.services.exceptions import (
    AssetNotFoundError,
    UserNotFoundError,
    AssetTypeNotFoundError,
    ValidationError,
    CreditNotFoundError,
)
from app.services.market_data_service import MarketDataService
from app.core.config import settings

logger = logging.getLogger(__name__)

# Generic types for assets and credits
ItemModel = TypeVar("ItemModel", Asset, Credit)
ItemResponse = TypeVar("ItemResponse", AssetResponse, CreditResponse)
CategoryBreakdown = TypeVar(
    "CategoryBreakdown", AssetCategoryBreakdown, CreditCategoryBreakdown
)


class FinanceService:
    """Consolidated service for asset management and portfolio calculations."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def _convert_to_base_currency(
        self, amount: Decimal, from_currency: str, to_currency: str
    ) -> tuple[Decimal, Decimal]:
        """
        Convert amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Tuple of (converted_amount, exchange_rate)
        """
        if from_currency == to_currency:
            return amount, Decimal("1.0")

        try:
            async with MarketDataService() as market_service:
                exchange_rate = await market_service.get_exchange_rate(
                    from_currency, to_currency
                )

                if exchange_rate:
                    converted_amount = amount * exchange_rate
                    logger.info(
                        f"Converted {amount} {from_currency} -> {converted_amount} {to_currency} @ rate {exchange_rate}"
                    )
                    return converted_amount, exchange_rate
                else:
                    logger.warning(
                        f"Failed to get exchange rate for {from_currency} -> {to_currency}, "
                        f"using original amount"
                    )
                    return amount, Decimal("1.0")
        except Exception as e:
            logger.error(
                f"Error converting currency {from_currency} -> {to_currency}: {e}, "
                f"using original amount"
            )
            return amount, Decimal("1.0")

    async def _group_and_convert_items(
        self,
        items: List[Union[Asset, Credit]],
        base_currency: str,
        response_class: type,
        breakdown_class: type,
    ) -> Dict[str, Union[AssetCategoryBreakdown, CreditCategoryBreakdown]]:
        """
        Generic method to group items by category with currency conversion.

        Args:
            items: List of assets or credits to group
            base_currency: Target currency for conversion
            response_class: Response schema class (AssetResponse or CreditResponse)
            breakdown_class: Breakdown schema class (AssetCategoryBreakdown or CreditCategoryBreakdown)

        Returns:
            Dictionary mapping categories to their breakdowns
        """
        grouped_items: Dict[str, List] = {}
        category_totals: Dict[str, Decimal] = {}

        for item in items:
            category = item.category

            # Initialize category if not exists
            if category not in grouped_items:
                grouped_items[category] = []
                category_totals[category] = Decimal("0")

            # Compute native amount (symbol * shares * price if available; else original_amount/amount)
            native_amount = await self._compute_native_amount(item)
            logger.debug(
                f"Computed native amount for item {getattr(item, 'id', None)}: {native_amount} {item.currency}"
            )

            # Convert native amount to base currency once
            converted_amount, conversion_rate = await self._convert_to_base_currency(
                native_amount, item.currency, base_currency
            )

            # Create response with conversion data
            item_dict = item.to_dict()
            item_dict["converted_amount"] = converted_amount
            item_dict["conversion_rate"] = conversion_rate
            item_response = response_class(**item_dict)

            grouped_items[category].append(item_response)
            category_totals[category] += converted_amount

        # Build final breakdown response
        return {
            category: breakdown_class(
                **{
                    (
                        "assets" if response_class == AssetResponse else "credits"
                    ): items_list,
                    "total_amount": category_totals[category],
                    "count": len(items_list),
                }
            )
            for category, items_list in grouped_items.items()
        }

    async def _calculate_category_summary(
        self,
        items: List[Union[Asset, Credit]],
        base_currency: str,
        breakdown_class: type,
    ) -> tuple[Dict[str, Union[AssetBreakdown, CreditBreakdown]], Decimal]:
        """
        Calculate category summaries and total amount in base currency.

        Args:
            items: List of assets or credits
            base_currency: Target currency for conversion
            breakdown_class: Breakdown class (AssetBreakdown or CreditBreakdown)

        Returns:
            Tuple of (category_summary_dict, total_amount)
        """
        category_totals: Dict[str, Decimal] = {}
        category_counts: Dict[str, int] = {}
        total_amount = Decimal("0")

        for item in items:
            category = item.category

            # Compute native amount and convert to base currency
            native_amount = await self._compute_native_amount(item)
            converted_amount, _ = await self._convert_to_base_currency(
                native_amount, item.currency, base_currency
            )

            # Update category aggregates
            category_totals[category] = (
                category_totals.get(category, Decimal("0")) + converted_amount
            )
            category_counts[category] = category_counts.get(category, 0) + 1
            total_amount += converted_amount

        # Build summary
        summary = {
            category: breakdown_class(
                total_amount=total_amount, count=category_counts[category]
            )
            for category, total_amount in category_totals.items()
        }

        return summary, total_amount

    async def _get_or_create_user(self, device_id: str) -> User:
        """Get existing user or create new one for device."""
        result = await self.db.execute(select(User).where(User.device_id == device_id))
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
                is_default=True,
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
                is_default=True,
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
            shares=asset_data.shares,
            is_market_tracked=asset_data.is_market_tracked,
            original_amount=asset_data.amount,
            last_price_update=datetime.now(timezone.utc),
        )

        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)

        logger.info(f"Created asset {asset.id} for user {user.id}")
        return asset.id

    async def get_asset_by_id(
        self, asset_id: uuid.UUID, device_id: str
    ) -> AssetResponse:
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

    async def get_assets_grouped_by_category(
        self, device_id: str, base_currency: str = "USD"
    ) -> Dict[str, AssetCategoryBreakdown]:
        """
        Get all assets grouped by category with currency conversion.

        Args:
            device_id: User device ID
            base_currency: Target currency for conversion (default: USD)

        Returns:
            Dict mapping category to AssetCategoryBreakdown with converted amounts
        """
        user = await self._get_or_create_user(device_id)

        result = await self.db.execute(
            select(Asset)
            .options(selectinload(Asset.asset_type))
            .where(Asset.user_id == user.id)
            .order_by(Asset.created_at.desc())
        )
        assets = result.scalars().all()

        return await self._group_and_convert_items(
            assets, base_currency, AssetResponse, AssetCategoryBreakdown
        )

    async def update_asset(
        self, asset_id: uuid.UUID, device_id: str, asset_data: AssetUpdate
    ) -> None:
        """Update an existing asset."""
        user = await self._get_or_create_user(device_id)

        result = await self.db.execute(
            select(Asset).where(and_(Asset.id == asset_id, Asset.user_id == user.id))
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
    async def create_credit(
        self, device_id: str, credit_data: CreditCreate
    ) -> uuid.UUID:
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
            notes=credit_data.notes,
        )

        self.db.add(credit)
        await self.db.commit()
        await self.db.refresh(credit)

        logger.info(f"Created credit {credit.id} for user {user.id}")
        return credit.id

    async def get_credit_by_id(
        self, credit_id: uuid.UUID, device_id: str
    ) -> CreditResponse:
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

    async def get_credits_grouped_by_category(
        self, device_id: str, base_currency: str = "USD"
    ) -> Dict[str, CreditCategoryBreakdown]:
        """
        Get all credits grouped by category with currency conversion.

        Args:
            device_id: User device ID
            base_currency: Target currency for conversion (default: USD)

        Returns:
            Dict mapping category to CreditCategoryBreakdown with converted amounts
        """
        user = await self._get_or_create_user(device_id)

        result = await self.db.execute(
            select(Credit)
            .options(selectinload(Credit.credit_type))
            .where(Credit.user_id == user.id)
            .order_by(Credit.created_at.desc())
        )
        credits = result.scalars().all()

        return await self._group_and_convert_items(
            credits, base_currency, CreditResponse, CreditCategoryBreakdown
        )

    async def update_credit(
        self, credit_id: uuid.UUID, device_id: str, credit_data: CreditUpdate
    ) -> None:
        """Update an existing credit."""
        user = await self._get_or_create_user(device_id)

        result = await self.db.execute(
            select(Credit).where(
                and_(Credit.id == credit_id, Credit.user_id == user.id)
            )
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
            select(Credit).where(
                and_(Credit.id == credit_id, Credit.user_id == user.id)
            )
        )
        credit = result.scalar_one_or_none()

        if not credit:
            raise CreditNotFoundError(f"Credit {credit_id} not found")

        await self.db.delete(credit)
        await self.db.commit()
        logger.info(f"Deleted credit {credit_id}")

    # Portfolio Operations
    async def get_portfolio_summary(
        self, device_id: str, base_currency: str = "USD"
    ) -> PortfolioSummary:
        """
        Get portfolio summary with breakdown by category in base currency.

        Args:
            device_id: User device ID
            base_currency: Target currency for all amounts (default: USD)

        Returns:
            Portfolio summary with all amounts converted to base currency
        """
        user = await self._get_or_create_user(device_id)

        # Fetch all assets and credits
        asset_result = await self.db.execute(
            select(Asset).where(Asset.user_id == user.id)
        )
        assets = asset_result.scalars().all()

        credit_result = await self.db.execute(
            select(Credit).where(Credit.user_id == user.id)
        )
        credits = credit_result.scalars().all()

        # Calculate summaries using helper method
        asset_summary, total_assets = await self._calculate_category_summary(
            assets, base_currency, AssetBreakdown
        )
        credit_summary, total_credits = await self._calculate_category_summary(
            credits, base_currency, CreditBreakdown
        )

        return PortfolioSummary(
            base_currency=base_currency,
            asset_summary=asset_summary,
            credit_summary=credit_summary,
            net_worth=total_assets - total_credits,
            last_updated=datetime.now(timezone.utc),
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
            ("Crypto", "crypto"),
            ("Real Estate", "real_estate"),
            ("Bond", "bond"),
            ("Gold", "gold"),
            ("Silver", "silver"),
            ("Other", "other"),
            ]

        for name, category in default_types:
            result = await self.db.execute(
                select(AssetType).where(AssetType.category == category)
            )
            existing = result.scalar_one_or_none()

            if not existing:
                asset_type = AssetType(name=name, category=category, is_default=True)
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
                credit_type = CreditType(name=name, category=category, is_default=True)
                self.db.add(credit_type)

        await self.db.commit()
        logger.info("Ensured default credit types exist")

    async def refresh_prices(
        self,
        device_id: str,
        asset_ids: Optional[List[uuid.UUID]] = None,
        base_currency: str = "USD",
    ) -> Dict[str, int]:
        """
        Refresh market prices for assets.

        Args:
            device_id: User device ID
            asset_ids: Optional list of specific asset IDs to refresh. If None, refreshes all market-tracked assets.
            base_currency: Target currency for conversion (default: USD)
        Returns:
            Dict with counts: {"updated": int, "failed": int, "skipped": int}
        """
        user = await self._get_or_create_user(device_id)

        # Build query for assets to refresh
        query = select(Asset).where(
            and_(Asset.user_id == user.id, Asset.is_market_tracked == True)
        )

        if asset_ids:
            query = query.where(Asset.id.in_(asset_ids))

        result = await self.db.execute(query)
        assets = result.scalars().all()

        if not assets:
            return {"updated": 0, "failed": 0, "skipped": 0}

        # Prepare asset data for market service
        assets_data = []
        for asset in assets:
            if not asset.symbol:  # Skip assets without symbols
                continue
            assets_data.append(
                {
                    "id": str(asset.id),
                    "category": asset.category,
                    "symbol": asset.symbol,
                    "shares": float(asset.shares) if asset.shares else 1.0,
                    "currency": asset.currency,
                    "amount": asset.amount,
                }
            )

        # Fetch market data (prices are in the asset's native/original currency)
        async with MarketDataService() as market_service:
            price_results = await market_service.update_multiple_assets(
                assets_data, base_currency
            )

        # Update database with new prices
        updated_count = 0
        failed_count = 0
        skipped_count = len(assets) - len(assets_data)  # Assets without symbols

        for asset in assets:
            asset_id = str(asset.id)
            if asset_id not in price_results:
                continue

            success, market_price, current_amount = price_results[asset_id]
            logger.info(f"Obtained asset {asset_id}: market_price: {market_price}")

            if success:
                # Initialize original_amount if not set; keep it immutable afterwards
                if asset.original_amount is None:
                    asset.original_amount = asset.amount

                # Update current market value in native currency only
                asset.current_amount = current_amount
                asset.last_price_update = datetime.now(timezone.utc)
                updated_count += 1

                logger.info(f"Updated asset {asset_id}: -> {current_amount}")
            else:
                failed_count += 1
                logger.warning(f"Failed to update price for asset {asset_id}")

        await self.db.commit()

        return {
            "updated": updated_count,
            "failed": failed_count,
            "skipped": skipped_count,
        }

    async def _compute_native_amount(self, item: Union[Asset, Credit]) -> Decimal:
        """Compute the item's amount in its native/original currency.

        Order-of-operations:
        - If symbol and shares are available (market-tracked assets):
          native_amount = shares * market_price(symbol) using cached price fetchers.
        - Else: native_amount = original_amount if available, else amount.
        """
        # Credits have no symbol/shares; fall back directly
        symbol = getattr(item, "symbol", None)
        shares = getattr(item, "shares", None)
        category = getattr(item, "category", None)

        if symbol and shares and category in {"stock", "crypto", "gold", "silver"}:
            try:
                async with MarketDataService() as market_service:
                    if category == "stock":
                        price = await market_service.get_stock_price(symbol)
                    elif category == "crypto":
                        price = await market_service.get_crypto_price(symbol)
                    elif category in {"gold", "silver"}:
                        price = await market_service.get_commodity_price(category)
                    else:
                        price = None

                if price is not None:
                    return price * Decimal(str(shares))
            except Exception as e:
                logger.warning(f"Failed to compute native amount via market price for {symbol}: {e}")
        return item.amount

    async def refresh_single_asset_price(
        self, asset_id: uuid.UUID, device_id: str
    ) -> bool:
        """
        Refresh price for a single asset.

        Returns:
            bool: True if successfully updated, False otherwise
        """
        result = await self.refresh_prices(device_id, [asset_id])
        return result["updated"] > 0
