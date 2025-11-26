"""
Configuration management with environment variables
Loads and validates configuration from .env file
Supports multiple environments: development, staging, production
"""
import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


class Config:
    """
    Application configuration loaded from environment variables
    Supports development, staging, and production environments
    """

    # Environment-specific defaults
    ENV_DEFAULTS = {
        'development': {
            'DEBUG': True,
            'LOG_LEVEL': 'DEBUG',
            'CORS_ORIGINS': 'http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000',
            'ENABLE_SECURITY_HEADERS': False,
            'RATE_LIMIT_ENABLED': False,
            'SENTRY_ENABLED': False,
        },
        'staging': {
            'DEBUG': True,
            'LOG_LEVEL': 'INFO',
            'CORS_ORIGINS': 'https://staging.spvtreasurehunt.com',
            'ENABLE_SECURITY_HEADERS': True,
            'RATE_LIMIT_ENABLED': True,
            'SENTRY_ENABLED': True,
        },
        'production': {
            'DEBUG': False,
            'LOG_LEVEL': 'WARNING',
            'CORS_ORIGINS': 'https://spvtreasurehunt.com',
            'ENABLE_SECURITY_HEADERS': True,
            'RATE_LIMIT_ENABLED': True,
            'SENTRY_ENABLED': True,
        }
    }

    def __init__(self):
        """Load configuration from .env file"""
        # Load .env file from backend directory
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)

        # Load and validate required configuration
        # Load app config first to set ENVIRONMENT
        self._load_app_config()
        self._load_database_config()
        self._load_cache_config()
        self._load_security_config()
        self._load_api_keys()
        self._load_monitoring_config()

    def _load_database_config(self):
        """Load database configuration"""
        self.DATABASE_URL = self._get_required_env('DATABASE_URL')

        # Parse database URL for individual components (optional)
        if self.DATABASE_URL.startswith('postgresql://'):
            self.DATABASE_TYPE = 'postgresql'
        else:
            self.DATABASE_TYPE = 'unknown'

    def _load_cache_config(self):
        """Load cache configuration (Redis)"""
        # Redis URL (optional - falls back to in-memory cache if not set)
        self.REDIS_URL = self._get_env('REDIS_URL')

        # Cache TTL settings (in seconds)
        self.CACHE_TTL_SHORT = int(self._get_env('CACHE_TTL_SHORT', '300'))  # 5 minutes
        self.CACHE_TTL_MEDIUM = int(self._get_env('CACHE_TTL_MEDIUM', '3600'))  # 1 hour
        self.CACHE_TTL_LONG = int(self._get_env('CACHE_TTL_LONG', '86400'))  # 24 hours

        # Cache enabled
        cache_enabled_str = self._get_env('CACHE_ENABLED', 'True' if self.REDIS_URL else 'False')
        self.CACHE_ENABLED = cache_enabled_str.lower() in ('true', '1', 'yes')

    def _load_security_config(self):
        """Load security configuration with environment-specific defaults"""
        env_defaults = self.ENV_DEFAULTS[self.ENVIRONMENT]

        # JWT Secret Key (required for authentication)
        self.JWT_SECRET_KEY = self._get_required_env('JWT_SECRET_KEY')

        # Validate JWT secret is not the default
        if 'change_in_production' in self.JWT_SECRET_KEY.lower():
            if self.ENVIRONMENT == 'production':
                raise ConfigError(
                    "JWT_SECRET_KEY must be changed from default value in production!"
                )

        # JWT settings
        self.JWT_ALGORITHM = self._get_env('JWT_ALGORITHM', 'HS256')
        self.JWT_EXPIRATION_HOURS = int(self._get_env('JWT_EXPIRATION_HOURS', '24'))

        # CSRF Protection
        self.CSRF_ENABLED = self._get_env('CSRF_ENABLED', 'true').lower() in ('true', '1', 'yes')
        self.CSRF_SECRET_KEY = self._get_env('CSRF_SECRET_KEY', self.JWT_SECRET_KEY)

        # CORS settings with environment-specific defaults
        self.CORS_ORIGINS = self._get_env('CORS_ORIGINS', env_defaults['CORS_ORIGINS'])
        self.CORS_ORIGINS_LIST = [origin.strip() for origin in self.CORS_ORIGINS.split(',')]

        # Session settings
        self.SESSION_COOKIE_SECURE = self.ENVIRONMENT != 'development'
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = 'lax'

    def _load_api_keys(self):
        """Load external API keys"""
        # Anthropic Claude API (required for identity generation)
        self.ANTHROPIC_API_KEY = self._get_env('ANTHROPIC_API_KEY')
        if not self.ANTHROPIC_API_KEY:
            print("⚠️  WARNING: ANTHROPIC_API_KEY not set - AI identity generation will fail")

        # Google API keys (optional for web scraping)
        self.GOOGLE_API_KEY = self._get_env('GOOGLE_API_KEY')
        self.GOOGLE_CSE_ID = self._get_env('GOOGLE_CSE_ID')

    def _load_monitoring_config(self):
        """Load monitoring and observability configuration"""
        env_defaults = self.ENV_DEFAULTS[self.ENVIRONMENT]

        # Sentry error tracking
        self.SENTRY_DSN = self._get_env('SENTRY_DSN')
        sentry_enabled_str = self._get_env('SENTRY_ENABLED', str(env_defaults['SENTRY_ENABLED']))
        self.SENTRY_ENABLED = sentry_enabled_str.lower() in ('true', '1', 'yes')

        # Only enable Sentry if DSN is provided
        if self.SENTRY_ENABLED and not self.SENTRY_DSN:
            print("⚠️  WARNING: SENTRY_ENABLED=true but SENTRY_DSN not set")
            self.SENTRY_ENABLED = False

        # Sentry sample rates
        self.SENTRY_TRACES_SAMPLE_RATE = float(self._get_env('SENTRY_TRACES_SAMPLE_RATE', '0.1'))
        self.SENTRY_PROFILES_SAMPLE_RATE = float(self._get_env('SENTRY_PROFILES_SAMPLE_RATE', '0.1'))

        # Health check settings
        self.HEALTH_CHECK_ENABLED = self._get_env('HEALTH_CHECK_ENABLED', 'true').lower() in ('true', '1', 'yes')

    def _load_app_config(self):
        """Load application configuration with environment-specific defaults"""
        # Determine environment
        self.ENVIRONMENT = self._get_env('ENVIRONMENT', 'development')

        if self.ENVIRONMENT not in self.ENV_DEFAULTS:
            raise ConfigError(
                f"Invalid ENVIRONMENT: {self.ENVIRONMENT}. "
                f"Must be one of: {', '.join(self.ENV_DEFAULTS.keys())}"
            )

        # Get environment defaults
        env_defaults = self.ENV_DEFAULTS[self.ENVIRONMENT]

        # Debug mode
        debug_str = self._get_env('DEBUG', str(env_defaults['DEBUG']))
        self.DEBUG = debug_str.lower() in ('true', '1', 'yes')

        # Logging level
        self.LOG_LEVEL = self._get_env('LOG_LEVEL', env_defaults['LOG_LEVEL'])

        # Rate limiting
        rate_limit_str = self._get_env('RATE_LIMIT_ENABLED', str(env_defaults['RATE_LIMIT_ENABLED']))
        self.RATE_LIMIT_ENABLED = rate_limit_str.lower() in ('true', '1', 'yes')

        # File upload settings
        self.MAX_FILE_SIZE_MB = int(self._get_env('MAX_FILE_SIZE_MB', '5'))
        self.MAX_REQUEST_SIZE_MB = int(self._get_env('MAX_REQUEST_SIZE_MB', '10'))

        # Image processing settings
        self.MAX_IMAGE_WIDTH = int(self._get_env('MAX_IMAGE_WIDTH', '1920'))
        self.MAX_IMAGE_HEIGHT = int(self._get_env('MAX_IMAGE_HEIGHT', '1920'))

        # Security headers
        security_str = self._get_env('ENABLE_SECURITY_HEADERS', str(env_defaults['ENABLE_SECURITY_HEADERS']))
        self.ENABLE_SECURITY_HEADERS = security_str.lower() in ('true', '1', 'yes')

        # Server settings
        self.HOST = self._get_env('HOST', '0.0.0.0')
        self.PORT = int(self._get_env('PORT', '8000'))

        # Workers (for production deployment)
        self.WORKERS = int(self._get_env('WORKERS', '4'))
        self.WORKER_CLASS = self._get_env('WORKER_CLASS', 'uvicorn.workers.UvicornWorker')

    def _get_required_env(self, key: str) -> str:
        """
        Get required environment variable

        Args:
            key: Environment variable name

        Returns:
            Environment variable value

        Raises:
            ConfigError: If environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ConfigError(
                f"Required environment variable '{key}' is not set. "
                f"Please check your .env file and ensure all required variables are configured."
            )
        return value

    def _get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get optional environment variable with default

        Args:
            key: Environment variable name
            default: Default value if not set

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    def validate(self):
        """
        Validate configuration

        Raises:
            ConfigError: If configuration is invalid
        """
        # Validate database URL
        if not self.DATABASE_URL:
            raise ConfigError("DATABASE_URL is required")

        if not self.DATABASE_URL.startswith('postgresql://'):
            raise ConfigError("DATABASE_URL must be a PostgreSQL connection string")

        # Validate JWT secret
        if not self.JWT_SECRET_KEY:
            raise ConfigError("JWT_SECRET_KEY is required")

        if len(self.JWT_SECRET_KEY) < 32:
            raise ConfigError("JWT_SECRET_KEY must be at least 32 characters long")

        # Validate environment
        if self.ENVIRONMENT not in ['development', 'staging', 'production']:
            raise ConfigError(f"Invalid ENVIRONMENT: {self.ENVIRONMENT}")

    def __repr__(self):
        """String representation (hides secrets)"""
        return (
            f"Config("
            f"ENVIRONMENT={self.ENVIRONMENT}, "
            f"DEBUG={self.DEBUG}, "
            f"LOG_LEVEL={self.LOG_LEVEL}, "
            f"DATABASE_TYPE={self.DATABASE_TYPE}, "
            f"CACHE_ENABLED={self.CACHE_ENABLED}, "
            f"SENTRY_ENABLED={self.SENTRY_ENABLED}, "
            f"JWT_SECRET_KEY=*****, "
            f"ANTHROPIC_API_KEY={'set' if self.ANTHROPIC_API_KEY else 'not set'}"
            f")"
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance

    Returns:
        Config instance

    Raises:
        ConfigError: If configuration is invalid
    """
    global _config

    if _config is None:
        _config = Config()
        _config.validate()

    return _config


def reload_config():
    """
    Reload configuration from environment variables
    Useful for testing
    """
    global _config
    _config = None
    return get_config()


# Load configuration on module import (fail fast)
try:
    config = get_config()
    print(f"✅ Configuration loaded successfully: {config}")
except ConfigError as e:
    print(f"❌ Configuration error: {e}")
    print("Please check your .env file and ensure all required variables are set.")
    raise
