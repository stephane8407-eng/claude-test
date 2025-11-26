"""
Configuration management with environment variables
Loads and validates configuration from .env file
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


class Config:
    """
    Application configuration loaded from environment variables
    """

    def __init__(self):
        """Load configuration from .env file"""
        # Load .env file from backend directory
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)

        # Load and validate required configuration
        # Load app config first to set ENVIRONMENT
        self._load_app_config()
        self._load_database_config()
        self._load_security_config()
        self._load_api_keys()

    def _load_database_config(self):
        """Load database configuration"""
        self.DATABASE_URL = self._get_required_env('DATABASE_URL')

        # Parse database URL for individual components (optional)
        if self.DATABASE_URL.startswith('postgresql://'):
            self.DATABASE_TYPE = 'postgresql'
        else:
            self.DATABASE_TYPE = 'unknown'

    def _load_security_config(self):
        """Load security configuration"""
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

        # CORS settings
        self.CORS_ORIGINS = self._get_env('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8000')
        self.CORS_ORIGINS_LIST = [origin.strip() for origin in self.CORS_ORIGINS.split(',')]

    def _load_api_keys(self):
        """Load external API keys"""
        # Anthropic Claude API (required for identity generation)
        self.ANTHROPIC_API_KEY = self._get_env('ANTHROPIC_API_KEY')
        if not self.ANTHROPIC_API_KEY:
            print("⚠️  WARNING: ANTHROPIC_API_KEY not set - AI identity generation will fail")

        # Google API keys (optional for web scraping)
        self.GOOGLE_API_KEY = self._get_env('GOOGLE_API_KEY')
        self.GOOGLE_CSE_ID = self._get_env('GOOGLE_CSE_ID')

    def _load_app_config(self):
        """Load application configuration"""
        self.ENVIRONMENT = self._get_env('ENVIRONMENT', 'development')
        self.DEBUG = self.ENVIRONMENT == 'development'

        # File upload settings
        self.MAX_FILE_SIZE_MB = int(self._get_env('MAX_FILE_SIZE_MB', '5'))
        self.MAX_REQUEST_SIZE_MB = int(self._get_env('MAX_REQUEST_SIZE_MB', '10'))

        # Image processing settings
        self.MAX_IMAGE_WIDTH = int(self._get_env('MAX_IMAGE_WIDTH', '1920'))
        self.MAX_IMAGE_HEIGHT = int(self._get_env('MAX_IMAGE_HEIGHT', '1920'))

        # Security headers
        self.ENABLE_SECURITY_HEADERS = self._get_env('ENABLE_SECURITY_HEADERS', 'true').lower() == 'true'

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
            f"DATABASE_TYPE={self.DATABASE_TYPE}, "
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
