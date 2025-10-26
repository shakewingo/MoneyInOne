"""API integration tests for MoneyInOne finance app."""

import pytest
import uuid
from decimal import Decimal
from httpx import AsyncClient


class TestAPIIntegration:
    """Test API endpoints focusing on HTTP integration."""
    
    @pytest.mark.asyncio
    async def test_health_and_metadata_endpoints(self, client: AsyncClient):
        """Test system health and metadata endpoints."""
        # Health check
        response = await client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert all(key in health_data for key in ["app", "version"])
        
        # Metadata endpoint
        response = await client.get("/api/v1/metadata/")
        assert response.status_code == 200
        metadata = response.json()
        
        # Verify complete metadata structure
        assert all(key in metadata for key in ["currencies", "asset_categories", "credit_categories"])
        assert len(metadata["currencies"]) >= 7  # At least USD, EUR, GBP, JPY, CAD, AUD, CNY
        assert "stock" in metadata["asset_categories"]  # Verify our new stock category
        
        # Verify currency details
        usd = next((c for c in metadata["currencies"] if c["code"] == "USD"), None)
        assert usd and usd["name"] == "US Dollar" and usd["symbol"] == "$"
    
    @pytest.mark.asyncio
    async def test_asset_api_workflow(self, client: AsyncClient, factory):
        """Test complete asset API workflow including stock fields."""
        device_id = "test-api-assets"
        
        # CREATE stock asset with symbol and shares
        stock_data = factory.stock_asset_data("Google", "GOOGL", 25.0, Decimal("37500.00"))
        response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=stock_data)
        assert response.status_code == 200
        
        create_result = response.json()
        assert create_result["message"] == "Asset created successfully"
        asset_id = create_result["data"]["id"]
        
        # Verify stock-specific fields in response
        created_asset = create_result["data"]
        assert created_asset["symbol"] == "GOOGL"
        assert created_asset["shares"] == 25.0
        
        # READ asset
        response = await client.get(f"/api/v1/assets/{asset_id}?device_id={device_id}")
        assert response.status_code == 200
        asset = response.json()
        assert asset["name"] == "Google"
        assert asset["symbol"] == "GOOGL"
        assert asset["shares"] == 25.0
        
        # UPDATE asset (including stock fields)
        update_data = {"name": "Alphabet Inc.", "shares": 30.0, "amount": "45000.00"}
        response = await client.put(f"/api/v1/assets/{asset_id}?device_id={device_id}", json=update_data)
        assert response.status_code == 200
        
        # Verify update
        response = await client.get(f"/api/v1/assets/{asset_id}?device_id={device_id}")
        updated_asset = response.json()
        assert updated_asset["name"] == "Alphabet Inc."
        assert updated_asset["shares"] == 30.0
        assert updated_asset["symbol"] == "GOOGL"  # Unchanged
        
        # DELETE asset
        response = await client.delete(f"/api/v1/assets/{asset_id}?device_id={device_id}")
        assert response.status_code == 200
        
        # Verify deletion
        response = await client.get(f"/api/v1/assets/{asset_id}?device_id={device_id}")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_credit_api_workflow(self, client: AsyncClient, factory):
        """Test complete credit API workflow."""
        device_id = "test-api-credits"
        
        # CREATE
        credit_data = factory.credit_data("Business Loan", "loan", Decimal("50000.00"))
        response = await client.post(f"/api/v1/credits/?device_id={device_id}", json=credit_data)
        assert response.status_code == 200
        credit_id = response.json()["data"]["id"]
        
        # UPDATE
        response = await client.put(
            f"/api/v1/credits/{credit_id}?device_id={device_id}",
            json={"amount": 45000.00}
        )
        assert response.status_code == 200
        
        # Verify and DELETE
        response = await client.get(f"/api/v1/credits/{credit_id}?device_id={device_id}")
        assert response.json()["amount"] == 45000.00
        
        response = await client.delete(f"/api/v1/credits/{credit_id}?device_id={device_id}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_grouped_data_endpoints(self, client: AsyncClient, factory):
        """Test grouped data retrieval via API."""
        device_id = "test-api-grouped"
        
        # Create diverse test data
        test_assets = [
            factory.asset_data("USD Cash", "cash", Decimal("5000.00"), "USD"),
            factory.asset_data("EUR Cash", "cash", Decimal("3000.00"), "EUR"),
            factory.stock_asset_data("Apple", "AAPL", 50.0, Decimal("7500.00")),
            factory.asset_data("Bitcoin", "crypto", Decimal("25000.00"), "USD"),
        ]
        
        test_credits = [
            factory.credit_data("Visa", "credit_card", Decimal("2000.00"), "USD"),
            factory.credit_data("Mortgage", "mortgage", Decimal("200000.00"), "USD"),
        ]
        
        # Create assets and credits
        for asset_data in test_assets:
            response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=asset_data)
            assert response.status_code == 200
        
        for credit_data in test_credits:
            response = await client.post(f"/api/v1/credits/?device_id={device_id}", json=credit_data)
            assert response.status_code == 200
        
        # Test grouped assets - now returns Dict[str, AssetCategoryBreakdown]
        response = await client.get(f"/api/v1/assets/?device_id={device_id}")
        assert response.status_code == 200
        grouped_assets = response.json()
        
        # Verify breakdown structure with assets list
        assert grouped_assets["cash"]["count"] == 2
        assert len(grouped_assets["cash"]["assets"]) == 2
        assert grouped_assets["stock"]["count"] == 1
        assert len(grouped_assets["stock"]["assets"]) == 1
        assert grouped_assets["crypto"]["count"] == 1
        
        # Verify stock asset has symbol and shares in API response
        stock_asset = grouped_assets["stock"]["assets"][0]
        assert stock_asset["symbol"] == "AAPL"
        assert stock_asset["shares"] == 50.0
        
        # Test grouped credits - now returns Dict[str, CreditCategoryBreakdown]
        response = await client.get(f"/api/v1/credits/?device_id={device_id}")
        assert response.status_code == 200
        grouped_credits = response.json()
        
        # Verify breakdown structure with credits list
        assert grouped_credits["credit_card"]["count"] == 1
        assert len(grouped_credits["credit_card"]["credits"]) == 1
        assert grouped_credits["mortgage"]["count"] == 1
        assert len(grouped_credits["mortgage"]["credits"]) == 1
    
    @pytest.mark.asyncio
    async def test_portfolio_summary_endpoint(self, client: AsyncClient, sample_data):
        """Test portfolio summary API endpoint."""
        device_id = sample_data["device_id"]
        
        response = await client.get(f"/api/v1/portfolio/summary?device_id={device_id}")
        assert response.status_code == 200
        portfolio = response.json()
        
        # Verify API response structure - now uses net_worth instead of net_summary
        required_keys = ["asset_summary", "credit_summary", "net_worth", "base_currency", "last_updated"]
        assert all(key in portfolio for key in required_keys)
        
        # Verify base currency
        assert portfolio["base_currency"] == "USD"
        
        # Verify calculations are correct (counts per category)
        assert portfolio["asset_summary"]["cash"]["count"] == 2
        assert portfolio["asset_summary"]["stock"]["count"] == 1
        assert portfolio["credit_summary"]["credit_card"]["count"] == 2
        
        # Test net_worth calculation (single value in base currency)
        # Without exchange rate service, EUR converts 1:1 to USD
        # Assets: $5000 + €3000 ($3000) + $7500 + $25000 = $40,500
        # Credits: $2000 + $15000 + €1000 ($1000) = $18,000
        # Net: $22,500
        assert float(portfolio["net_worth"]) == 22848.6
    
    @pytest.mark.asyncio
    async def test_api_validation_and_error_responses(self, client: AsyncClient):
        """Test API validation and error handling."""
        device_id = "test-api-validation"
        fake_id = str(uuid.uuid4())

        # Test stock field validation
        invalid_stock = {
            "name": "Test Stock",
            "category": "cash",  
            "amount": "1000.00",
            "currency": "USD",
            "purchase_date": "2024-01-01",
            "shares": "-10"  
        }
        
        response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=invalid_stock)
        assert response.status_code == 422
        
        endpoints = [
            f"/api/v1/assets/{fake_id}",
            f"/api/v1/credits/{fake_id}"
        ]
        
        for endpoint in endpoints:
            # GET
            response = await client.get(f"{endpoint}?device_id={device_id}")
            assert response.status_code == 404
            
            # PUT
            response = await client.put(f"{endpoint}?device_id={device_id}", json={"name": "Updated"})
            assert response.status_code == 404
            
            # DELETE
            response = await client.delete(f"{endpoint}?device_id={device_id}")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_device_isolation_via_api(self, client: AsyncClient, factory):
        """Test device-based data isolation through API."""
        devices = ["device-1", "device-2"]
        asset_data = factory.asset_data("Isolation Test")
        
        # Create asset for device 1
        response = await client.post(f"/api/v1/assets/?device_id={devices[0]}", json=asset_data)
        assert response.status_code == 200
        asset_id = response.json()["data"]["id"]
        
        # Device 1 can access its asset
        response = await client.get(f"/api/v1/assets/{asset_id}?device_id={devices[0]}")
        assert response.status_code == 200
        
        # Device 2 cannot access device 1's asset
        response = await client.get(f"/api/v1/assets/{asset_id}?device_id={devices[1]}")
        assert response.status_code == 404
        
        # Verify grouped assets are isolated
        response = await client.get(f"/api/v1/assets/?device_id={devices[1]}")
        assert response.status_code == 200
        grouped = response.json()
        # grouped is now Dict[str, AssetCategoryBreakdown], should be empty for device 2
        assert len(grouped) == 0 or all(breakdown["count"] == 0 for breakdown in grouped.values())


@pytest.mark.asyncio
async def test_api_response_formats(client: AsyncClient, factory):
    """Test API response formats and data serialization."""
    device_id = "test-response-format"
    
    # Create asset with decimal precision
    asset_data = factory.asset_data(amount=Decimal("12345.6789"))
    response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=asset_data)
    
    # Verify response format
    result = response.json()
    assert "message" in result
    assert "data" in result
    assert isinstance(result["data"], dict)
    
    # Verify decimal serialization
    created_asset = result["data"]
    assert created_asset["amount"] == 12345.6789  # Float format for precision
    assert "created_at" in created_asset
    assert "updated_at" in created_asset

    @pytest.mark.asyncio
    async def test_market_data_endpoints(self, client: AsyncClient, factory):
        """Test market data refresh endpoints integrated into assets."""
        device_id = "test-market-data"
        
        # Create a stock asset with market tracking
        stock_data = factory.stock_asset_data("Tesla", "TSLA", 10.0, Decimal("2500.00"))
        stock_data["is_market_tracked"] = True
        
        response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=stock_data)
        assert response.status_code == 200
        asset_id = response.json()["data"]["id"]
        
        # Test refresh all prices endpoint
        response = await client.post(
            "/api/v1/assets/refresh-prices",
            headers={"X-Device-ID": device_id}
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "data" in result
        assert all(key in result["data"] for key in ["updated", "failed", "skipped"])
        
        # Test refresh specific assets endpoint
        response = await client.post(
            "/api/v1/assets/refresh-prices/assets",
            json=[asset_id],
            headers={"X-Device-ID": device_id}
        )
        assert response.status_code == 200
        result = response.json()
        assert "Price refresh completed for 1 assets" in result["message"]
        
        # Test refresh single asset endpoint
        response = await client.post(
            f"/api/v1/assets/{asset_id}/refresh-price",
            headers={"X-Device-ID": device_id}
        )
        assert response.status_code == 200
        result = response.json()
        assert f"Asset {asset_id} price updated successfully" == result["message"]

    @pytest.mark.asyncio
    async def test_usd_only_for_stock_crypto_on_create(self, client: AsyncClient, factory):
        """Stock/Crypto assets must use USD currency on create."""
        device_id = "test-usd-only"

        # Non-USD stock should fail
        stock_eur = factory.stock_asset_data("Apple", "AAPL", 10.0, Decimal("1500.00"))
        stock_eur["currency"] = "EUR"
        response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=stock_eur)
        assert response.status_code == 422
        assert "must use USD currency" in response.text

        # USD stock should succeed
        stock_usd = factory.stock_asset_data("Apple", "AAPL", 10.0, Decimal("1500.00"))
        response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=stock_usd)
        assert response.status_code == 200

        # Non-USD crypto should fail
        crypto_gbp = factory.asset_data("Bitcoin", "crypto", Decimal("1000.00"), "GBP")
        crypto_gbp.update({"symbol": "BTC", "shares": 0.05, "is_market_tracked": True})
        response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=crypto_gbp)
        assert response.status_code == 422
        assert "must use USD currency" in response.text

        # USD crypto should succeed
        crypto_usd = factory.asset_data("Bitcoin", "crypto", Decimal("1000.00"), "USD")
        crypto_usd.update({"symbol": "BTC", "shares": 0.05, "is_market_tracked": True})
        response = await client.post(f"/api/v1/assets/?device_id={device_id}", json=crypto_usd)
        assert response.status_code == 200