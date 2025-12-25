"""Security headers middleware for FastAPI application."""

import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all API responses.

    Implements OWASP security best practices including:
    - HSTS (HTTP Strict Transport Security)
    - Content Security Policy
    - X-Frame-Options (clickjacking protection)
    - X-Content-Type-Options (MIME-sniffing protection)
    - No-cache headers for sensitive endpoints
    """

    # Sensitive endpoints that should never be cached
    SENSITIVE_ENDPOINTS = [
        "/api/user-api-keys",
        "/api/user-api-keys/current",
        "/api/user-api-keys/test",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response with security headers added
        """
        # Process request
        response = await call_next(request)

        # Global security headers (applied to all responses)
        self._add_global_headers(response)

        # Sensitive endpoint headers (no-cache for API keys)
        if self._is_sensitive_endpoint(request.url.path):
            self._add_no_cache_headers(response)
            logger.debug(f"Applied no-cache headers to sensitive endpoint: {request.url.path}")

        return response

    def _add_global_headers(self, response: Response) -> None:
        """
        Add global security headers to response.

        Args:
            response: HTTP response object to modify
        """
        # HSTS - Force HTTPS for 1 year (including subdomains)
        # NOTE: Only enable in production with valid SSL certificate
        # For development, this header is informational only
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Prevent MIME-sniffing attacks
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking by blocking iframe embedding
        response.headers["X-Frame-Options"] = "DENY"

        # Content Security Policy - restrict resource loading
        # This is a basic policy; adjust based on frontend needs
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'"
        )

        # XSS Protection (legacy header, but still useful for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy - control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy - disable unused browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )

    def _add_no_cache_headers(self, response: Response) -> None:
        """
        Add no-cache headers for sensitive endpoints.

        Prevents caching of API keys and other sensitive data
        in browsers, proxies, and CDNs.

        Args:
            response: HTTP response object to modify
        """
        # HTTP 1.1 - no caching
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate, private, max-age=0"
        )

        # HTTP 1.0 - no caching (legacy support)
        response.headers["Pragma"] = "no-cache"

        # HTTP 1.0 - expire immediately
        response.headers["Expires"] = "0"

    def _is_sensitive_endpoint(self, path: str) -> bool:
        """
        Check if endpoint contains sensitive data (API keys).

        Args:
            path: Request URL path

        Returns:
            True if endpoint is sensitive, False otherwise
        """
        return any(path.startswith(endpoint) for endpoint in self.SENSITIVE_ENDPOINTS)
