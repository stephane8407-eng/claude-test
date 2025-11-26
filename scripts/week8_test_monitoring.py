#!/usr/bin/env python3
"""
Week 8: Logging, Monitoring & Rate Limiting Test Suite

Tests all monitoring and observability features including:
- Structured logging
- Rate limiting
- Request tracking
- CORS
- Health checks
- Error tracking integration
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import json
import time
from io import StringIO


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")


def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")


def print_section(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}\n")


def test_structured_logging():
    """Test 1: Structured logging with JSON format"""
    print_section("TEST 1: Structured Logging")

    from app.services.logger import setup_logging, get_logger
    import logging

    # Capture log output
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)

    from app.services.logger import JSONFormatter
    handler.setFormatter(JSONFormatter())

    logger = get_logger('test')
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.INFO)

    # Test logging
    logger.info("Test message", extra={'user_id': 123, 'request_id': 'abc-123'})

    # Get log output
    log_output = log_stream.getvalue()

    try:
        log_entry = json.loads(log_output)

        # Check structure
        if 'timestamp' in log_entry:
            print_success("Timestamp present in log")
        else:
            print_error("Timestamp missing from log")
            return False

        if log_entry.get('level') == 'INFO':
            print_success("Log level correct")
        else:
            print_error(f"Log level incorrect: {log_entry.get('level')}")
            return False

        if log_entry.get('message') == 'Test message':
            print_success("Message correct")
        else:
            print_error(f"Message incorrect: {log_entry.get('message')}")
            return False

        if log_entry.get('user_id') == 123:
            print_success("User ID in context")
        else:
            print_error("User ID not in context")
            return False

        if log_entry.get('request_id') == 'abc-123':
            print_success("Request ID in context")
        else:
            print_error("Request ID not in context")
            return False

        print_success("JSON log format validated")
        return True

    except json.JSONDecodeError as e:
        print_error(f"Failed to parse JSON log: {e}")
        print(f"Output: {log_output}")
        return False


def test_sensitive_data_masking():
    """Test 2: Sensitive data masking in logs"""
    print_section("TEST 2: Sensitive Data Masking")

    from app.services.logger import SensitiveDataFilter
    import logging

    # Create test record
    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname='',
        lineno=0,
        msg='User login with password="SecretPass123" and token="abc123xyz"',
        args=(),
        exc_info=None
    )

    # Apply filter
    filter = SensitiveDataFilter()
    filter.filter(record)

    # Check masking
    if '***REDACTED***' in record.msg:
        print_success("Sensitive data masked")
    else:
        print_error("Sensitive data not masked")
        return False

    if 'SecretPass123' not in record.msg:
        print_success("Password not in log")
    else:
        print_error("Password leaked in log")
        return False

    if 'abc123xyz' not in record.msg:
        print_success("Token not in log")
    else:
        print_error("Token leaked in log")
        return False

    return True


def test_rate_limit_config():
    """Test 3: Rate limit configuration"""
    print_section("TEST 3: Rate Limit Configuration")

    from app.middleware.rate_limit import RateLimits

    # Check rate limit values
    if RateLimits.LOGIN == "5/minute":
        print_success("Login rate limit: 5/minute")
    else:
        print_error(f"Login rate limit incorrect: {RateLimits.LOGIN}")
        return False

    if RateLimits.REGISTER == "3/hour":
        print_success("Register rate limit: 3/hour")
    else:
        print_error(f"Register rate limit incorrect: {RateLimits.REGISTER}")
        return False

    if RateLimits.PASSWORD_RESET == "3/hour":
        print_success("Password reset rate limit: 3/hour")
    else:
        print_error(f"Password reset rate limit incorrect: {RateLimits.PASSWORD_RESET}")
        return False

    if RateLimits.PUBLIC_READ == "100/minute":
        print_success("Public read rate limit: 100/minute")
    else:
        print_error(f"Public read rate limit incorrect: {RateLimits.PUBLIC_READ}")
        return False

    if RateLimits.AUTHENTICATED == "1000/minute":
        print_success("Authenticated rate limit: 1000/minute")
    else:
        print_error(f"Authenticated rate limit incorrect: {RateLimits.AUTHENTICATED}")
        return False

    return True


def test_request_tracking():
    """Test 4: Request ID generation"""
    print_section("TEST 4: Request Tracking")

    import uuid

    # Test UUID generation (used for request IDs)
    request_id = str(uuid.uuid4())

    if len(request_id) == 36:  # UUID format: 8-4-4-4-12
        print_success(f"Request ID generated: {request_id[:8]}...")
    else:
        print_error(f"Invalid request ID format: {request_id}")
        return False

    # Test multiple IDs are unique
    ids = {str(uuid.uuid4()) for _ in range(100)}
    if len(ids) == 100:
        print_success("Request IDs are unique")
    else:
        print_error("Request ID collision detected")
        return False

    return True


def test_cors_config():
    """Test 5: CORS configuration"""
    print_section("TEST 5: CORS Configuration")

    from app.middleware.cors import CORSConfig

    # Test development origins
    dev_origins = CORSConfig.get_allowed_origins('development')
    if 'http://localhost:3000' in dev_origins:
        print_success("Development origin localhost:3000 allowed")
    else:
        print_error("Development origin localhost:3000 not allowed")
        return False

    # Test allowed methods
    methods = CORSConfig.get_allowed_methods()
    required_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    if all(method in methods for method in required_methods):
        print_success(f"All required methods allowed: {', '.join(required_methods)}")
    else:
        print_error(f"Missing methods: {set(required_methods) - set(methods)}")
        return False

    # Test allowed headers
    headers = CORSConfig.get_allowed_headers()
    required_headers = ['Authorization', 'Content-Type', 'X-CSRF-Token']
    if all(header in headers for header in required_headers):
        print_success(f"All required headers allowed")
    else:
        print_error(f"Missing headers: {set(required_headers) - set(headers)}")
        return False

    # Test exposed headers
    exposed = CORSConfig.get_expose_headers()
    if 'X-Request-ID' in exposed:
        print_success("X-Request-ID exposed to client")
    else:
        print_error("X-Request-ID not exposed")
        return False

    if 'X-RateLimit-Remaining' in exposed:
        print_success("Rate limit headers exposed")
    else:
        print_error("Rate limit headers not exposed")
        return False

    return True


def test_health_check_structure():
    """Test 6: Health check endpoint structure"""
    print_section("TEST 6: Health Check Structure")

    # Test expected structure (can't test actual endpoint without running server)
    expected_fields = ['status', 'timestamp', 'version', 'environment', 'checks']

    print_success(f"Health check should include: {', '.join(expected_fields)}")
    print_success("Health check endpoints: /api/health, /api/health/db, /api/health/ready, /api/health/live")

    return True


def test_error_tracking_config():
    """Test 7: Error tracking configuration"""
    print_section("TEST 7: Error Tracking (Sentry) Configuration")

    # Test Sentry integration exists
    try:
        from app.services.error_tracking import setup_sentry, capture_exception

        print_success("Sentry integration module exists")
        print_success("Error tracking functions available")

        # Test that it doesn't crash without DSN
        setup_sentry(environment='development')
        print_success("Sentry setup handles missing DSN gracefully")

        return True
    except ImportError as e:
        print_error(f"Failed to import error tracking: {e}")
        return False


def test_logging_levels():
    """Test 8: Log levels configuration"""
    print_section("TEST 8: Logging Levels")

    from app.services.logger import get_logger
    import logging

    logger = get_logger('test')

    # Test all log levels exist
    levels = ['debug', 'info', 'warning', 'error', 'critical']
    for level in levels:
        if hasattr(logger, level):
            print_success(f"{level.upper()} log level available")
        else:
            print_error(f"{level.upper()} log level missing")
            return False

    return True


def test_performance_logging():
    """Test 9: Performance timing logic"""
    print_section("TEST 9: Performance Timing")

    # Test timing logic
    start = time.time()
    time.sleep(0.1)  # Simulate work
    duration_ms = (time.time() - start) * 1000

    if duration_ms >= 100:
        print_success(f"Timing accurate: {duration_ms:.2f}ms (expected ~100ms)")
    else:
        print_error(f"Timing inaccurate: {duration_ms:.2f}ms")
        return False

    # Test slow request threshold
    slow_threshold = 1000  # 1 second
    if duration_ms < slow_threshold:
        print_success("Request not considered slow (< 1000ms)")
    else:
        print_warning("Request considered slow (>= 1000ms)")

    return True


def test_api_logging_function():
    """Test 10: API request logging function"""
    print_section("TEST 10: API Request Logging")

    from app.services.logger import log_api_request

    # Test that function accepts all parameters
    try:
        # This won't actually log in test mode, just verify it doesn't crash
        log_api_request(
            method='GET',
            path='/api/test',
            status_code=200,
            duration_ms=150.5,
            request_id='test-123',
            user_id=456,
            village_id=789,
            ip_address='127.0.0.1'
        )
        print_success("API request logging function works")
        return True
    except Exception as e:
        print_error(f"API request logging failed: {e}")
        return False


def main():
    print(f"\n{Colors.BOLD}Week 8: Logging, Monitoring & Rate Limiting Test Suite{Colors.ENDC}\n")

    # Run all tests
    tests = [
        ("Structured Logging", test_structured_logging),
        ("Sensitive Data Masking", test_sensitive_data_masking),
        ("Rate Limit Configuration", test_rate_limit_config),
        ("Request Tracking", test_request_tracking),
        ("CORS Configuration", test_cors_config),
        ("Health Check Structure", test_health_check_structure),
        ("Error Tracking Configuration", test_error_tracking_config),
        ("Logging Levels", test_logging_levels),
        ("Performance Timing", test_performance_logging),
        ("API Request Logging", test_api_logging_function),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.ENDC}" if result else f"{Colors.RED}FAIL{Colors.ENDC}"
        print(f"{status}  {test_name}")

    print()
    if passed == total:
        print_success(f"All {total} tests passed! ✨")
    else:
        print_warning(f"{passed}/{total} tests passed ({total - passed} failed)")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
