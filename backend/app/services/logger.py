"""
Structured logging service with JSON formatting and context tracking
"""
import logging
import json
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
import re


class SensitiveDataFilter(logging.Filter):
    """
    Filter to mask sensitive data in logs
    """

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'password="***REDACTED***"'),
        (r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'token="***REDACTED***"'),
        (r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'api_key="***REDACTED***"'),
        (r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'secret="***REDACTED***"'),
        (r'authorization:\s*bearer\s+\S+', 'authorization: bearer ***REDACTED***'),
        (r'sk-ant-api\d+-[a-zA-Z0-9_-]+', 'sk-ant-api03-***REDACTED***'),  # Anthropic API keys
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Mask sensitive data in log message

        Args:
            record: Log record to filter

        Returns:
            True to allow log record (always returns True after filtering)
        """
        if isinstance(record.msg, str):
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                record.msg = re.sub(pattern, replacement, record.msg, flags=re.IGNORECASE)

        # Also filter args if present
        if hasattr(record, 'args') and record.args:
            filtered_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in self.SENSITIVE_PATTERNS:
                        arg = re.sub(pattern, replacement, arg, flags=re.IGNORECASE)
                filtered_args.append(arg)
            record.args = tuple(filtered_args)

        return True


class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON for structured logging
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON

        Args:
            record: Log record to format

        Returns:
            JSON formatted log string
        """
        # Build log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add context if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id

        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id

        if hasattr(record, 'village_id'):
            log_entry['village_id'] = record.village_id

        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address

        if hasattr(record, 'method'):
            log_entry['method'] = record.method

        if hasattr(record, 'path'):
            log_entry['path'] = record.path

        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code

        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)


class ContextLogger:
    """
    Logger with context management for request tracking
    """

    def __init__(self, name: str):
        """
        Initialize context logger

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self.context = {}

    def set_context(self, **kwargs):
        """
        Set context for all subsequent logs

        Args:
            **kwargs: Context key-value pairs
        """
        self.context.update(kwargs)

    def clear_context(self):
        """Clear all context"""
        self.context = {}

    def _log(self, level: int, message: str, **kwargs):
        """
        Internal log method with context

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional fields
        """
        # Merge context and kwargs (remove 'extra' key if present)
        extra_dict = kwargs.pop('extra', {})
        extra = {**self.context, **extra_dict, **kwargs}

        # Pass extra dict to logger
        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, exc_info=None, **kwargs):
        """Log error message"""
        if exc_info:
            kwargs['exc_info'] = exc_info
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, exc_info=None, **kwargs):
        """Log critical message"""
        if exc_info:
            kwargs['exc_info'] = exc_info
        self._log(logging.CRITICAL, message, **kwargs)


def setup_logging(log_level: str = "INFO", json_logs: bool = True):
    """
    Setup application logging

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Use JSON formatter if True, standard formatter otherwise
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Set formatter
    if json_logs:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    console_handler.setFormatter(formatter)

    # Add sensitive data filter
    console_handler.addFilter(SensitiveDataFilter())

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Silence noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('multipart').setLevel(logging.WARNING)


def get_logger(name: str) -> ContextLogger:
    """
    Get a context logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        ContextLogger instance
    """
    return ContextLogger(name)


# Application-level loggers
api_logger = get_logger('api')
auth_logger = get_logger('auth')
db_logger = get_logger('database')
security_logger = get_logger('security')


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: Optional[str] = None,
    user_id: Optional[int] = None,
    village_id: Optional[int] = None,
    ip_address: Optional[str] = None
):
    """
    Log API request with timing

    Args:
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        request_id: Request ID
        user_id: User ID (if authenticated)
        village_id: Village ID (if applicable)
        ip_address: Client IP address
    """
    log_data = {
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_ms': duration_ms,
    }

    if request_id:
        log_data['request_id'] = request_id
    if user_id:
        log_data['user_id'] = user_id
    if village_id:
        log_data['village_id'] = village_id
    if ip_address:
        log_data['ip_address'] = ip_address

    # Log level based on status code
    if status_code >= 500:
        api_logger.error(f"{method} {path} - {status_code}", **log_data)
    elif status_code >= 400:
        api_logger.warning(f"{method} {path} - {status_code}", **log_data)
    else:
        api_logger.info(f"{method} {path} - {status_code}", **log_data)

    # Warn on slow requests
    if duration_ms > 1000:
        api_logger.warning(
            f"Slow request: {method} {path} took {duration_ms}ms",
            **log_data
        )


def log_auth_attempt(
    email: str,
    success: bool,
    ip_address: Optional[str] = None,
    reason: Optional[str] = None,
    request_id: Optional[str] = None
):
    """
    Log authentication attempt

    Args:
        email: Email address
        success: Whether authentication succeeded
        ip_address: Client IP address
        reason: Failure reason (if failed)
        request_id: Request ID
    """
    log_data = {
        'email': email,
        'success': success,
    }

    if ip_address:
        log_data['ip_address'] = ip_address
    if reason:
        log_data['reason'] = reason
    if request_id:
        log_data['request_id'] = request_id

    if success:
        auth_logger.info(f"Authentication successful: {email}", **log_data)
    else:
        auth_logger.warning(f"Authentication failed: {email} - {reason}", **log_data)


def log_error(
    message: str,
    exc_info=None,
    request_id: Optional[str] = None,
    user_id: Optional[int] = None,
    **extra_fields
):
    """
    Log error with context

    Args:
        message: Error message
        exc_info: Exception info (sys.exc_info() result)
        request_id: Request ID
        user_id: User ID
        **extra_fields: Additional fields
    """
    log_data = extra_fields.copy()

    if request_id:
        log_data['request_id'] = request_id
    if user_id:
        log_data['user_id'] = user_id

    if exc_info:
        api_logger.error(message, exc_info=exc_info, **log_data)
    else:
        api_logger.error(message, **log_data)
