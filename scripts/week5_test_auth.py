#!/usr/bin/env python3
"""
Week 5: Authentication System Tests

Comprehensive tests for the authentication system including:
- User registration
- Login with valid/invalid credentials
- Password strength validation
- JWT token authentication
- Protected route access
- Password reset flow
"""

import sys
import os
import requests
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

BASE_URL = "http://localhost:8000"

# Test user data
TEST_USER = {
    "email": f"test_{int(time.time())}@example.com",
    "password": "SecurePassword123",
    "first_name": "Test",
    "last_name": "User"
}

# Village admin test user
TEST_VILLAGE_ADMIN = {
    "email": f"admin_{int(time.time())}@chirac.fr",
    "password": "ChiracAdmin2024!",
    "first_name": "Jacques",
    "last_name": "Chirac",
    "village_slug": "chirac"
}

# Weak password test
WEAK_PASSWORD = "weak"


def print_test_header(test_name: str):
    """Print formatted test header"""
    print()
    print("=" * 80)
    print(f"TEST: {test_name}")
    print("=" * 80)


def print_result(success: bool, message: str):
    """Print test result"""
    symbol = "✓" if success else "✗"
    status = "PASS" if success else "FAIL"
    print(f"  {symbol} {status}: {message}")


def test_password_strength_validation():
    """Test password strength validation"""
    print_test_header("Password Strength Validation")

    # Test weak password (should fail)
    print("\n  Testing weak password (should fail)...")
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": "test@example.com",
            "password": WEAK_PASSWORD
        }
    )

    if response.status_code == 400:
        print_result(True, "Weak password rejected")
        print(f"    Error: {response.json()['detail']}")
    else:
        print_result(False, f"Weak password not rejected (status: {response.status_code})")
        return False

    return True


def test_register_user():
    """Test user registration"""
    print_test_header("User Registration")

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=TEST_USER
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "User registered successfully")
        print(f"    User ID: {data['user']['id']}")
        print(f"    Email: {data['user']['email']}")
        print(f"    Role: {data['user']['role']}")
        print(f"    Token received: {len(data['access_token'])} chars")
        return data['access_token']
    else:
        print_result(False, f"Registration failed: {response.text}")
        return None


def test_register_village_admin():
    """Test village admin registration"""
    print_test_header("Village Admin Registration")

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=TEST_VILLAGE_ADMIN
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Village admin registered successfully")
        print(f"    User ID: {data['user']['id']}")
        print(f"    Email: {data['user']['email']}")
        print(f"    Role: {data['user']['role']}")
        print(f"    Village ID: {data['user']['village_id']}")
        return data['access_token']
    else:
        print_result(False, f"Village admin registration failed: {response.text}")
        return None


def test_duplicate_registration():
    """Test duplicate email registration (should fail)"""
    print_test_header("Duplicate Email Registration (should fail)")

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=TEST_USER
    )

    if response.status_code == 400 and "already registered" in response.text.lower():
        print_result(True, "Duplicate email rejected")
        print(f"    Error: {response.json()['detail']}")
        return True
    else:
        print_result(False, f"Duplicate email not rejected (status: {response.status_code})")
        return False


def test_login_valid():
    """Test login with valid credentials"""
    print_test_header("Login with Valid Credentials")

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Login successful")
        print(f"    Token received: {len(data['access_token'])} chars")
        print(f"    User: {data['user']['email']}")
        return data['access_token']
    else:
        print_result(False, f"Login failed: {response.text}")
        return None


def test_login_invalid():
    """Test login with invalid credentials (should fail)"""
    print_test_header("Login with Invalid Credentials (should fail)")

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": "WrongPassword123"
        }
    )

    if response.status_code == 401:
        print_result(True, "Invalid credentials rejected")
        print(f"    Error: {response.json()['detail']}")
        return True
    else:
        print_result(False, f"Invalid credentials not rejected (status: {response.status_code})")
        return False


def test_get_current_user(token: str):
    """Test getting current user profile"""
    print_test_header("Get Current User Profile")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "User profile retrieved")
        print(f"    Email: {data['email']}")
        print(f"    Role: {data['role']}")
        print(f"    Active: {data['is_active']}")
        return True
    else:
        print_result(False, f"Failed to get user profile: {response.text}")
        return False


def test_protected_route_without_token():
    """Test accessing protected route without token (should fail)"""
    print_test_header("Access Protected Route Without Token (should fail)")

    response = requests.get(f"{BASE_URL}/api/auth/me")

    if response.status_code == 403:
        print_result(True, "Unauthorized access rejected")
        print(f"    Error: {response.json()['detail']}")
        return True
    else:
        print_result(False, f"Unauthorized access not rejected (status: {response.status_code})")
        return False


def test_protected_route_invalid_token():
    """Test accessing protected route with invalid token (should fail)"""
    print_test_header("Access Protected Route With Invalid Token (should fail)")

    headers = {"Authorization": "Bearer invalid_token_12345"}
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )

    if response.status_code == 401:
        print_result(True, "Invalid token rejected")
        print(f"    Error: {response.json()['detail']}")
        return True
    else:
        print_result(False, f"Invalid token not rejected (status: {response.status_code})")
        return False


def test_logout(token: str):
    """Test logout"""
    print_test_header("Logout")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/auth/logout",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Logout successful")
        print(f"    Message: {data['message']}")
        return True
    else:
        print_result(False, f"Logout failed: {response.text}")
        return False


def test_password_reset_flow():
    """Test password reset flow"""
    print_test_header("Password Reset Flow")

    # Step 1: Request password reset
    print("\n  Step 1: Request password reset...")
    response = requests.post(
        f"{BASE_URL}/api/auth/reset-password-request",
        json={"email": TEST_USER["email"]}
    )

    if response.status_code != 200:
        print_result(False, "Password reset request failed")
        return False

    data = response.json()
    print_result(True, "Password reset token generated")
    reset_token = data.get("reset_token")
    if not reset_token:
        print_result(False, "No reset token in response")
        return False

    print(f"    Reset token: {reset_token[:20]}...")

    # Step 2: Reset password with token
    print("\n  Step 2: Reset password with token...")
    new_password = "NewSecurePassword456"
    response = requests.post(
        f"{BASE_URL}/api/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": new_password
        }
    )

    if response.status_code != 200:
        print_result(False, f"Password reset failed: {response.text}")
        return False

    print_result(True, "Password reset successful")

    # Step 3: Login with new password
    print("\n  Step 3: Login with new password...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": new_password
        }
    )

    if response.status_code == 200:
        print_result(True, "Login with new password successful")
        # Update TEST_USER password for future tests
        TEST_USER["password"] = new_password
        return True
    else:
        print_result(False, "Login with new password failed")
        return False


def main():
    """Run all tests"""
    print()
    print("=" * 80)
    print("WEEK 5: AUTHENTICATION SYSTEM TESTS")
    print("=" * 80)
    print()
    print(f"API Base URL: {BASE_URL}")
    print(f"Start Time: {datetime.now().isoformat()}")
    print()
    print("Make sure the backend server is running!")
    print()

    results = []

    # Run tests in order
    results.append(("Password Strength Validation", test_password_strength_validation()))

    token = test_register_user()
    results.append(("User Registration", token is not None))

    village_admin_token = test_register_village_admin()
    results.append(("Village Admin Registration", village_admin_token is not None))

    results.append(("Duplicate Registration Rejection", test_duplicate_registration()))

    results.append(("Login Invalid Credentials", test_login_invalid()))

    login_token = test_login_valid()
    results.append(("Login Valid Credentials", login_token is not None))

    if login_token:
        results.append(("Get Current User", test_get_current_user(login_token)))
        results.append(("Logout", test_logout(login_token)))

    results.append(("Protected Route Without Token", test_protected_route_without_token()))
    results.append(("Protected Route Invalid Token", test_protected_route_invalid_token()))

    results.append(("Password Reset Flow", test_password_reset_flow()))

    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        symbol = "✓" if result else "✗"
        status = "PASS" if result else "FAIL"
        print(f"  {symbol} {status}: {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
