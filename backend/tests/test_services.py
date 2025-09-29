"""Test services for simplified finance app."""

import pytest
import uuid
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.finance_service import FinanceService
from app.services.exceptions import AssetNotFoundError
from app.models.schemas import AssetCreate, AssetUpdate, AssetCategory, Currency
from app.models.user import User
from app.models.asset import Asset, AssetType


@pytest.mark.asyncio
async def test_finance_service_create_user(test_session: AsyncSession):
    """Test user creation in finance service."""
    service = FinanceService(test_session)
    device_id = "test-device-create-user"
    
    # First call should create user
    user1 = await service._get_or_create_user(device_id)
    assert user1.device_id == device_id
    assert user1.id is not None
    
    # Second call should return same user
    user2 = await service._get_or_create_user(device_id)
    assert user1.id == user2.id
    assert user1.device_id == user2.device_id


@pytest.mark.asyncio
async def test_finance_service_create_asset_type(test_session: AsyncSession):
    """Test asset type creation in finance service."""
    service = FinanceService(test_session)
    category = "cash"
    
    # First call should create asset type
    asset_type1 = await service._get_or_create_asset_type(category)
    assert asset_type1.category == category
    assert asset_type1.name == "Cash"
    assert asset_type1.is_default is True
    
    # Second call should return same asset type
    asset_type2 = await service._get_or_create_asset_type(category)
    assert asset_type1.id == asset_type2.id


@pytest.mark.asyncio
async def test_create_asset(test_session: AsyncSession):
    """Test asset creation."""
    service = FinanceService(test_session)
    device_id = "test-device-create-asset"
    
    asset_data = AssetCreate(
        name="Test Savings",
        category=AssetCategory.CASH,
        amount=Decimal("5000.00"),
        currency=Currency.USD,
        purchase_date=date(2024, 1, 15),
        notes="Test savings account"
    )
    
    # Create asset
    asset_id = await service.create_asset(device_id, asset_data)
    assert asset_id is not None
    
    # Verify asset was created
    asset = await service.get_asset_by_id(asset_id, device_id)
    assert asset.name == "Test Savings"
    assert asset.category == "cash"
    assert asset.amount == Decimal("5000.00")
    assert asset.currency == "USD"
    assert asset.notes == "Test savings account"


@pytest.mark.asyncio
async def test_get_asset_by_id(test_session: AsyncSession):
    """Test getting asset by ID."""
    service = FinanceService(test_session)
    device_id = "test-device-get-asset"
    
    # Create asset first
    asset_data = AssetCreate(
        name="Test Stock",
        category=AssetCategory.STOCK,
        amount=Decimal("10000.00"),
        currency=Currency.USD,
        purchase_date=date(2024, 1, 20)
    )
    
    asset_id = await service.create_asset(device_id, asset_data)
    
    # Get asset by ID
    asset = await service.get_asset_by_id(asset_id, device_id)
    assert asset.id == asset_id
    assert asset.name == "Test Stock"
    assert asset.category == "stock"
    assert asset.amount == Decimal("10000.00")


@pytest.mark.asyncio
async def test_get_asset_not_found(test_session: AsyncSession):
    """Test getting non-existent asset."""
    service = FinanceService(test_session)
    device_id = "test-device-not-found"
    fake_id = uuid.uuid4()
    
    with pytest.raises(AssetNotFoundError):
        await service.get_asset_by_id(fake_id, device_id)


@pytest.mark.asyncio
async def test_get_assets_grouped_by_category(test_session: AsyncSession):
    """Test getting assets grouped by category."""
    service = FinanceService(test_session)
    device_id = "test-device-grouped"
    
    # Create assets in different categories
    assets_data = [
        AssetCreate(
            name="Cash Account",
            category=AssetCategory.CASH,
            amount=Decimal("5000.00"),
            currency=Currency.USD,
            purchase_date=date(2024, 1, 1)
        ),
        AssetCreate(
            name="Stock Investment",
            category=AssetCategory.STOCK,
            amount=Decimal("15000.00"),
            currency=Currency.USD,
            purchase_date=date(2024, 1, 15)
        ),
        AssetCreate(
            name="Another Cash",
            category=AssetCategory.CASH,
            amount=Decimal("3000.00"),
            currency=Currency.EUR,
            purchase_date=date(2024, 1, 20)
        )
    ]
    
    for asset_data in assets_data:
        await service.create_asset(device_id, asset_data)
    
    # Get grouped assets
    grouped = await service.get_assets_grouped_by_category(device_id)
    
    assert "cash" in grouped
    assert "stock" in grouped
    assert len(grouped["cash"]) == 2
    assert len(grouped["stock"]) == 1
    
    # Check asset details
    cash_names = {asset.name for asset in grouped["cash"]}
    assert cash_names == {"Cash Account", "Another Cash"}


@pytest.mark.asyncio
async def test_update_asset(test_session: AsyncSession):
    """Test updating an asset."""
    service = FinanceService(test_session)
    device_id = "test-device-update"
    
    # Create asset
    asset_data = AssetCreate(
        name="Original Name",
        category=AssetCategory.CRYPTO,
        amount=Decimal("2000.00"),
        currency=Currency.USD,
        purchase_date=date(2024, 1, 10),
        notes="Original notes"
    )
    
    asset_id = await service.create_asset(device_id, asset_data)
    
    # Update asset
    update_data = AssetUpdate(
        name="Updated Name",
        amount=Decimal("2500.00"),
        notes="Updated notes"
    )
    
    await service.update_asset(asset_id, device_id, update_data)
    
    # Verify update
    updated_asset = await service.get_asset_by_id(asset_id, device_id)
    assert updated_asset.name == "Updated Name"
    assert updated_asset.amount == Decimal("2500.00")
    assert updated_asset.notes == "Updated notes"
    assert updated_asset.category == "crypto"  # Should remain unchanged
    assert updated_asset.currency == "USD"  # Should remain unchanged


@pytest.mark.asyncio
async def test_update_nonexistent_asset(test_session: AsyncSession):
    """Test updating non-existent asset."""
    service = FinanceService(test_session)
    device_id = "test-device-update-notfound"
    fake_id = uuid.uuid4()
    
    update_data = AssetUpdate(name="New Name")
    
    with pytest.raises(AssetNotFoundError):
        await service.update_asset(fake_id, device_id, update_data)


@pytest.mark.asyncio
async def test_delete_asset(test_session: AsyncSession):
    """Test deleting an asset."""
    service = FinanceService(test_session)
    device_id = "test-device-delete"
    
    # Create asset
    asset_data = AssetCreate(
        name="To Be Deleted",
        category=AssetCategory.REAL_ESTATE,
        amount=Decimal("300000.00"),
        currency=Currency.USD,
        purchase_date=date(2024, 1, 1)
    )
    
    asset_id = await service.create_asset(device_id, asset_data)
    
    # Verify asset exists
    asset = await service.get_asset_by_id(asset_id, device_id)
    assert asset.name == "To Be Deleted"
    
    # Delete asset
    await service.delete_asset(asset_id, device_id)
    
    # Verify asset is deleted
    with pytest.raises(AssetNotFoundError):
        await service.get_asset_by_id(asset_id, device_id)


@pytest.mark.asyncio
async def test_delete_nonexistent_asset(test_session: AsyncSession):
    """Test deleting non-existent asset."""
    service = FinanceService(test_session)
    device_id = "test-device-delete-notfound"
    fake_id = uuid.uuid4()
    
    with pytest.raises(AssetNotFoundError):
        await service.delete_asset(fake_id, device_id)


@pytest.mark.asyncio
async def test_get_portfolio_summary(test_session: AsyncSession):
    """Test portfolio summary calculation."""
    service = FinanceService(test_session)
    device_id = "test-device-portfolio"
    
    # Create assets in different categories
    assets_data = [
        AssetCreate(
            name="Savings",
            category=AssetCategory.CASH,
            amount=Decimal("10000.00"),
            currency=Currency.USD,
            purchase_date=date(2024, 1, 1)
        ),
        AssetCreate(
            name="Checking",
            category=AssetCategory.CASH,
            amount=Decimal("5000.00"),
            currency=Currency.USD,
            purchase_date=date(2024, 1, 1)
        ),
        AssetCreate(
            name="Apple Stock",
            category=AssetCategory.STOCK,
            amount=Decimal("20000.00"),
            currency=Currency.USD,
            purchase_date=date(2024, 1, 15)
        ),
        AssetCreate(
            name="Bitcoin",
            category=AssetCategory.CRYPTO,
            amount=Decimal("8000.00"),
            currency=Currency.USD,
            purchase_date=date(2024, 1, 20)
        )
    ]
    
    for asset_data in assets_data:
        await service.create_asset(device_id, asset_data)
    
    # Get portfolio summary
    summary = await service.get_portfolio_summary(device_id, "USD")
    
    assert summary.base_currency == "USD"
    assert "cash" in summary.asset_breakdown
    assert "stock" in summary.asset_breakdown
    assert "crypto" in summary.asset_breakdown
    
    # Check breakdown
    cash_breakdown = summary.asset_breakdown["cash"]
    stock_breakdown = summary.asset_breakdown["stock"]
    crypto_breakdown = summary.asset_breakdown["crypto"]
    
    assert cash_breakdown.total_amount == Decimal("15000.00")  # 10000 + 5000
    assert cash_breakdown.count == 2
    assert stock_breakdown.total_amount == Decimal("20000.00")
    assert stock_breakdown.count == 1
    assert crypto_breakdown.total_amount == Decimal("8000.00")
    assert crypto_breakdown.count == 1


@pytest.mark.asyncio
async def test_get_currencies(test_session: AsyncSession):
    """Test getting supported currencies."""
    service = FinanceService(test_session)
    
    currencies = await service.get_currencies()
    
    assert len(currencies) > 0
    assert all("code" in currency for currency in currencies)
    assert all("name" in currency for currency in currencies)
    assert all("symbol" in currency for currency in currencies)
    
    # Check for specific currencies
    codes = {currency["code"] for currency in currencies}
    assert "USD" in codes
    assert "EUR" in codes
    assert "CNY" in codes


@pytest.mark.asyncio
async def test_get_asset_categories(test_session: AsyncSession):
    """Test getting asset categories."""
    service = FinanceService(test_session)
    
    categories = await service.get_asset_categories()
    
    assert len(categories) > 0
    assert "cash" in categories
    assert "stock" in categories
    assert "crypto" in categories
    assert "real_estate" in categories


@pytest.mark.asyncio
async def test_ensure_default_asset_types(test_session: AsyncSession):
    """Test ensuring default asset types exist."""
    service = FinanceService(test_session)
    
    # Should create default asset types
    await service.ensure_default_asset_types()
    
    # Verify asset types were created
    from sqlalchemy import select
    result = await test_session.execute(select(AssetType))
    asset_types = result.scalars().all()
    
    assert len(asset_types) >= 5  # At least the default ones
    categories = {at.category for at in asset_types}
    assert "cash" in categories
    assert "stock" in categories
    assert "crypto" in categories
    assert "real_estate" in categories
    assert "other" in categories


@pytest.mark.asyncio
async def test_user_isolation(test_session: AsyncSession):
    """Test that users can only access their own assets."""
    service = FinanceService(test_session)
    device_id1 = "test-device-user1"
    device_id2 = "test-device-user2"
    
    # Create asset for user 1
    asset_data1 = AssetCreate(
        name="User 1 Asset",
        category=AssetCategory.CASH,
        amount=Decimal("1000.00"),
        currency=Currency.USD,
        purchase_date=date(2024, 1, 1)
    )
    asset_id1 = await service.create_asset(device_id1, asset_data1)
    
    # Create asset for user 2
    asset_data2 = AssetCreate(
        name="User 2 Asset",
        category=AssetCategory.CASH,
        amount=Decimal("2000.00"),
        currency=Currency.USD,
        purchase_date=date(2024, 1, 1)
    )
    asset_id2 = await service.create_asset(device_id2, asset_data2)
    
    # User 1 can access their asset
    asset1 = await service.get_asset_by_id(asset_id1, device_id1)
    assert asset1.name == "User 1 Asset"
    
    # User 2 can access their asset
    asset2 = await service.get_asset_by_id(asset_id2, device_id2)
    assert asset2.name == "User 2 Asset"
    
    # User 1 cannot access user 2's asset
    with pytest.raises(AssetNotFoundError):
        await service.get_asset_by_id(asset_id2, device_id1)
    
    # User 2 cannot access user 1's asset
    with pytest.raises(AssetNotFoundError):
        await service.get_asset_by_id(asset_id1, device_id2)