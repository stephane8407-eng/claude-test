"""
Request tracking middleware - Generates unique request IDs and logs requests
"""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
from app.services.logger import log_api_request, log_error


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that tracks requests with unique IDs and logs timing
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with tracking

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response with tracking headers
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store request ID in request state for access in endpoints
        request.state.request_id = request_id

        # Get client IP
        client_ip = self._get_client_ip(request)
        request.state.client_ip = client_ip

        # Start timing
        start_time = time.time()

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Get user context if available
            user_id = None
            village_id = None
            if hasattr(request.state, 'user') and request.state.user:
                user_id = request.state.user.id
                if hasattr(request.state.user, 'village_id'):
                    village_id = request.state.user.village_id

            # Log request
            log_api_request(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id,
                user_id=user_id,
                village_id=village_id,
                ip_address=client_ip
            )

            # Add tracking headers to response
            response.headers['X-Request-ID'] = request_id
            response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"

            return response

        except Exception as exc:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            log_error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=(type(exc), exc, exc.__traceback__),
                request_id=request_id
            )

            # Re-raise exception
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request

        Args:
            request: FastAPI request

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (set by reverse proxies)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(',')[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip

        # Fall back to direct client address
        if request.client:
            return request.client.host

        return 'unknown'


def get_request_id(request: Request) -> str:
    """
    Get request ID from request state

    Args:
        request: FastAPI request

    Returns:
        Request ID or 'unknown' if not set
    """
    if hasattr(request.state, 'request_id'):
        return request.state.request_id
    return 'unknown'


def get_client_ip(request: Request) -> str:
    """
    Get client IP from request state

    Args:
        request: FastAPI request

    Returns:
        Client IP or 'unknown' if not set
    """
    if hasattr(request.state, 'client_ip'):
        return request.state.client_ip
    return 'unknown'
