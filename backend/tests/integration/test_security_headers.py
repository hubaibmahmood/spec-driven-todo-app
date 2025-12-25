"""Integration tests for security headers middleware."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
class TestSecurityHeaders:
    """Tests for security headers applied to all API responses."""

    async def test_global_security_headers_on_health_endpoint(self, test_client: AsyncClient):
        """Test that global security headers are applied to health endpoint."""
        response = await test_client.get("/health")

        assert response.status_code == 200

        # Verify global security headers
        assert "Strict-Transport-Security" in response.headers
        assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

        assert "Permissions-Policy" in response.headers

    async def test_no_cache_headers_on_api_key_endpoints(self, test_client: AsyncClient):
        """Test that no-cache headers are applied to API key endpoints."""
        # Note: This will fail authentication, but we're only checking headers
        response = await test_client.get("/api/user-api-keys/current")

        # Should return 401 (no auth), but headers should still be present
        assert response.status_code == 401

        # Verify no-cache headers for sensitive endpoint
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]
        assert "no-store" in response.headers["Cache-Control"]
        assert "must-revalidate" in response.headers["Cache-Control"]
        assert "private" in response.headers["Cache-Control"]

        assert "Pragma" in response.headers
        assert response.headers["Pragma"] == "no-cache"

        assert "Expires" in response.headers
        assert response.headers["Expires"] == "0"

        # Should also have global security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers

    async def test_no_cache_headers_on_save_api_key_endpoint(self, test_client: AsyncClient):
        """Test no-cache headers on POST /api/user-api-keys endpoint."""
        response = await test_client.post(
            "/api/user-api-keys",
            json={"api_key": "test-key", "provider": "gemini"}
        )

        # Should return 401 (no auth), but headers should still be present
        assert response.status_code == 401

        # Verify no-cache headers
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]
        assert "no-store" in response.headers["Cache-Control"]

    async def test_no_cache_headers_on_test_api_key_endpoint(self, test_client: AsyncClient):
        """Test no-cache headers on POST /api/user-api-keys/test endpoint."""
        response = await test_client.post(
            "/api/user-api-keys/test",
            json={"api_key": "test-key"}
        )

        # Should return 401 (no auth), but headers should still be present
        assert response.status_code == 401

        # Verify no-cache headers
        assert "Cache-Control" in response.headers
        assert "no-cache" in response.headers["Cache-Control"]

    async def test_normal_caching_on_non_sensitive_endpoints(self, test_client: AsyncClient):
        """Test that non-sensitive endpoints don't have no-cache headers."""
        response = await test_client.get("/health")

        assert response.status_code == 200

        # Should NOT have no-cache headers
        if "Cache-Control" in response.headers:
            # If Cache-Control exists, it should not be the strict no-cache version
            cache_control = response.headers["Cache-Control"]
            # Health endpoint might have some caching, but not the strict API key version
            assert not all([
                "no-cache" in cache_control,
                "no-store" in cache_control,
                "must-revalidate" in cache_control,
                "private" in cache_control
            ])

        # Should still have global security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers

    async def test_all_endpoints_have_security_headers(self, test_client: AsyncClient):
        """Test that all endpoints receive global security headers."""
        endpoints_to_test = [
            "/health",
            "/api/tasks",  # Will fail auth but should have headers
        ]

        for endpoint in endpoints_to_test:
            response = await test_client.get(endpoint)

            # Verify minimum security headers are present
            assert "X-Content-Type-Options" in response.headers, f"Missing X-Content-Type-Options on {endpoint}"
            assert "X-Frame-Options" in response.headers, f"Missing X-Frame-Options on {endpoint}"
            assert "Strict-Transport-Security" in response.headers, f"Missing HSTS on {endpoint}"
