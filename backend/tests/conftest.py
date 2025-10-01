"""Test configuration and fixtures."""

import asyncio
import uuid
from decimal import Decimal
from datetime import date
from typing import AsyncGenerator, Dict, Any
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
from httpx import AsyncClient

from app.models.base import Base
from app.core.database import get_db_session
from app.main import app
from app.services.finance_service import FinanceService
from app.models.schemas import AssetCreate, CreditCreate, AssetCategory, CreditCategory, Currency

# Import all models to ensure they're registered with Base
from app.models import User, Asset, AssetType, Credit, CreditType


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine for each test function."""
    test_db_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
        future=True,
    )
    
    # Enable foreign key support for SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    
    # Override the database dependency
    def override_get_db_session():
        yield test_session
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    finally:
        # Clean up
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def service(test_session: AsyncSession) -> FinanceService:
    """Create a finance service instance."""
    return FinanceService(test_session)


# Test data factories
class TestDataFactory:
    """Factory for creating consistent test data."""
    
    @staticmethod
    def asset_data(
        name: str = "Test Asset",
        category: AssetCategory = AssetCategory.CASH,
        amount: Decimal = Decimal("1000.00"),
        currency: Currency = Currency.USD,
        **kwargs
    ) -> Dict[str, Any]:
        """Create asset test data."""
        data = {
            "name": name,
            "category": category,
            "amount": str(amount),
            "currency": currency,
            "purchase_date": "2024-01-15",
        }
        data.update(kwargs)
        return data
    
    @staticmethod
    def credit_data(
        name: str = "Test Credit",
        category: CreditCategory = CreditCategory.CREDIT_CARD,
        amount: Decimal = Decimal("500.00"),
        currency: Currency = Currency.USD,
        **kwargs
    ) -> Dict[str, Any]:
        """Create credit test data."""
        data = {
            "name": name,
            "category": category,
            "amount": str(amount),
            "currency": currency,
            "issue_date": "2024-01-15",
        }
        data.update(kwargs)
        return data
    
    @staticmethod
    def stock_asset_data(
        name: str = "Apple Inc.",
        symbol: str = "AAPL",
        shares: float = 100.0,
        amount: Decimal = Decimal("15000.00"),
        **kwargs
    ) -> Dict[str, Any]:
        """Create stock asset test data."""
        return TestDataFactory.asset_data(
            name=name,
            category=AssetCategory.STOCK,
            amount=amount,
            symbol=symbol,
            shares=shares,
            **kwargs
        )


@pytest.fixture
def factory() -> TestDataFactory:
    """Provide test data factory."""
    return TestDataFactory


@pytest_asyncio.fixture
async def sample_data(service: FinanceService, factory: TestDataFactory):
    """Create sample data for testing."""
    device_id = "sample-device"
    
    # Create assets
    asset_data = [
        factory.asset_data("USD Cash", AssetCategory.CASH, Decimal("5000.00"), Currency.USD),
        factory.asset_data("EUR Cash", AssetCategory.CASH, Decimal("3000.00"), Currency.EUR),
        factory.stock_asset_data("Apple Stock", "AAPL", 50.0, Decimal("7500.00")),
        factory.asset_data("Bitcoin", AssetCategory.CRYPTO, Decimal("25000.00"), Currency.USD),
    ]
    
    # Create credits
    credit_data = [
        factory.credit_data("Visa Card", CreditCategory.CREDIT_CARD, Decimal("2000.00"), Currency.USD),
        factory.credit_data("Car Loan", CreditCategory.LOAN, Decimal("15000.00"), Currency.USD),
        factory.credit_data("EUR Card", CreditCategory.CREDIT_CARD, Decimal("1000.00"), Currency.EUR),
    ]
    
    # Create in service
    asset_ids = []
    for data in asset_data:
        asset_create = AssetCreate(**data)
        asset_id = await service.create_asset(device_id, asset_create)
        asset_ids.append(asset_id)
    
    credit_ids = []
    for data in credit_data:
        credit_create = CreditCreate(**data)
        credit_id = await service.create_credit(device_id, credit_create)
        credit_ids.append(credit_id)
    
    return {
        "device_id": device_id,
        "asset_ids": asset_ids,
        "credit_ids": credit_ids,
        "assets": asset_data,
        "credits": credit_data,
    }