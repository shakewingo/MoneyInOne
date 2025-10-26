"""Tests for currency conversion correctness and refresh semantics.

These tests validate:
- Order-of-operations: symbol × shares × market_price, else fallback to original_amount
- Single conversion at request time using cached exchange rates
- Refresh does not overwrite original amount; only updates current_amount
"""

import uuid
from decimal import Decimal
from typing import Optional, Dict, Tuple, List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.finance_service import FinanceService
from app.models.schemas import AssetCreate, AssetCategory, Currency


class FakeMarketDataService:
    """Async context manager stub for MarketDataService used in tests."""

    def __init__(self, prices: Dict[str, Decimal], fx: Dict[Tuple[str, str], Decimal]):
        self._prices = prices
        self._fx = fx

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get_stock_price(self, symbol: str) -> Optional[Decimal]:
        return self._prices.get(symbol)

    async def get_crypto_price(self, symbol: str) -> Optional[Decimal]:
        return self._prices.get(symbol)

    async def get_commodity_price(self, commodity: str) -> Optional[Decimal]:
        # commodity keys like "gold" or "silver" intentionally allowed
        return self._prices.get(commodity)

    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        if from_currency == to_currency:
            return Decimal("1.0")
        return self._fx.get((from_currency, to_currency))

    async def update_multiple_assets(self, assets_data: List[Dict], base_currency: str = "USD"):
        # Return tuples: (success, market_price, current_amount) in native currency
        results = {}
        for a in assets_data:
            symbol = a.get("symbol")
            shares = Decimal(str(a.get("shares", 1)))
            price = self._prices.get(symbol)
            if price is None:
                results[a.get("id")] = (False, None, None)
            else:
                current_amount = price * shares
                results[a.get("id")] = (True, price, current_amount)
        return results


@pytest.mark.asyncio
async def test_order_of_operations_and_currency_switch(monkeypatch, service: FinanceService):
    """Verify symbol×shares×price then convert; switching base currency recomputes correctly."""
    device_id = "conv-switch"

    # Create one USD stock and one EUR cash
    stock = AssetCreate(
        name="Apple",
        category=AssetCategory.STOCK,
        amount=Decimal("1000.00"),  # will be ignored in favor of shares×price
        currency=Currency.USD,
        purchase_date="2024-01-01",
        symbol="AAPL",
        shares=Decimal("3"),
        is_market_tracked=True,
    )
    eur_cash = AssetCreate(
        name="EUR Cash",
        category=AssetCategory.CASH,
        amount=Decimal("100.00"),
        currency=Currency.EUR,
        purchase_date="2024-01-02",
    )

    stock_id = await service.create_asset(device_id, stock)
    _ = await service.create_asset(device_id, eur_cash)

    # Provide deterministic market prices and FX
    prices = {"AAPL": Decimal("200")}
    fx = {
        ("USD", "CNY"): Decimal("7.0"),
        ("EUR", "CNY"): Decimal("8.0"),
        ("EUR", "USD"): Decimal("1.1"),
    }

    # Patch MarketDataService in the finance_service module
    from app.services import finance_service as fs_module

    def fake_factory(*args, **kwargs):
        return FakeMarketDataService(prices, fx)

    monkeypatch.setattr(fs_module, "MarketDataService", fake_factory)

    # Base CNY: stock 3*200*7 = 4200; EUR cash 100*8 = 800
    grouped_cny = await service.get_assets_grouped_by_category(device_id, base_currency="CNY")
    assert grouped_cny["stock"].total_amount == Decimal("4200")
    assert grouped_cny["cash"].total_amount == Decimal("800")

    # Base USD: stock 3*200 = 600; EUR cash 100*1.1 = 110
    grouped_usd = await service.get_assets_grouped_by_category(device_id, base_currency="USD")
    assert grouped_usd["stock"].total_amount == Decimal("600")
    assert grouped_usd["cash"].total_amount == Decimal("110")


@pytest.mark.asyncio
async def test_refresh_does_not_overwrite_amount(monkeypatch, service: FinanceService):
    """Refresh updates current_amount only; amount (original currency) remains unchanged."""
    device_id = "refresh-amount"
    asset = AssetCreate(
        name="Tracked Stock",
        category=AssetCategory.STOCK,
        amount=Decimal("300.00"),
        currency=Currency.USD,
        purchase_date="2024-01-01",
        symbol="AAPL",
        shares=Decimal("3"),
        is_market_tracked=True,
    )
    asset_id = await service.create_asset(device_id, asset)

    prices = {"AAPL": Decimal("200")}
    fx = {}

    from app.services import finance_service as fs_module

    def fake_factory(*args, **kwargs):
        return FakeMarketDataService(prices, fx)

    monkeypatch.setattr(fs_module, "MarketDataService", fake_factory)

    # Run refresh; current_amount should become 3*200=600 (native USD), amount should remain 300
    await service.refresh_prices(device_id, [asset_id], base_currency="USD")

    # Read back
    updated = await service.get_asset_by_id(asset_id, device_id)
    assert updated.amount == Decimal("300.00")
    assert updated.current_amount == Decimal("600")


