"""
Error tracking with Sentry integration
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from typing import Optional
import os


def setup_sentry(
    environment: str = 'development',
    dsn: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1
):
    """
    Setup Sentry error tracking

    Args:
        environment: Environment name (development, staging, production)
        dsn: Sentry DSN (Data Source Name)
        traces_sample_rate: Percentage of transactions to trace (0.0 to 1.0)
        profiles_sample_rate: Percentage of transactions to profile (0.0 to 1.0)
    """
    # Get DSN from environment variable if not provided
    if dsn is None:
        dsn = os.getenv('SENTRY_DSN')

    # Don't initialize Sentry in development without explicit DSN
    if environment == 'development' and not dsn:
        print("⚠️  Sentry not initialized (no DSN in development)")
        return

    if not dsn:
        print("⚠️  Sentry DSN not configured - error tracking disabled")
        return

    # Initialize Sentry
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        # Integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        # Performance monitoring
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        # Release tracking
        release=os.getenv('APP_VERSION', 'dev'),
        # Error filtering
        before_send=before_send_filter,
        # Additional options
        attach_stacktrace=True,
        send_default_pii=False,  # Don't send personally identifiable info
    )

    print(f"✅ Sentry initialized for environment: {environment}")


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry

    Args:
        event: Sentry event
        hint: Additional information

    Returns:
        Event to send or None to drop
    """
    # Don't send certain error types
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']

        # Don't send 404 errors
        if exc_type.__name__ == 'HTTPException':
            if hasattr(exc_value, 'status_code') and exc_value.status_code == 404:
                return None

        # Don't send validation errors
        if exc_type.__name__ == 'ValidationError':
            return None

    return event


def capture_exception(error: Exception, context: Optional[dict] = None):
    """
    Capture exception in Sentry with context

    Args:
        error: Exception to capture
        context: Additional context information
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            # Add context
            for key, value in context.items():
                scope.set_extra(key, value)

            # Capture exception
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = 'info', context: Optional[dict] = None):
    """
    Capture message in Sentry

    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context information
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            # Add context
            for key, value in context.items():
                scope.set_extra(key, value)

            # Capture message
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: int, email: Optional[str] = None, username: Optional[str] = None):
    """
    Set user context for error tracking

    Args:
        user_id: User ID
        email: User email (optional)
        username: Username (optional)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username
    })


def set_request_context(request_id: str, path: str, method: str):
    """
    Set request context for error tracking

    Args:
        request_id: Unique request ID
        path: Request path
        method: HTTP method
    """
    sentry_sdk.set_context("request", {
        "request_id": request_id,
        "path": path,
        "method": method
    })


def add_breadcrumb(message: str, category: str = 'default', level: str = 'info', data: Optional[dict] = None):
    """
    Add breadcrumb for error context

    Args:
        message: Breadcrumb message
        category: Breadcrumb category
        level: Severity level
        data: Additional data
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )


def start_transaction(name: str, op: str = 'http.server'):
    """
    Start performance transaction

    Args:
        name: Transaction name
        op: Operation type

    Returns:
        Transaction context manager
    """
    return sentry_sdk.start_transaction(name=name, op=op)


class SentryMiddleware:
    """
    Middleware to add Sentry context to requests
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """Process request with Sentry context"""
        if scope['type'] == 'http':
            # Add request context
            path = scope.get('path', '')
            method = scope.get('method', '')

            # Start transaction
            with sentry_sdk.start_transaction(
                op="http.server",
                name=f"{method} {path}"
            ):
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)
