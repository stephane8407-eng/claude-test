"""
CORS (Cross-Origin Resource Sharing) configuration
"""
from fastapi.middleware.cors import CORSMiddleware
from typing import List


class CORSConfig:
    """
    CORS configuration for different environments
    """

    @staticmethod
    def get_allowed_origins(environment: str = 'development') -> List[str]:
        """
        Get allowed origins based on environment

        Args:
            environment: Environment name (development, staging, production)

        Returns:
            List of allowed origins
        """
        if environment == 'production':
            # In production, specify exact domains
            return [
                "https://treasuremap.example.com",
                "https://www.treasuremap.example.com",
            ]
        elif environment == 'staging':
            # In staging, allow staging domains
            return [
                "https://staging.treasuremap.example.com",
                "http://localhost:3000",  # For testing
            ]
        else:  # development
            # In development, allow localhost with common ports
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:8000",
                "http://localhost:8080",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
            ]

    @staticmethod
    def get_allowed_methods() -> List[str]:
        """
        Get allowed HTTP methods

        Returns:
            List of allowed methods
        """
        return ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    @staticmethod
    def get_allowed_headers() -> List[str]:
        """
        Get allowed request headers

        Returns:
            List of allowed headers
        """
        return [
            "Accept",
            "Accept-Language",
            "Content-Type",
            "Authorization",
            "X-CSRF-Token",
            "X-Request-ID",
        ]

    @staticmethod
    def get_expose_headers() -> List[str]:
        """
        Get headers to expose to client

        Returns:
            List of headers to expose
        """
        return [
            "X-Request-ID",
            "X-Response-Time",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]


def setup_cors(app, environment: str = 'development'):
    """
    Setup CORS middleware for FastAPI application

    Args:
        app: FastAPI application instance
        environment: Environment name
    """
    config = CORSConfig()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get_allowed_origins(environment),
        allow_credentials=True,  # Allow cookies and authorization headers
        allow_methods=config.get_allowed_methods(),
        allow_headers=config.get_allowed_headers(),
        expose_headers=config.get_expose_headers(),
        max_age=86400,  # Cache preflight requests for 24 hours
    )


def is_origin_allowed(origin: str, environment: str = 'development') -> bool:
    """
    Check if an origin is allowed

    Args:
        origin: Origin to check
        environment: Environment name

    Returns:
        True if origin is allowed
    """
    allowed_origins = CORSConfig.get_allowed_origins(environment)
    return origin in allowed_origins
