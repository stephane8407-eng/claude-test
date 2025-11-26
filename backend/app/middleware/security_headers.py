"""
Security headers middleware
Adds security headers to all responses to prevent common web vulnerabilities
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all responses

    Security headers protect against:
    - XSS (Cross-Site Scripting)
    - Clickjacking
    - MIME type sniffing
    - Information leakage
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to response

        Args:
            request: The incoming request
            call_next: The next middleware or endpoint

        Returns:
            Response with security headers
        """
        # Process request and get response
        response = await call_next(request)

        # Add security headers

        # Content Security Policy - Prevents XSS and injection attacks
        # This is a strict policy - adjust based on your needs
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # X-Frame-Options - Prevents clickjacking
        # DENY: Page cannot be displayed in a frame
        response.headers['X-Frame-Options'] = 'DENY'

        # X-Content-Type-Options - Prevents MIME type sniffing
        # nosniff: Browser should not try to detect content type
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # X-XSS-Protection - Legacy XSS protection (mostly for older browsers)
        # 1; mode=block: Enable XSS filter and block page if attack detected
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Referrer-Policy - Controls how much referrer information is sent
        # strict-origin-when-cross-origin: Send full URL for same-origin, origin only for cross-origin
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions-Policy - Controls which browser features can be used
        # Disable potentially dangerous features
        response.headers['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'accelerometer=()'
        )

        # Strict-Transport-Security - Force HTTPS (only add if using HTTPS)
        # This header tells browsers to only connect via HTTPS
        # max-age=31536000: Remember for 1 year
        # includeSubDomains: Apply to all subdomains
        # preload: Allow inclusion in browser preload lists
        if request.url.scheme == 'https':
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )

        # X-Permitted-Cross-Domain-Policies - Restrict Adobe Flash and PDF cross-domain requests
        response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'

        # Remove headers that leak information
        response.headers.pop('Server', None)  # Remove server version
        response.headers.pop('X-Powered-By', None)  # Remove framework info

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that limits request body size to prevent memory exhaustion attacks
    """

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):
        """
        Initialize middleware

        Args:
            app: The FastAPI application
            max_size: Maximum request body size in bytes (default: 10MB)
        """
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check request size before processing

        Args:
            request: The incoming request
            call_next: The next middleware or endpoint

        Returns:
            Response or 413 error if request too large
        """
        # Check Content-Length header if present
        content_length = request.headers.get('content-length')

        if content_length:
            try:
                content_length = int(content_length)
                if content_length > self.max_size:
                    return Response(
                        content=f"Request body too large: {content_length} bytes (max {self.max_size} bytes)",
                        status_code=413,  # Payload Too Large
                        media_type="text/plain"
                    )
            except ValueError:
                # Invalid Content-Length header
                return Response(
                    content="Invalid Content-Length header",
                    status_code=400,
                    media_type="text/plain"
                )

        # Process request
        response = await call_next(request)
        return response


# Convenience function to add security middleware to app
def add_security_middleware(app, max_request_size: int = 10 * 1024 * 1024):
    """
    Add security middleware to FastAPI application

    Args:
        app: FastAPI application instance
        max_request_size: Maximum request body size in bytes (default: 10MB)
    """
    # Add request size limit middleware
    app.add_middleware(RequestSizeLimitMiddleware, max_size=max_request_size)

    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
