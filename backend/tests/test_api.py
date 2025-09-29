"""Test API endpoints for simplified finance app."""

import pytest
import uuid
from decimal import Decimal
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import AssetType


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_detailed_health_check(client: AsyncClient):
    """Test detailed health check endpoint."""
    response = await client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data
    assert data["checks"]["database"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_metadata(client: AsyncClient):
    """Test metadata endpoint."""
    response = await client.get("/api/v1/metadata/")
    assert response.status_code == 200
    
    data = response.json()
    assert "currencies" in data
    assert "asset_categories" in data
    assert len(data["currencies"]) > 0
    assert len(data["asset_categories"]) > 0
    
    # Check USD is present
    usd = next((c for c in data["currencies"] if c["code"] == "USD"), None)
    assert usd is not None
    assert usd["name"] == "US Dollar"
    assert usd["symbol"] == "$"


@pytest.mark.asyncio
async def test_get_currencies(client: AsyncClient):
    """Test currencies endpoint."""
    response = await client.get("/api/v1/metadata/currencies")
    assert response.status_code == 200
    
    currencies = response.json()
    assert len(currencies) > 0
    
    # Check USD is present
    usd = next((c for c in currencies if c["code"] == "USD"), None)
    assert usd is not None
    assert usd["name"] == "US Dollar"
    assert usd["symbol"] == "$"


@pytest.mark.asyncio
async def test_get_asset_categories(client: AsyncClient):
    """Test asset categories endpoint."""
    response = await client.get("/api/v1/metadata/categories")
    assert response.status_code == 200
    
    categories = response.json()
    assert len(categories) > 0
    assert "cash" in categories
    assert "stock" in categories
    assert "crypto" in categories


@pytest.mark.asyncio
async def test_asset_crud_operations(client: AsyncClient):
    """Test complete CRUD operations for assets."""
    device_id = "test-device-123"
    
    # Test CREATE asset
    asset_data = {
        "name": "Test Savings Account",
        "category": "cash",
        "amount": "5000.00",
        "currency": "USD",
        "purchase_date": "2024-01-15",
        "notes": "Primary savings account"
    }
    
    response = await client.post(
        f"/api/v1/assets/?device_id={device_id}",
        json=asset_data
    )
    assert response.status_code == 200
    create_result = response.json()
    assert create_result["message"] == "Asset created successfully"
    assert "data" in create_result
    asset_id = create_result["data"]["id"]
    
    # Test READ single asset
    response = await client.get(
        f"/api/v1/assets/{asset_id}?device_id={device_id}"
    )
    assert response.status_code == 200
    asset = response.json()
    assert asset["name"] == "Test Savings Account"
    assert asset["category"] == "cash"
    assert asset["amount"] == "5000.0000"
    assert asset["currency"] == "USD"
    assert asset["notes"] == "Primary savings account"
    
    # Test READ all assets (grouped)
    response = await client.get(f"/api/v1/assets/?device_id={device_id}")
    assert response.status_code == 200
    grouped_assets = response.json()
    assert "cash" in grouped_assets
    assert len(grouped_assets["cash"]) == 1
    assert grouped_assets["cash"][0]["id"] == asset_id
    
    # Test UPDATE asset
    update_data = {
        "name": "Updated Savings Account",
        "amount": "6000.00",
        "notes": "Updated primary savings account"
    }
    
    response = await client.put(
        f"/api/v1/assets/{asset_id}?device_id={device_id}",
        json=update_data
    )
    assert response.status_code == 200
    update_result = response.json()
    assert update_result["message"] == "Asset updated successfully"
    
    # Verify update
    response = await client.get(
        f"/api/v1/assets/{asset_id}?device_id={device_id}"
    )
    assert response.status_code == 200
    updated_asset = response.json()
    assert updated_asset["name"] == "Updated Savings Account"
    assert updated_asset["amount"] == "6000.0000"
    assert updated_asset["notes"] == "Updated primary savings account"
    
    # Test DELETE asset
    response = await client.delete(
        f"/api/v1/assets/{asset_id}?device_id={device_id}"
    )
    assert response.status_code == 200
    delete_result = response.json()
    assert delete_result["message"] == "Asset deleted successfully"
    
    # Verify deletion
    response = await client.get(
        f"/api/v1/assets/{asset_id}?device_id={device_id}"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_portfolio_summary(client: AsyncClient):
    """Test portfolio summary calculation."""
    device_id = "test-device-portfolio"
    
    # Create multiple assets
    assets_data = [
        {
            "name": "Savings Account",
            "category": "cash",
            "amount": "10000.00",
            "currency": "USD",
            "purchase_date": "2024-01-01"
        },
        {
            "name": "Apple Stock",
            "category": "stock",
            "amount": "15000.00",
            "currency": "USD",
            "purchase_date": "2024-01-15"
        },
        {
            "name": "Bitcoin",
            "category": "crypto",
            "amount": "5000.00",
            "currency": "USD",
            "purchase_date": "2024-01-20"
        }
    ]
    
    for asset_data in assets_data:
        response = await client.post(
            f"/api/v1/assets/?device_id={device_id}",
            json=asset_data
        )
        assert response.status_code == 200
    
    # Test portfolio summary
    response = await client.get(
        f"/api/v1/portfolio/summary?device_id={device_id}&base_currency=USD"
    )
    assert response.status_code == 200
    
    summary = response.json()
    assert "asset_breakdown" in summary
    assert "base_currency" in summary
    assert "last_updated" in summary
    assert summary["base_currency"] == "USD"
    
    # Should have all three categories
    assert "cash" in summary["asset_breakdown"]
    assert "stock" in summary["asset_breakdown"]
    assert "crypto" in summary["asset_breakdown"]
    
    # Check values
    cash_breakdown = summary["asset_breakdown"]["cash"]
    stock_breakdown = summary["asset_breakdown"]["stock"]
    crypto_breakdown = summary["asset_breakdown"]["crypto"]
    
    assert cash_breakdown["total_amount"] == "10000.0000"
    assert cash_breakdown["count"] == 1
    assert stock_breakdown["total_amount"] == "15000.0000"
    assert stock_breakdown["count"] == 1
    assert crypto_breakdown["total_amount"] == "5000.0000"
    assert crypto_breakdown["count"] == 1


@pytest.mark.asyncio
async def test_asset_not_found(client: AsyncClient):
    """Test asset not found scenarios."""
    device_id = "test-device-notfound"
    fake_id = str(uuid.uuid4())
    
    # Test GET non-existent asset
    response = await client.get(
        f"/api/v1/assets/{fake_id}?device_id={device_id}"
    )
    assert response.status_code == 404
    
    # Test UPDATE non-existent asset
    response = await client.put(
        f"/api/v1/assets/{fake_id}?device_id={device_id}",
        json={"name": "Updated Name"}
    )
    assert response.status_code == 404
    
    # Test DELETE non-existent asset
    response = await client.delete(
        f"/api/v1/assets/{fake_id}?device_id={device_id}"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_validation_errors(client: AsyncClient):
    """Test validation error handling."""
    device_id = "test-device-validation"
    
    # Test invalid asset data
    invalid_data = {
        "name": "",  # Empty name should fail
        "category": "cash",
        "amount": "0",  # Zero amount should fail
        "currency": "INVALID",  # Invalid currency
        "purchase_date": "invalid-date"  # Invalid date format
    }
    
    response = await client.post(
        f"/api/v1/assets/?device_id={device_id}",
        json=invalid_data
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_multiple_currencies(client: AsyncClient):
    """Test assets with different currencies."""
    device_id = "test-device-multicurrency"
    
    # Create assets in different currencies
    assets_data = [
        {
            "name": "USD Cash",
            "category": "cash",
            "amount": "1000.00",
            "currency": "USD",
            "purchase_date": "2024-01-01"
        },
        {
            "name": "EUR Cash",
            "category": "cash",
            "amount": "850.00",
            "currency": "EUR",
            "purchase_date": "2024-01-01"
        },
        {
            "name": "CNY Cash",
            "category": "cash",
            "amount": "7000.00",
            "currency": "CNY",
            "purchase_date": "2024-01-01"
        }
    ]
    
    created_assets = []
    for asset_data in assets_data:
        response = await client.post(
            f"/api/v1/assets/?device_id={device_id}",
            json=asset_data
        )
        assert response.status_code == 200
        created_assets.append(response.json()["data"])
    
    # Get all assets
    response = await client.get(f"/api/v1/assets/?device_id={device_id}")
    assert response.status_code == 200
    grouped_assets = response.json()
    
    # Should have 3 cash assets with different currencies
    assert "cash" in grouped_assets
    assert len(grouped_assets["cash"]) == 3
    
    # Check currencies are preserved
    currencies = {asset["currency"] for asset in grouped_assets["cash"]}
    assert currencies == {"USD", "EUR", "CNY"}


@pytest.mark.asyncio
async def test_asset_categories(client: AsyncClient):
    """Test different asset categories."""
    device_id = "test-device-categories"
    
    # Create assets in different categories
    assets_data = [
        {
            "name": "Emergency Fund",
            "category": "cash",
            "amount": "5000.00",
            "currency": "USD",
            "purchase_date": "2024-01-01"
        },
        {
            "name": "Tesla Stock",
            "category": "stock",
            "amount": "10000.00",
            "currency": "USD",
            "purchase_date": "2024-01-15"
        },
        {
            "name": "Ethereum",
            "category": "crypto",
            "amount": "3000.00",
            "currency": "USD",
            "purchase_date": "2024-01-20"
        },
        {
            "name": "Apartment",
            "category": "real_estate",
            "amount": "300000.00",
            "currency": "USD",
            "purchase_date": "2024-01-01"
        }
    ]
    
    for asset_data in assets_data:
        response = await client.post(
            f"/api/v1/assets/?device_id={device_id}",
            json=asset_data
        )
        assert response.status_code == 200
    
    # Get all assets grouped
    response = await client.get(f"/api/v1/assets/?device_id={device_id}")
    assert response.status_code == 200
    grouped_assets = response.json()
    
    # Should have all categories
    expected_categories = {"cash", "stock", "crypto", "real_estate"}
    assert set(grouped_assets.keys()) == expected_categories
    
    # Each category should have exactly one asset
    for category in expected_categories:
        assert len(grouped_assets[category]) == 1