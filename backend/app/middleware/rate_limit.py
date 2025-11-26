"""
Rate limiting middleware to prevent abuse
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from typing import Callable, Optional


def get_user_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting (IP for anonymous, user ID for authenticated)

    Args:
        request: FastAPI request

    Returns:
        Identifier string for rate limiting
    """
    # Check if user is authenticated
    if hasattr(request.state, 'user') and request.state.user:
        # Use user ID for authenticated requests
        return f"user:{request.state.user.id}"

    # Use IP address for anonymous requests
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["1000/minute"],  # Default limit for authenticated users
    storage_uri="memory://",  # Use in-memory storage (consider Redis for production)
    headers_enabled=True  # Include rate limit headers in response
)


def add_rate_limit_headers(response: Response, request: Request):
    """
    Add rate limit headers to response

    Args:
        response: FastAPI response
        request: FastAPI request
    """
    # Headers are automatically added by slowapi when headers_enabled=True
    # This function is here for potential custom header logic
    pass


# Rate limit configurations for different endpoints
class RateLimits:
    """
    Rate limit configurations for different endpoint types
    """

    # Authentication endpoints (prevent brute force)
    LOGIN = "5/minute"  # 5 login attempts per minute per IP
    REGISTER = "3/hour"  # 3 registrations per hour per IP
    PASSWORD_RESET = "3/hour"  # 3 password reset requests per hour per IP

    # Public API endpoints
    PUBLIC_READ = "100/minute"  # 100 requests per minute per IP for public reads

    # Authenticated API endpoints
    AUTHENTICATED = "1000/minute"  # 1000 requests per minute per user

    # AI/Expensive operations
    AI_GENERATION = "10/hour"  # 10 AI generations per hour per user

    # File uploads
    FILE_UPLOAD = "20/hour"  # 20 file uploads per hour per user


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors

    Args:
        request: FastAPI request
        exc: RateLimitExceeded exception

    Returns:
        Custom error response
    """
    return Response(
        content={
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {exc.detail}",
            "retry_after": getattr(exc, 'retry_after', None)
        },
        status_code=429,
        headers={
            "Retry-After": str(getattr(exc, 'retry_after', 60)),
            "X-RateLimit-Limit": str(getattr(exc, 'limit', 'unknown')),
            "X-RateLimit-Remaining": "0"
        }
    )


# Decorator for custom rate limits
def rate_limit(limit: str):
    """
    Decorator to apply custom rate limit to endpoint

    Args:
        limit: Rate limit string (e.g., "5/minute", "100/hour")

    Returns:
        Decorator function

    Usage:
        @router.post("/endpoint")
        @limiter.limit(RateLimits.LOGIN)
        async def endpoint():
            pass
    """
    return limiter.limit(limit)


def setup_rate_limiting(app):
    """
    Setup rate limiting for FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Add limiter state to app
    app.state.limiter = limiter

    # Add exception handler for rate limit exceeded
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Convenience decorators for common limits
def limit_login(func):
    """Apply login rate limit"""
    return limiter.limit(RateLimits.LOGIN)(func)


def limit_register(func):
    """Apply registration rate limit"""
    return limiter.limit(RateLimits.REGISTER)(func)


def limit_password_reset(func):
    """Apply password reset rate limit"""
    return limiter.limit(RateLimits.PASSWORD_RESET)(func)


def limit_ai_generation(func):
    """Apply AI generation rate limit"""
    return limiter.limit(RateLimits.AI_GENERATION)(func)


def limit_file_upload(func):
    """Apply file upload rate limit"""
    return limiter.limit(RateLimits.FILE_UPLOAD)(func)


def limit_public_read(func):
    """Apply public read rate limit"""
    return limiter.limit(RateLimits.PUBLIC_READ)(func)
