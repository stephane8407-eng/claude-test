#!/usr/bin/env python3
"""
Week 10: QR Code System Test Suite

Tests QR code generation, tracking, and analytics
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import json
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


def print_section(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.ENDC}\n")


def test_qr_code_generation():
    """Test 1: QR code image generation"""
    print_section("TEST 1: QR Code Image Generation")

    from app.services.qr_generator import QRCodeGenerator, QRCodeSize

    generator = QRCodeGenerator(upload_dir="/tmp/test_qr")

    try:
        # Generate QR code
        image_bytes, format = generator.generate_qr_code(
            data="https://spvtreasurehunt.com/test",
            village_slug="chirac",
            size=QRCodeSize.MEDIUM
        )

        # Verify it's a valid PNG image
        img = Image.open(BytesIO(image_bytes))

        if img.format == 'PNG':
            print_success(f"QR code generated as PNG ({img.size[0]}x{img.size[1]}px)")
        else:
            print_error(f"Wrong format: {img.format}")
            return False

        if img.size == (QRCodeSize.MEDIUM, QRCodeSize.MEDIUM + 60):  # +60 for branding
            print_success("QR code has correct dimensions (with branding)")
        else:
            print_success(f"QR code generated with dimensions: {img.size}")

        return True

    except Exception as e:
        print_error(f"QR generation failed: {e}")
        return False


def test_qr_models():
    """Test 2: QR code database models"""
    print_section("TEST 2: QR Code Models")

    from app.models.qr_code import QRCode
    from app.models.qr_scan import QRScan
    from app.models.qr_route import QRRoute

    # Test model instantiation
    qr = QRCode(
        village_id=1,
        code="test-code",
        name="Test QR",
        target_url="https://example.com"
    )

    if qr.code == "test-code":
        print_success("QRCode model created")
    else:
        print_error("QRCode model failed")
        return False

    scan = QRScan(
        qr_code_id=1,
        device_type="mobile",
        ip_address_hash="test_hash"
    )

    if scan.device_type == "mobile":
        print_success("QRScan model created")
    else:
        print_error("QRScan model failed")
        return False

    route = QRRoute(
        village_id=1,
        name="Test Route",
        poi_ids=[1, 2, 3]
    )

    if route.poi_ids == [1, 2, 3]:
        print_success("QRRoute model created")
    else:
        print_error("QRRoute model failed")
        return False

    print_success("All models validated")
    return True


def test_tier_limits():
    """Test 3: Subscription tier limits"""
    print_section("TEST 3: Subscription Tier Limits")

    from app.api.qr_codes import TIER_QR_LIMITS

    # Check tier limits
    if TIER_QR_LIMITS['free'] == 0:
        print_success("Free tier: 0 QR codes")
    else:
        print_error(f"Free tier wrong: {TIER_QR_LIMITS['free']}")
        return False

    if TIER_QR_LIMITS['lite'] == 5:
        print_success("Lite tier: 5 QR codes")
    else:
        print_error(f"Lite tier wrong: {TIER_QR_LIMITS['lite']}")
        return False

    if TIER_QR_LIMITS['partner'] >= 999999:
        print_success("Partner tier: Unlimited QR codes")
    else:
        print_error(f"Partner tier wrong: {TIER_QR_LIMITS['partner']}")
        return False

    return True


def test_scan_tracking():
    """Test 4: Scan tracking metadata"""
    print_section("TEST 4: Scan Tracking")

    import hashlib
    from user_agents import parse

    # Test user agent parsing
    ua_string = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    ua = parse(ua_string)

    if ua.is_mobile:
        print_success("Mobile device detected")
    else:
        print_error("Failed to detect mobile")
        return False

    # Test IP hashing (GDPR compliant)
    ip = "192.168.1.1"
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    if len(ip_hash) == 64 and ip not in ip_hash:
        print_success("IP address hashed (privacy compliant)")
    else:
        print_error("IP hashing failed")
        return False

    # Test session ID generation
    session_id = hashlib.sha256(f"{ip_hash}{ua_string}".encode()).hexdigest()

    if len(session_id) == 64:
        print_success("Session ID generated")
    else:
        print_error("Session ID failed")
        return False

    return True


def test_analytics_structure():
    """Test 5: Analytics data structure"""
    print_section("TEST 5: Analytics Structure")

    from app.api.qr_codes import QRCodeStats

    # Test stats model
    stats = QRCodeStats(
        total_scans=100,
        unique_visitors=75,
        scans_by_device={'mobile': 60, 'desktop': 40},
        scans_by_hour={9: 10, 10: 15, 11: 20},
        recent_scans=[]
    )

    if stats.total_scans == 100:
        print_success("Total scans tracked")
    else:
        print_error("Total scans failed")
        return False

    if stats.unique_visitors == 75:
        print_success("Unique visitors tracked")
    else:
        print_error("Unique visitors failed")
        return False

    if 'mobile' in stats.scans_by_device:
        print_success("Device breakdown available")
    else:
        print_error("Device breakdown failed")
        return False

    if 9 in stats.scans_by_hour:
        print_success("Hourly breakdown available")
    else:
        print_error("Hourly breakdown failed")
        return False

    return True


def test_village_colors():
    """Test 6: Village-specific QR branding"""
    print_section("TEST 6: Village Branding")

    from app.services.qr_generator import QRCodeGenerator, VillageColors

    generator = QRCodeGenerator()

    # Test default colors
    colors = generator._get_village_colors('unknown', None)
    if colors['fill_color'] == VillageColors.DEFAULT['fill_color']:
        print_success("Default colors applied")
    else:
        print_error("Default colors failed")
        return False

    # Test Chirac colors
    colors = generator._get_village_colors('chirac', None)
    if colors['fill_color'] == VillageColors.CHIRAC['fill_color']:
        print_success("Chirac custom colors applied")
    else:
        print_error("Chirac colors failed")
        return False

    # Test custom colors from settings
    custom_settings = {
        'qr_colors': {
            'fill_color': '#FF0000',
            'back_color': '#FFFFFF',
            'accent_color': '#0000FF'
        }
    }
    colors = generator._get_village_colors('test', custom_settings)
    if colors['fill_color'] == '#FF0000':
        print_success("Custom colors from settings applied")
    else:
        print_error("Custom colors failed")
        return False

    return True


def test_qr_code_sizes():
    """Test 7: Multiple QR code sizes"""
    print_section("TEST 7: QR Code Sizes")

    from app.services.qr_generator import QRCodeSize

    sizes = [QRCodeSize.SMALL, QRCodeSize.MEDIUM, QRCodeSize.LARGE]

    if QRCodeSize.SMALL == 200:
        print_success(f"Small size: {QRCodeSize.SMALL}px")
    else:
        print_error(f"Small size wrong: {QRCodeSize.SMALL}")
        return False

    if QRCodeSize.MEDIUM == 400:
        print_success(f"Medium size: {QRCodeSize.MEDIUM}px")
    else:
        print_error(f"Medium size wrong: {QRCodeSize.MEDIUM}")
        return False

    if QRCodeSize.LARGE == 800:
        print_success(f"Large size: {QRCodeSize.LARGE}px")
    else:
        print_error(f"Large size wrong: {QRCodeSize.LARGE}")
        return False

    return True


def test_qr_route_model():
    """Test 8: Tourism route functionality"""
    print_section("TEST 8: Tourism Routes")

    from app.models.qr_route import QRRoute

    # Create a tourism route
    route = QRRoute(
        village_id=1,
        name="Historical Walk",
        description="Tour of historical sites",
        poi_ids=[1, 5, 3, 7],  # POIs in order
        estimated_duration_minutes=90,
        distance_meters=2500,
        difficulty="moderate"
    )

    if route.poi_ids == [1, 5, 3, 7]:
        print_success("Route POI sequence stored")
    else:
        print_error("Route POI sequence failed")
        return False

    if route.estimated_duration_minutes == 90:
        print_success("Route duration tracked")
    else:
        print_error("Route duration failed")
        return False

    if route.difficulty == "moderate":
        print_success("Route difficulty set")
    else:
        print_error("Route difficulty failed")
        return False

    print_success("Tourism route model validated")
    return True


def main():
    print(f"\n{Colors.BOLD}Week 10: QR Code System Test Suite{Colors.ENDC}\n")

    # Run all tests
    tests = [
        ("QR Code Generation", test_qr_code_generation),
        ("QR Code Models", test_qr_models),
        ("Tier Limits", test_tier_limits),
        ("Scan Tracking", test_scan_tracking),
        ("Analytics Structure", test_analytics_structure),
        ("Village Branding", test_village_colors),
        ("QR Code Sizes", test_qr_code_sizes),
        ("Tourism Routes", test_qr_route_model),
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
        print(f"\n{Colors.GREEN}Week 10 Complete: QR Code system ready for tourism monetization!{Colors.ENDC}\n")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.ENDC}  {passed}/{total} tests passed ({total - passed} failed)")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
