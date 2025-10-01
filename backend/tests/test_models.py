"""Comprehensive model tests for MoneyInOne finance app."""

import pytest
import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.asset import Asset, AssetType
from app.models.credit import Credit, CreditType


class TestModels:
    """Test suite for all database models."""
    
    @pytest.mark.asyncio
    async def test_model_creation_and_relationships(self, test_session: AsyncSession):
        """Test comprehensive model creation with relationships."""
        # Create user
        user = User(device_id="test-comprehensive")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create types
        asset_type = AssetType(name="Stock", category="stock", is_default=True)
        credit_type = CreditType(name="Credit Card", category="credit_card", is_default=True)
        test_session.add_all([asset_type, credit_type])
        await test_session.commit()
        await test_session.refresh(asset_type)
        await test_session.refresh(credit_type)
        
        # Create asset with stock fields
        asset = Asset(
            user_id=user.id,
            asset_type_id=asset_type.id,
            name="Apple Inc.",
            category="stock",
            amount=Decimal("15000.00"),
            currency="USD",
            purchase_date=date(2024, 1, 15),
            notes="Tech investment",
            symbol="AAPL",
            shares=100.0
        )
        
        # Create credit
        credit = Credit(
            user_id=user.id,
            credit_type_id=credit_type.id,
            name="Visa Card",
            category="credit_card",
            amount=Decimal("2500.00"),
            currency="USD",
            issue_date=date(2024, 1, 15),
            notes="Main card"
        )
        
        test_session.add_all([asset, credit])
        await test_session.commit()
        await test_session.refresh(asset)
        await test_session.refresh(credit)
        
        # Test all model attributes
        self._verify_user_model(user)
        self._verify_asset_model(asset, asset_type)
        self._verify_credit_model(credit, credit_type)
        self._verify_type_models(asset_type, credit_type)
        
        # Test relationships
        await test_session.refresh(user, ["assets", "credits"])
        assert len(user.assets) == 1
        assert len(user.credits) == 1
        assert user.assets[0].symbol == "AAPL"
        assert user.credits[0].name == "Visa Card"
    
    @pytest.mark.asyncio
    async def test_multi_user_isolation(self, test_session: AsyncSession):
        """Test data isolation between users."""
        # Create users and types
        users = [User(device_id=f"user-{i}") for i in range(2)]
        asset_type = AssetType(name="Cash", category="cash", is_default=True)
        credit_type = CreditType(name="Loan", category="loan", is_default=True)
        
        test_session.add_all(users + [asset_type, credit_type])
        await test_session.commit()
        
        # Create data for each user
        for i, user in enumerate(users):
            await test_session.refresh(user)
            asset = Asset(
                user_id=user.id, asset_type_id=asset_type.id,
                name=f"User{i} Asset", category="cash",
                amount=Decimal(f"{(i+1)*1000}.00"), currency="USD",
                purchase_date=date(2024, 1, 1)
            )
            credit = Credit(
                user_id=user.id, credit_type_id=credit_type.id,
                name=f"User{i} Credit", category="loan",
                amount=Decimal(f"{(i+1)*500}.00"), currency="USD",
                issue_date=date(2024, 1, 1)
            )
            test_session.add_all([asset, credit])
        
        await test_session.commit()
        
        # Verify isolation
        for i, user in enumerate(users):
            await test_session.refresh(user, ["assets", "credits"])
            assert len(user.assets) == 1
            assert len(user.credits) == 1
            assert user.assets[0].name == f"User{i} Asset"
            assert user.assets[0].amount == Decimal(f"{(i+1)*1000}.00")
            assert user.credits[0].name == f"User{i} Credit"
    
    @pytest.mark.asyncio
    async def test_stock_specific_fields(self, test_session: AsyncSession):
        """Test stock-specific fields behavior."""
        user = User(device_id="test-stock-fields")
        stock_type = AssetType(name="Stock", category="stock", is_default=True)
        cash_type = AssetType(name="Cash", category="cash", is_default=True)
        
        test_session.add_all([user, stock_type, cash_type])
        await test_session.commit()
        await test_session.refresh(user)
        await test_session.refresh(stock_type)
        await test_session.refresh(cash_type)
        
        # Stock asset with symbol and shares
        stock_asset = Asset(
            user_id=user.id, asset_type_id=stock_type.id,
            name="Tesla Inc.", category="stock",
            amount=Decimal("50000.00"), currency="USD",
            purchase_date=date(2024, 2, 1),
            symbol="TSLA", shares=200.5
        )
        
        # Non-stock asset (should have None for stock fields)
        cash_asset = Asset(
            user_id=user.id, asset_type_id=cash_type.id,
            name="Savings", category="cash",
            amount=Decimal("10000.00"), currency="USD",
            purchase_date=date(2024, 2, 1)
        )
        
        test_session.add_all([stock_asset, cash_asset])
        await test_session.commit()
        await test_session.refresh(stock_asset)
        await test_session.refresh(cash_asset)
        
        # Verify stock fields
        assert stock_asset.symbol == "TSLA"
        assert stock_asset.shares == 200.5
        assert cash_asset.symbol is None
        assert cash_asset.shares is None
    
    def _verify_user_model(self, user: User):
        """Verify user model attributes."""
        assert isinstance(user.id, uuid.UUID)
        assert user.device_id.startswith("test-")
        assert user.created_at is not None
        assert user.updated_at is not None
        assert "User" in str(user)
    
    def _verify_asset_model(self, asset: Asset, asset_type: AssetType):
        """Verify asset model attributes."""
        assert isinstance(asset.id, uuid.UUID)
        assert asset.name == "Apple Inc."
        assert asset.category == "stock"
        assert asset.amount == Decimal("15000.00")
        assert asset.currency == "USD"
        assert asset.symbol == "AAPL"
        assert asset.shares == 100.0
        assert asset.notes == "Tech investment"
        assert asset.created_at is not None
        assert "Asset" in str(asset)
        assert "Apple Inc." in str(asset)
    
    def _verify_credit_model(self, credit: Credit, credit_type: CreditType):
        """Verify credit model attributes."""
        assert isinstance(credit.id, uuid.UUID)
        assert credit.name == "Visa Card"
        assert credit.category == "credit_card"
        assert credit.amount == Decimal("2500.00")
        assert credit.currency == "USD"
        assert credit.notes == "Main card"
        assert credit.created_at is not None
        assert "Credit" in str(credit)
        assert "Visa Card" in str(credit)
    
    def _verify_type_models(self, asset_type: AssetType, credit_type: CreditType):
        """Verify type model attributes."""
        assert asset_type.name == "Stock"
        assert asset_type.category == "stock"
        assert asset_type.is_default is True
        assert "AssetType" in str(asset_type)
        
        assert credit_type.name == "Credit Card"
        assert credit_type.category == "credit_card"
        assert credit_type.is_default is True
        assert "CreditType" in str(credit_type)


@pytest.mark.asyncio
async def test_model_precision_and_constraints(test_session: AsyncSession):
    """Test decimal precision and database constraints."""
    user = User(device_id="test-precision")
    asset_type = AssetType(name="Test", category="other", is_default=True)
    test_session.add_all([user, asset_type])
    await test_session.commit()
    await test_session.refresh(user)
    await test_session.refresh(asset_type)
    
    # Test high precision decimal
    precise_amount = Decimal("123456789.123456")
    asset = Asset(
        user_id=user.id, asset_type_id=asset_type.id,
        name="Precision Test", category="other",
        amount=precise_amount, currency="USD",
        purchase_date=date(2024, 1, 1)
    )
    
    test_session.add(asset)
    await test_session.commit()
    await test_session.refresh(asset)
    
    # Verify precision is maintained (limited by Numeric(15, 4))
    assert asset.amount == Decimal("123456789.1235")  # Rounded to 4 decimal places