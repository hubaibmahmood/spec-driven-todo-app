"""Integration tests for health check endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_health_check_returns_200(test_client: AsyncClient):
    """Test that health check endpoint returns 200 status code."""
    response = await test_client.get("/health")
    
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_health_check_includes_database_status(test_client: AsyncClient):
    """Test that health check response includes database connectivity status."""
    response = await test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "status" in data
    assert "timestamp" in data
    assert "database" in data
    
    # Check field values
    assert data["status"] in ["healthy", "unhealthy"]
    assert isinstance(data["timestamp"], str)
    assert data["database"] == "connected"  # Should be connected in tests
