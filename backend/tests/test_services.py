"""Test service layer functionality."""

import pytest
from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.asset import Asset, AssetType
from app.models.schemas import AssetCreate, AssetUpdate
from app.services.asset_service import AssetService
from app.services.exceptions import NotFoundError


class TestAssetService:
    """Test AssetService functionality."""
    
    @pytest.mark.asyncio
    async def test_create_and_get_asset(self, test_session: AsyncSession):
        """Test creating and retrieving an asset."""
        service = AssetService(test_session)
        
        # Create test user
        user = User(device_id="test-device-123")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create test asset type
        asset_type = AssetType(
            name="Stock",
            category="stock",
            is_default=True
        )
        test_session.add(asset_type)
        await test_session.commit()
        await test_session.refresh(asset_type)
        
        # Create asset
        asset_data = AssetCreate(
            asset_type_id=asset_type.id,
            name="Apple Inc.",
            symbol="AAPL",
            quantity=Decimal("10.0"),
            purchase_price=Decimal("150.00"),
            purchase_currency="USD",
            purchase_date=date(2024, 1, 15),
            tags=["tech", "dividend"]
        )
        
        created_asset = await service.create_asset(asset_data, user.id)
        
        assert created_asset.name == "Apple Inc."
        assert created_asset.symbol == "AAPL"
        assert created_asset.quantity == Decimal("10.0")
        assert created_asset.purchase_price == Decimal("150.00")
        assert created_asset.tags == ["tech", "dividend"]
        
        # Retrieve asset
        retrieved_asset = await service.get_asset_by_id(created_asset.id, user.id)
        assert retrieved_asset.id == created_asset.id
        assert retrieved_asset.name == "Apple Inc."
    
    @pytest.mark.asyncio
    async def test_get_assets_pagination(self, test_session: AsyncSession):
        """Test getting assets with pagination."""
        service = AssetService(test_session)
        
        # Create test user
        user = User(device_id="test-device-456")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create test asset type
        asset_type = AssetType(name="Crypto", category="crypto")
        test_session.add(asset_type)
        await test_session.commit()
        await test_session.refresh(asset_type)
        
        # Create multiple assets
        for i in range(5):
            asset = Asset(
                user_id=user.id,
                asset_type_id=asset_type.id,
                name=f"Asset {i}",
                symbol=f"SYM{i}",
                quantity=Decimal("1.0"),
                purchase_price=Decimal("100.00"),
                purchase_currency="USD",
                purchase_date=date.today()
            )
            test_session.add(asset)
        
        await test_session.commit()
        
        # Test pagination
        assets, total_count = await service.get_assets(user.id, skip=0, limit=3)
        
        assert len(assets) == 3
        assert total_count == 5
    
    @pytest.mark.asyncio
    async def test_update_asset(self, test_session: AsyncSession):
        """Test updating an asset."""
        service = AssetService(test_session)
        
        # Create test data
        user = User(device_id="test-device-789")
        test_session.add(user)
        
        asset_type = AssetType(name="Bond", category="bond")
        test_session.add(asset_type)
        
        await test_session.commit()
        await test_session.refresh(user)
        await test_session.refresh(asset_type)
        
        # Create asset
        asset_data = AssetCreate(
            asset_type_id=asset_type.id,
            name="US Treasury",
            quantity=Decimal("1000.0"),
            purchase_price=Decimal("100.00"),
            purchase_currency="USD",
            purchase_date=date.today()
        )
        
        created_asset = await service.create_asset(asset_data, user.id)
        
        # Update asset
        update_data = AssetUpdate(
            name="US Treasury Bond",
            quantity=Decimal("2000.0"),
            tags=["government", "safe"]
        )
        
        updated_asset = await service.update_asset(created_asset.id, update_data, user.id)
        
        assert updated_asset.name == "US Treasury Bond"
        assert updated_asset.quantity == Decimal("2000.0")
        assert updated_asset.tags == ["government", "safe"]
    
    @pytest.mark.asyncio
    async def test_delete_asset(self, test_session: AsyncSession):
        """Test deleting an asset."""
        service = AssetService(test_session)
        
        # Create test data
        user = User(device_id="test-device-delete")
        asset_type = AssetType(name="Test Type", category="test")
        test_session.add(user)
        test_session.add(asset_type)
        await test_session.commit()
        await test_session.refresh(user)
        await test_session.refresh(asset_type)
        
        # Create asset
        asset_data = AssetCreate(
            asset_type_id=asset_type.id,
            name="To Delete",
            quantity=Decimal("1.0"),
            purchase_price=Decimal("100.00"),
            purchase_currency="USD",
            purchase_date=date.today()
        )
        
        created_asset = await service.create_asset(asset_data, user.id)
        asset_id = created_asset.id
        
        # Delete asset
        await service.delete_asset(asset_id, user.id)
        
        # Verify deletion
        with pytest.raises(NotFoundError):
            await service.get_asset_by_id(asset_id, user.id)
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_asset(self, test_session: AsyncSession):
        """Test getting a non-existent asset raises NotFoundError."""
        service = AssetService(test_session)
        
        fake_asset_id = uuid4()
        fake_user_id = uuid4()
        
        with pytest.raises(NotFoundError):
            await service.get_asset_by_id(fake_asset_id, fake_user_id)
