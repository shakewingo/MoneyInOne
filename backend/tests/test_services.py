"""Comprehensive service layer tests for MoneyInOne finance app."""

import pytest
import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
import pydantic

from app.services.finance_service import FinanceService
from app.services.exceptions import AssetNotFoundError, CreditNotFoundError
from app.models.schemas import (
    AssetCreate, AssetUpdate, CreditCreate, CreditUpdate,
    AssetCategory, CreditCategory, Currency
)


class TestFinanceService:
    """Comprehensive test suite for FinanceService."""
    
    @pytest.mark.asyncio
    async def test_user_and_type_management(self, service: FinanceService):
        """Test user and type creation with idempotency."""
        device_id = "test-management"
        
        # Test idempotent operations
        user1 = await service._get_or_create_user(device_id)
        user2 = await service._get_or_create_user(device_id)
        assert user1.id == user2.id
        
        asset_type1 = await service._get_or_create_asset_type("stock")
        asset_type2 = await service._get_or_create_asset_type("stock")
        assert asset_type1.id == asset_type2.id
        assert asset_type1.name == "Stock"
        
        credit_type1 = await service._get_or_create_credit_type("mortgage")
        credit_type2 = await service._get_or_create_credit_type("mortgage")
        assert credit_type1.id == credit_type2.id
        assert credit_type1.name == "Mortgage"
    
    @pytest.mark.asyncio
    async def test_complete_asset_lifecycle(self, service: FinanceService, factory):
        """Test complete asset CRUD lifecycle with stock fields."""
        device_id = "test-asset-lifecycle"
        
        # CREATE with stock fields
        asset_data = AssetCreate(**factory.stock_asset_data(
            "Microsoft", "MSFT", 75.0, Decimal("22500.00")
        ))
        asset_id = await service.create_asset(device_id, asset_data)
        
        # READ and verify
        asset = await service.get_asset_by_id(asset_id, device_id)
        assert asset.name == "Microsoft"
        assert asset.symbol == "MSFT"
        assert asset.shares == 75.0
        assert asset.amount == Decimal("22500.00")
        
        # UPDATE
        update_data = AssetUpdate(
            name="Microsoft Corp",
            shares=100.0,
            amount=Decimal("30000.00")
        )
        await service.update_asset(asset_id, device_id, update_data)
        
        updated_asset = await service.get_asset_by_id(asset_id, device_id)
        assert updated_asset.name == "Microsoft Corp"
        assert updated_asset.shares == 100.0
        assert updated_asset.symbol == "MSFT"  # Unchanged
        
        # DELETE
        await service.delete_asset(asset_id, device_id)
        with pytest.raises(AssetNotFoundError):
            await service.get_asset_by_id(asset_id, device_id)
    
    @pytest.mark.asyncio
    async def test_complete_credit_lifecycle(self, service: FinanceService, factory):
        """Test complete credit CRUD lifecycle."""
        device_id = "test-credit-lifecycle"
        
        # CREATE
        credit_data = CreditCreate(**factory.credit_data(
            "Home Mortgage", CreditCategory.MORTGAGE, Decimal("250000.00")
        ))
        credit_id = await service.create_credit(device_id, credit_data)
        
        # READ and verify
        credit = await service.get_credit_by_id(credit_id, device_id)
        assert credit.name == "Home Mortgage"
        assert credit.category == "mortgage"
        assert credit.amount == Decimal("250000.00")
        
        # UPDATE
        update_data = CreditUpdate(amount=Decimal("240000.00"))
        await service.update_credit(credit_id, device_id, update_data)
        
        updated_credit = await service.get_credit_by_id(credit_id, device_id)
        assert updated_credit.amount == Decimal("240000.00")
        
        # DELETE
        await service.delete_credit(credit_id, device_id)
        with pytest.raises(CreditNotFoundError):
            await service.get_credit_by_id(credit_id, device_id)
    
    @pytest.mark.asyncio
    async def test_grouped_data_retrieval(self, service: FinanceService, sample_data):
        """Test grouped asset and credit retrieval."""
        device_id = sample_data["device_id"]
        
        # Test grouped assets
        grouped_assets = await service.get_assets_grouped_by_category(device_id)
        assert "cash" in grouped_assets
        assert "stock" in grouped_assets
        assert "crypto" in grouped_assets
        assert len(grouped_assets["cash"]) == 2  # USD + EUR
        assert len(grouped_assets["stock"]) == 1
        
        # Verify stock asset has symbol and shares
        stock_asset = grouped_assets["stock"][0]
        assert stock_asset.symbol == "AAPL"
        assert stock_asset.shares == 50.0
        
        # Test grouped credits
        grouped_credits = await service.get_credits_grouped_by_category(device_id)
        assert "credit_card" in grouped_credits
        assert "loan" in grouped_credits
        assert len(grouped_credits["credit_card"]) == 2  # USD + EUR
        assert len(grouped_credits["loan"]) == 1
    
    @pytest.mark.asyncio
    async def test_portfolio_summary_calculations(self, service: FinanceService, sample_data):
        """Test portfolio summary with complex calculations."""
        device_id = sample_data["device_id"]
        
        portfolio = await service.get_portfolio_summary(device_id)
        
        # Verify structure
        assert all(key in portfolio.__dict__ for key in [
            "asset_summary", "credit_summary", "net_summary", "base_currency"
        ])
        
        # Verify asset summary calculations
        asset_summary = portfolio.asset_summary
        assert asset_summary["cash"].count == 2
        assert asset_summary["stock"].count == 1
        assert asset_summary["crypto"].count == 1
        
        # Verify credit summary
        credit_summary = portfolio.credit_summary
        assert credit_summary["credit_card"].count == 2
        assert credit_summary["loan"].count == 1
        
        # Verify net calculations
        net_summary = portfolio.net_summary
        expected_usd_net = Decimal("5000") + Decimal("7500") + Decimal("25000") - Decimal("2000") - Decimal("15000")
        expected_eur_net = Decimal("3000") - Decimal("1000")
        
        assert net_summary["USD"] == expected_usd_net  # 20500
        assert net_summary["EUR"] == expected_eur_net  # 2000
    
    @pytest.mark.asyncio
    async def test_user_isolation_and_security(self, service: FinanceService, factory):
        """Test that users can only access their own data."""
        devices = ["user1-device", "user2-device"]
        asset_ids = []
        
        # Create assets for different users
        for i, device_id in enumerate(devices):
            asset_data = AssetCreate(**factory.asset_data(f"User{i+1} Asset"))
            asset_id = await service.create_asset(device_id, asset_data)
            asset_ids.append(asset_id)
        
        # Test access control - users can only access their own assets
        asset1 = await service.get_asset_by_id(asset_ids[0], devices[0])
        assert asset1.name == "User1 Asset"
        
        # User2 cannot access User1's asset
        with pytest.raises(AssetNotFoundError):
            await service.get_asset_by_id(asset_ids[0], devices[1])
        
        # User1 cannot access User2's asset
        with pytest.raises(AssetNotFoundError):
            await service.get_asset_by_id(asset_ids[1], devices[0])
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service: FinanceService):
        """Test comprehensive error handling."""
        device_id = "test-errors"
        fake_id = uuid.uuid4()
        
        # Test all not found scenarios
        with pytest.raises(AssetNotFoundError):
            await service.get_asset_by_id(fake_id, device_id)
        
        with pytest.raises(AssetNotFoundError):
            await service.update_asset(fake_id, device_id, AssetUpdate(name="Updated"))
        
        with pytest.raises(AssetNotFoundError):
            await service.delete_asset(fake_id, device_id)
        
        # Same for credits
        with pytest.raises(CreditNotFoundError):
            await service.get_credit_by_id(fake_id, device_id)
    
    @pytest.mark.asyncio
    async def test_metadata_operations(self, service: FinanceService):
        """Test metadata retrieval operations."""
        # Test currency metadata
        currencies = await service.get_currencies()
        assert len(currencies) > 0
        usd = next((c for c in currencies if c["code"] == "USD"), None)
        assert usd and usd["name"] == "US Dollar" and usd["symbol"] == "$"
        
        # Test category metadata
        asset_categories = await service.get_asset_categories()
        assert "cash" in asset_categories
        assert "stock" in asset_categories
        
        credit_categories = await service.get_credit_categories()
        assert "credit_card" in credit_categories
        assert "loan" in credit_categories
    
    @pytest.mark.asyncio
    async def test_default_types_initialization(self, service: FinanceService):
        """Test default asset and credit types creation."""
        await service.ensure_default_asset_types()
        await service.ensure_default_credit_types()
        
        # Verify default types exist
        stock_type = await service._get_or_create_asset_type("stock")
        assert stock_type.name == "Stock"
        assert stock_type.is_default is True
        
        card_type = await service._get_or_create_credit_type("credit_card")
        assert card_type.name == "Credit Card"
        assert card_type.is_default is True


class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_asset_schema_validation(self, factory):
        """Test comprehensive asset schema validation."""
        # Valid stock asset
        valid_stock = AssetCreate(**factory.stock_asset_data())
        assert valid_stock.symbol == "AAPL"
        assert valid_stock.shares == 100.0
        
        # Valid non-stock asset
        valid_cash = AssetCreate(**factory.asset_data())
        assert valid_cash.symbol is None
        assert valid_cash.shares is None
        
        # Test validation errors
        with pytest.raises(pydantic.ValidationError):
            AssetCreate(**factory.asset_data(amount="-100.00"))  # Negative amount
        
        with pytest.raises(pydantic.ValidationError):
            AssetCreate(**factory.stock_asset_data(shares=-10.0))  # Negative shares
    
    def test_credit_schema_validation(self, factory):
        """Test credit schema validation."""
        # Valid credit
        valid_credit = CreditCreate(**factory.credit_data())
        assert valid_credit.category == CreditCategory.CREDIT_CARD
        
        # Test validation errors
        with pytest.raises(pydantic.ValidationError):
            CreditCreate(**factory.credit_data(amount="-500.00"))  # Negative amount
    
    def test_update_schema_validation(self):
        """Test update schema validation."""
        # Valid partial update
        update = AssetUpdate(name="Updated Name", shares=150.0)
        assert update.name == "Updated Name"
        assert update.shares == 150.0
        assert update.symbol is None  # Not provided
        
        # Invalid update
        with pytest.raises(pydantic.ValidationError):
            AssetUpdate(shares=-50.0)  # Negative shares