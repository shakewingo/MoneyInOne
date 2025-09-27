"""Test database models."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from app.models.user import User
from app.models.asset import Asset, AssetType
from app.models.price import AssetPrice, ExchangeRate


class TestUserModel:
    """Test User model."""
    
    def test_user_creation(self):
        """Test creating a user instance."""
        user = User(device_id="test-device-123")
        
        assert user.device_id == "test-device-123"
    
    def test_user_repr(self):
        """Test user string representation."""
        user = User(device_id="test-device-123")
        repr_str = repr(user)
        
        assert "User" in repr_str
        assert "test-device-123" in repr_str


class TestAssetTypeModel:
    """Test AssetType model."""
    
    def test_asset_type_creation(self):
        """Test creating an asset type instance."""
        asset_type = AssetType(
            name="Stock",
            category="stock",
            is_default=True,
            attributes={"required_fields": ["symbol"]}
        )
        
        assert asset_type.name == "Stock"
        assert asset_type.category == "stock"
        assert asset_type.is_default is True
        assert asset_type.attributes == {"required_fields": ["symbol"]}
    
    def test_asset_type_repr(self):
        """Test asset type string representation."""
        asset_type = AssetType(name="Stock", category="stock")
        repr_str = repr(asset_type)
        
        assert "AssetType" in repr_str
        assert "Stock" in repr_str
        assert "stock" in repr_str


class TestAssetModel:
    """Test Asset model."""
    
    def test_asset_creation(self):
        """Test creating an asset instance."""
        user_id = uuid4()
        asset_type_id = uuid4()
        
        asset = Asset(
            user_id=user_id,
            asset_type_id=asset_type_id,
            name="Apple Inc.",
            symbol="AAPL",
            quantity=Decimal("10.0"),
            purchase_price=Decimal("150.00"),
            purchase_currency="USD",
            purchase_date=date(2024, 1, 15),
            attributes={"shares": 10},
            tags=["tech", "dividend"]
        )
        
        assert asset.name == "Apple Inc."
        assert asset.symbol == "AAPL"
        assert asset.quantity == Decimal("10.0")
        assert asset.purchase_price == Decimal("150.00")
        assert asset.purchase_currency == "USD"
        assert asset.purchase_date == date(2024, 1, 15)
        assert asset.attributes == {"shares": 10}
        assert asset.tags == ["tech", "dividend"]
    
    def test_total_cost_calculation(self):
        """Test total cost property calculation."""
        asset = Asset(
            user_id=uuid4(),
            asset_type_id=uuid4(),
            name="Test Asset",
            quantity=Decimal("5.0"),
            purchase_price=Decimal("100.00"),
            purchase_currency="USD",
            purchase_date=date.today()
        )
        
        assert asset.total_cost == Decimal("500.00")
    
    def test_asset_repr(self):
        """Test asset string representation."""
        asset = Asset(
            user_id=uuid4(),
            asset_type_id=uuid4(),
            name="Apple Inc.",
            symbol="AAPL",
            quantity=Decimal("10.0"),
            purchase_price=Decimal("150.00"),
            purchase_currency="USD",
            purchase_date=date.today()
        )
        repr_str = repr(asset)
        
        assert "Asset" in repr_str
        assert "Apple Inc." in repr_str
        assert "AAPL" in repr_str
        assert "10.0" in repr_str


class TestAssetPriceModel:
    """Test AssetPrice model."""
    
    def test_asset_price_creation(self):
        """Test creating an asset price instance."""
        price = AssetPrice(
            symbol="AAPL",
            asset_type="stock",
            price=Decimal("180.00"),
            currency="USD",
            source="yahoo_finance",
            change_24h=Decimal("2.5"),
            fetched_at=datetime.utcnow()
        )
        
        assert price.symbol == "AAPL"
        assert price.asset_type == "stock"
        assert price.price == Decimal("180.00")
        assert price.currency == "USD"
        assert price.source == "yahoo_finance"
        assert price.change_24h == Decimal("2.5")
    
    def test_asset_price_repr(self):
        """Test asset price string representation."""
        price = AssetPrice(
            symbol="AAPL",
            asset_type="stock",
            price=Decimal("180.00"),
            currency="USD",
            source="yahoo_finance",
            fetched_at=datetime.utcnow()
        )
        repr_str = repr(price)
        
        assert "AssetPrice" in repr_str
        assert "AAPL" in repr_str
        assert "180.00" in repr_str
        assert "USD" in repr_str


class TestExchangeRateModel:
    """Test ExchangeRate model."""
    
    def test_exchange_rate_creation(self):
        """Test creating an exchange rate instance."""
        rate = ExchangeRate(
            from_currency="USD",
            to_currency="CNY",
            rate=Decimal("7.20"),
            source="exchangerate-api",
            fetched_at=datetime.utcnow()
        )
        
        assert rate.from_currency == "USD"
        assert rate.to_currency == "CNY"
        assert rate.rate == Decimal("7.20")
        assert rate.source == "exchangerate-api"
    
    def test_exchange_rate_repr(self):
        """Test exchange rate string representation."""
        rate = ExchangeRate(
            from_currency="USD",
            to_currency="CNY",
            rate=Decimal("7.20"),
            source="exchangerate-api",
            fetched_at=datetime.utcnow()
        )
        repr_str = repr(rate)
        
        assert "ExchangeRate" in repr_str
        assert "USD/CNY" in repr_str
        assert "7.20" in repr_str
