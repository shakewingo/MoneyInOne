"""Test database models for simplified finance app."""

import pytest
import uuid
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.asset import Asset, AssetType


@pytest.mark.asyncio
async def test_user_model(test_session: AsyncSession):
    """Test User model basic operations."""
    # Create user
    user = User(device_id="test-device-123")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    # Test user attributes
    assert user.id is not None
    assert user.device_id == "test-device-123"
    assert user.created_at is not None
    assert user.updated_at is not None
    assert isinstance(user.id, uuid.UUID)


@pytest.mark.asyncio
async def test_asset_type_model(test_session: AsyncSession):
    """Test AssetType model basic operations."""
    # Create asset type
    asset_type = AssetType(
        name="Cash",
        category="cash",
        is_default=True
    )
    test_session.add(asset_type)
    await test_session.commit()
    await test_session.refresh(asset_type)
    
    # Test asset type attributes
    assert asset_type.id is not None
    assert asset_type.name == "Cash"
    assert asset_type.category == "cash"
    assert asset_type.is_default is True
    assert asset_type.created_at is not None
    assert asset_type.updated_at is not None


@pytest.mark.asyncio
async def test_asset_model(test_session: AsyncSession):
    """Test Asset model basic operations."""
    # Create user and asset type first
    user = User(device_id="test-device-456")
    test_session.add(user)
    
    asset_type = AssetType(
        name="Stock",
        category="stock",
        is_default=True
    )
    test_session.add(asset_type)
    await test_session.commit()
    await test_session.refresh(user)
    await test_session.refresh(asset_type)
    
    # Create asset
    asset = Asset(
        user_id=user.id,
        asset_type_id=asset_type.id,
        name="Apple Inc.",
        category="stock",
        amount=Decimal("15000.00"),
        currency="USD",
        purchase_date=date(2024, 1, 15),
        notes="Technology stock investment"
    )
    test_session.add(asset)
    await test_session.commit()
    await test_session.refresh(asset)
    
    # Test asset attributes
    assert asset.id is not None
    assert asset.user_id == user.id
    assert asset.asset_type_id == asset_type.id
    assert asset.name == "Apple Inc."
    assert asset.category == "stock"
    assert asset.amount == Decimal("15000.00")
    assert asset.currency == "USD"
    assert asset.purchase_date == date(2024, 1, 15)
    assert asset.notes == "Technology stock investment"
    assert asset.created_at is not None
    assert asset.updated_at is not None


@pytest.mark.asyncio
async def test_asset_relationships(test_session: AsyncSession):
    """Test relationships between models."""
    # Create user and asset type
    user = User(device_id="test-device-relationships")
    test_session.add(user)
    
    asset_type = AssetType(
        name="Cryptocurrency",
        category="crypto",
        is_default=True
    )
    test_session.add(asset_type)
    await test_session.commit()
    await test_session.refresh(user)
    await test_session.refresh(asset_type)
    
    # Create multiple assets
    assets = [
        Asset(
            user_id=user.id,
            asset_type_id=asset_type.id,
            name="Bitcoin",
            category="crypto",
            amount=Decimal("50000.00"),
            currency="USD",
            purchase_date=date(2024, 1, 1)
        ),
        Asset(
            user_id=user.id,
            asset_type_id=asset_type.id,
            name="Ethereum",
            category="crypto",
            amount=Decimal("30000.00"),
            currency="USD",
            purchase_date=date(2024, 1, 15)
        )
    ]
    
    for asset in assets:
        test_session.add(asset)
    await test_session.commit()
    
    # Test user -> assets relationship
    await test_session.refresh(user, ["assets"])
    assert len(user.assets) == 2
    asset_names = {asset.name for asset in user.assets}
    assert asset_names == {"Bitcoin", "Ethereum"}
    
    # Test asset_type -> assets relationship
    await test_session.refresh(asset_type, ["assets"])
    assert len(asset_type.assets) == 2


@pytest.mark.asyncio
async def test_asset_validation(test_session: AsyncSession):
    """Test asset model validation."""
    # Create user and asset type
    user = User(device_id="test-device-validation")
    test_session.add(user)
    
    asset_type = AssetType(
        name="Cash",
        category="cash",
        is_default=True
    )
    test_session.add(asset_type)
    await test_session.commit()
    await test_session.refresh(user)
    await test_session.refresh(asset_type)
    
    # Test valid asset
    valid_asset = Asset(
        user_id=user.id,
        asset_type_id=asset_type.id,
        name="Savings Account",
        category="cash",
        amount=Decimal("1000.00"),
        currency="USD",
        purchase_date=date(2024, 1, 1)
    )
    test_session.add(valid_asset)
    await test_session.commit()
    await test_session.refresh(valid_asset)
    
    assert valid_asset.id is not None


@pytest.mark.asyncio
async def test_multiple_users_assets(test_session: AsyncSession):
    """Test that assets are properly isolated by user."""
    # Create two users
    user1 = User(device_id="test-device-user1")
    user2 = User(device_id="test-device-user2")
    test_session.add(user1)
    test_session.add(user2)
    
    # Create asset type
    asset_type = AssetType(
        name="Cash",
        category="cash",
        is_default=True
    )
    test_session.add(asset_type)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)
    await test_session.refresh(asset_type)
    
    # Create assets for each user
    asset1 = Asset(
        user_id=user1.id,
        asset_type_id=asset_type.id,
        name="User 1 Cash",
        category="cash",
        amount=Decimal("1000.00"),
        currency="USD",
        purchase_date=date(2024, 1, 1)
    )
    
    asset2 = Asset(
        user_id=user2.id,
        asset_type_id=asset_type.id,
        name="User 2 Cash",
        category="cash",
        amount=Decimal("2000.00"),
        currency="EUR",
        purchase_date=date(2024, 1, 1)
    )
    
    test_session.add(asset1)
    test_session.add(asset2)
    await test_session.commit()
    
    # Test user isolation
    await test_session.refresh(user1, ["assets"])
    await test_session.refresh(user2, ["assets"])
    
    assert len(user1.assets) == 1
    assert len(user2.assets) == 1
    assert user1.assets[0].name == "User 1 Cash"
    assert user2.assets[0].name == "User 2 Cash"
    assert user1.assets[0].currency == "USD"
    assert user2.assets[0].currency == "EUR"


@pytest.mark.asyncio
async def test_asset_string_representation(test_session: AsyncSession):
    """Test string representation of models."""
    # Create user and asset type
    user = User(device_id="test-device-repr")
    test_session.add(user)
    
    asset_type = AssetType(
        name="Real Estate",
        category="real_estate",
        is_default=True
    )
    test_session.add(asset_type)
    await test_session.commit()
    await test_session.refresh(user)
    await test_session.refresh(asset_type)
    
    # Create asset
    asset = Asset(
        user_id=user.id,
        asset_type_id=asset_type.id,
        name="Family Home",
        category="real_estate",
        amount=Decimal("500000.00"),
        currency="USD",
        purchase_date=date(2024, 1, 1)
    )
    test_session.add(asset)
    await test_session.commit()
    await test_session.refresh(asset)
    
    # Test string representations
    assert "AssetType" in str(asset_type)
    assert "Real Estate" in str(asset_type)
    assert "real_estate" in str(asset_type)
    
    assert "Asset" in str(asset)
    assert "Family Home" in str(asset)
    assert "real_estate" in str(asset)
    assert "500000.00" in str(asset)


@pytest.mark.asyncio
async def test_decimal_precision(test_session: AsyncSession):
    """Test decimal precision for financial amounts."""
    # Create user and asset type
    user = User(device_id="test-device-decimal")
    test_session.add(user)
    
    asset_type = AssetType(
        name="Cash",
        category="cash",
        is_default=True
    )
    test_session.add(asset_type)
    await test_session.commit()
    await test_session.refresh(user)
    await test_session.refresh(asset_type)
    
    # Create asset with precise decimal amount
    precise_amount = Decimal("1234.5678")
    asset = Asset(
        user_id=user.id,
        asset_type_id=asset_type.id,
        name="Precise Cash",
        category="cash",
        amount=precise_amount,
        currency="USD",
        purchase_date=date(2024, 1, 1)
    )
    test_session.add(asset)
    await test_session.commit()
    await test_session.refresh(asset)
    
    # Test precision is maintained
    assert asset.amount == precise_amount
    assert str(asset.amount) == "1234.5678"