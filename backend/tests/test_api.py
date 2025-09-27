"""Test API endpoints."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_basic_health_check(self, client: AsyncClient):
        """Test basic health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_api_health_check(self, client: AsyncClient):
        """Test API v1 health check endpoint."""
        response = await client.get("/api/v1/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "MoneyInOne API"
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_detailed_health_check(self, client: AsyncClient):
        """Test detailed health check endpoint."""
        response = await client.get("/api/v1/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["status"] == "healthy"


class TestAssetEndpoints:
    """Test asset management endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_assets_empty(self, client: AsyncClient):
        """Test getting assets when none exist."""
        response = await client.get("/api/v1/assets/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_count"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 50
    
    @pytest.mark.asyncio
    async def test_get_asset_types(self, client: AsyncClient):
        """Test getting asset types."""
        response = await client.get("/api/v1/assets/types/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have default asset types from migration
        assert len(data) > 0
        
        # Check that default types are present
        type_names = [asset_type["name"] for asset_type in data]
        assert "Stock" in type_names
        assert "Cryptocurrency" in type_names
        assert "Cash/Bank Account" in type_names
