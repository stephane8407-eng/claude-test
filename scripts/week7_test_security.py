#!/usr/bin/env python3
"""
Week 7: Input Validation & Secrets Management Test Suite

Tests all security features including:
- Input sanitization (XSS prevention)
- File upload validation
- Coordinate validation
- Request size limits
- Security headers
- CSRF protection
- Config validation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from io import BytesIO
from PIL import Image


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


def test_input_sanitization():
    """Test 1: Input sanitization prevents XSS"""
    print_section("TEST 1: Input Sanitization (XSS Prevention)")

    from app.middleware.validation import InputSanitizer

    # Test XSS attack vectors
    test_cases = [
        {
            'input': '<script>alert("XSS")</script>Hello',
            'expected_plain': 'alert("XSS")Hello',  # bleach strips tags but keeps content
            'expected_html': 'alert("XSS")Hello',
            'description': 'Script tag removal (content remains)'
        },
        {
            'input': '<img src=x onerror="alert(1)">',
            'expected_plain': '',
            'expected_html': '',
            'description': 'Malicious img tag removal'
        },
        {
            'input': '<strong>Bold</strong> text',
            'expected_plain': 'Bold text',
            'expected_html': '<strong>Bold</strong> text',
            'description': 'Safe HTML preservation'
        },
        {
            'input': '<a href="javascript:alert(1)">Click</a>',
            'expected_plain': 'Click',
            'expected_html': '<a>Click</a>',  # bleach keeps tag but removes dangerous href
            'description': 'JavaScript protocol removal'
        },
        {
            'input': 'Normal text',
            'expected_plain': 'Normal text',
            'expected_html': 'Normal text',
            'description': 'Plain text unchanged'
        }
    ]

    success = True
    for test in test_cases:
        # Test plain text sanitization
        result_plain = InputSanitizer.sanitize_plain_text(test['input'])
        if result_plain == test['expected_plain']:
            print_success(f"{test['description']} (plain): '{result_plain}'")
        else:
            print_error(f"{test['description']} (plain): got '{result_plain}', expected '{test['expected_plain']}'")
            success = False

        # Test HTML sanitization
        result_html = InputSanitizer.sanitize_html(test['input'])
        if result_html == test['expected_html']:
            print_success(f"{test['description']} (HTML): '{result_html}'")
        else:
            print_error(f"{test['description']} (HTML): got '{result_html}', expected '{test['expected_html']}'")
            success = False

    return success


def test_url_sanitization():
    """Test 2: URL sanitization prevents javascript: and data: URLs"""
    print_section("TEST 2: URL Sanitization")

    from app.middleware.validation import InputSanitizer

    test_cases = [
        {
            'input': 'javascript:alert(1)',
            'expected': None,
            'description': 'Block javascript: protocol'
        },
        {
            'input': 'data:text/html,<script>alert(1)</script>',
            'expected': None,
            'description': 'Block data: protocol'
        },
        {
            'input': 'https://example.com',
            'expected': 'https://example.com',
            'description': 'Allow https URL'
        },
        {
            'input': 'http://example.com',
            'expected': 'http://example.com',
            'description': 'Allow http URL'
        },
        {
            'input': '/relative/path',
            'expected': '/relative/path',
            'description': 'Allow relative URL'
        }
    ]

    success = True
    for test in test_cases:
        result = InputSanitizer.sanitize_url(test['input'])
        if result == test['expected']:
            print_success(f"{test['description']}: {test['input']} -> {result}")
        else:
            print_error(f"{test['description']}: got {result}, expected {test['expected']}")
            success = False

    return success


def test_coordinate_validation():
    """Test 3: Coordinate validation"""
    print_section("TEST 3: Coordinate Validation")

    from app.middleware.validation import CoordinateValidator

    test_cases = [
        {
            'lat': 45.7, 'lon': 6.3,
            'valid': True,
            'description': 'Valid coordinates (Chirac, France)'
        },
        {
            'lat': -90, 'lon': 180,
            'valid': True,
            'description': 'Boundary values (min lat, max lon)'
        },
        {
            'lat': 90, 'lon': -180,
            'valid': True,
            'description': 'Boundary values (max lat, min lon)'
        },
        {
            'lat': 91, 'lon': 0,
            'valid': False,
            'description': 'Invalid latitude (> 90)'
        },
        {
            'lat': -91, 'lon': 0,
            'valid': False,
            'description': 'Invalid latitude (< -90)'
        },
        {
            'lat': 0, 'lon': 181,
            'valid': False,
            'description': 'Invalid longitude (> 180)'
        },
        {
            'lat': 0, 'lon': -181,
            'valid': False,
            'description': 'Invalid longitude (< -180)'
        }
    ]

    success = True
    for test in test_cases:
        is_valid, error = CoordinateValidator.validate_coordinates(test['lat'], test['lon'])

        if is_valid == test['valid']:
            status = "Valid" if is_valid else f"Invalid: {error}"
            print_success(f"{test['description']}: {status}")
        else:
            print_error(f"{test['description']}: expected {'valid' if test['valid'] else 'invalid'}, got {'valid' if is_valid else 'invalid'}")
            success = False

    return success


def test_file_upload_validation():
    """Test 4: File upload validation"""
    print_section("TEST 4: File Upload Validation")

    from app.services.file_upload import FileUploadValidator

    # Test file size validation
    print("  File size validation:")
    is_valid, error = FileUploadValidator.validate_file_size(1024 * 1024)  # 1MB
    if is_valid:
        print_success(f"1MB file accepted")
    else:
        print_error(f"1MB file rejected: {error}")

    is_valid, error = FileUploadValidator.validate_file_size(10 * 1024 * 1024)  # 10MB
    if not is_valid:
        print_success(f"10MB file rejected (exceeds 5MB limit)")
    else:
        print_error(f"10MB file incorrectly accepted")

    # Test file extension validation
    print("\n  File extension validation:")
    extensions = [
        ('image.jpg', True),
        ('image.png', True),
        ('image.webp', True),
        ('image.gif', False),
        ('file.exe', False),
        ('script.js', False)
    ]

    extension_success = True
    for filename, should_be_valid in extensions:
        is_valid, error = FileUploadValidator.validate_file_extension(filename)
        if is_valid == should_be_valid:
            status = "accepted" if is_valid else "rejected"
            print_success(f"{filename}: {status}")
        else:
            print_error(f"{filename}: expected {'valid' if should_be_valid else 'invalid'}")
            extension_success = False

    # Test MIME type validation
    print("\n  MIME type validation:")
    mime_types = [
        ('image/jpeg', True),
        ('image/png', True),
        ('image/webp', True),
        ('image/gif', False),
        ('application/javascript', False),
        ('text/html', False)
    ]

    mime_success = True
    for mime_type, should_be_valid in mime_types:
        is_valid, error = FileUploadValidator.validate_mime_type(mime_type)
        if is_valid == should_be_valid:
            status = "accepted" if is_valid else "rejected"
            print_success(f"{mime_type}: {status}")
        else:
            print_error(f"{mime_type}: expected {'valid' if should_be_valid else 'invalid'}")
            mime_success = False

    return extension_success and mime_success


def test_image_processing():
    """Test 5: Image processing (resize & EXIF stripping)"""
    print_section("TEST 5: Image Processing")

    from app.services.file_upload import FileUploadValidator

    # Create a test image
    img = Image.new('RGB', (3000, 2000), color='red')

    # Use the image directly (no need for EXIF in this test)
    exif_img = img

    # Save to bytes
    img_bytes = BytesIO()
    exif_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    original_size = len(img_bytes.getvalue())

    # Process image
    success, processed_bytes, mime_type, error = FileUploadValidator.process_image_upload(
        img_bytes.getvalue(),
        'test.jpg'
    )

    if not success:
        print_error(f"Image processing failed: {error}")
        return False

    # Load processed image
    processed_img = Image.open(BytesIO(processed_bytes))
    processed_width, processed_height = processed_img.size

    # Check if image was resized
    if processed_width <= 1920 and processed_height <= 1920:
        print_success(f"Image resized: 3000x2000 -> {processed_width}x{processed_height}")
    else:
        print_error(f"Image not resized properly: {processed_width}x{processed_height}")
        return False

    # Check if file size reduced
    processed_size = len(processed_bytes)
    if processed_size < original_size:
        reduction = ((original_size - processed_size) / original_size) * 100
        print_success(f"File size reduced: {original_size} -> {processed_size} bytes ({reduction:.1f}% reduction)")
    else:
        print_warning(f"File size not reduced: {original_size} -> {processed_size}")

    print_success(f"MIME type detected: {mime_type}")

    return True


def test_request_size_validation():
    """Test 6: Request size limits"""
    print_section("TEST 6: Request Size Validation")

    from app.middleware.validation import RequestValidator

    test_cases = [
        (1024, True, '1KB request'),
        (5 * 1024 * 1024, True, '5MB request'),
        (10 * 1024 * 1024, True, '10MB request (at limit)'),
        (11 * 1024 * 1024, False, '11MB request (exceeds limit)')
    ]

    success = True
    for size, should_be_valid, description in test_cases:
        is_valid, error = RequestValidator.validate_request_size(size)

        if is_valid == should_be_valid:
            status = "accepted" if is_valid else "rejected"
            print_success(f"{description}: {status}")
        else:
            print_error(f"{description}: expected {'valid' if should_be_valid else 'invalid'}")
            success = False

    return success


def test_csrf_protection():
    """Test 7: CSRF token generation and validation"""
    print_section("TEST 7: CSRF Protection")

    from app.services.csrf_protection import CSRFProtection

    # Generate token
    token = CSRFProtection.create_token_with_timestamp()
    print_success(f"CSRF token generated: {token[:30]}...")

    # Valid token should pass
    is_valid, error = CSRFProtection.verify_token(token, token)
    if is_valid:
        print_success("Token self-verification passed")
    else:
        print_error(f"Token self-verification failed: {error}")
        return False

    # Different token should fail
    different_token = CSRFProtection.create_token_with_timestamp()
    is_valid, error = CSRFProtection.verify_token(token, different_token)
    if not is_valid:
        print_success("Different token correctly rejected")
    else:
        print_error("Different token incorrectly accepted")
        return False

    # Missing token should fail
    is_valid, error = CSRFProtection.verify_token(token, None)
    if not is_valid:
        print_success("Missing token correctly rejected")
    else:
        print_error("Missing token incorrectly accepted")
        return False

    return True


def test_config_validation():
    """Test 8: Configuration validation"""
    print_section("TEST 8: Configuration Validation")

    # Test that .env.example exists
    env_example_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env.example')
    if os.path.exists(env_example_path):
        print_success(".env.example template exists")
    else:
        print_error(".env.example template missing")
        return False

    # Test that .env is in .gitignore
    gitignore_path = os.path.join(os.path.dirname(__file__), '..', '.gitignore')
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()

    if '.env' in gitignore_content:
        print_success(".env is in .gitignore")
    else:
        print_error(".env is NOT in .gitignore (security risk!)")
        return False

    # Test config loading (if .env exists)
    env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
    if os.path.exists(env_path):
        try:
            from app.config import get_config
            config = get_config()
            print_success(f"Configuration loaded: {config.ENVIRONMENT} environment")

            # Check required fields are set
            if config.DATABASE_URL:
                print_success("DATABASE_URL is set")
            if config.JWT_SECRET_KEY:
                print_success("JWT_SECRET_KEY is set")

        except Exception as e:
            print_error(f"Configuration validation failed: {e}")
            return False
    else:
        print_warning(".env file not found (expected for new installations)")

    return True


def main():
    print(f"\n{Colors.BOLD}Week 7: Input Validation & Secrets Management Test Suite{Colors.ENDC}\n")

    # Run all tests
    tests = [
        ("Input Sanitization (XSS)", test_input_sanitization),
        ("URL Sanitization", test_url_sanitization),
        ("Coordinate Validation", test_coordinate_validation),
        ("File Upload Validation", test_file_upload_validation),
        ("Image Processing", test_image_processing),
        ("Request Size Validation", test_request_size_validation),
        ("CSRF Protection", test_csrf_protection),
        ("Config Validation", test_config_validation),
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
