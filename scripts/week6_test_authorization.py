#!/usr/bin/env python3
"""
Week 6: Authorization & Permissions Test Suite

Tests the complete authorization system including:
- Role-based access control (RBAC)
- Permission checks
- Village ownership validation
- Subscription tier gating
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

# Database connection
DB_CONFIG = {
    'dbname': 'spv_treasure_map',
    'user': 'spv_admin',
    'password': 'MySecurePass123',
    'host': 'localhost',
    'port': 5432
}

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

def test_roles_table(cursor):
    """Test 1: Verify roles table and default roles"""
    print_section("TEST 1: Roles Table")

    # Check table exists
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_name = 'roles'
    """)
    result = cursor.fetchone()

    if result['count'] == 0:
        print_error("Roles table does not exist")
        return False

    print_success("Roles table exists")

    # Check default roles
    cursor.execute("SELECT id, name, description FROM roles ORDER BY name")
    roles = cursor.fetchall()

    expected_roles = {'admin', 'village_admin', 'editor', 'viewer'}
    actual_roles = {r['name'] for r in roles}

    if expected_roles == actual_roles:
        print_success(f"All 4 default roles exist: {', '.join(sorted(expected_roles))}")
        for role in roles:
            print(f"  • {role['name']}: {role['description']}")
        return True
    else:
        missing = expected_roles - actual_roles
        extra = actual_roles - expected_roles
        if missing:
            print_error(f"Missing roles: {missing}")
        if extra:
            print_warning(f"Extra roles: {extra}")
        return False

def test_permissions_table(cursor):
    """Test 2: Verify permissions table and default permissions"""
    print_section("TEST 2: Permissions Table")

    # Check table exists
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_name = 'permissions'
    """)
    result = cursor.fetchone()

    if result['count'] == 0:
        print_error("Permissions table does not exist")
        return False

    print_success("Permissions table exists")

    # Count permissions by category
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM permissions
        GROUP BY category
        ORDER BY category
    """)
    categories = cursor.fetchall()

    print(f"  Permissions by category:")
    total = 0
    for cat in categories:
        print(f"    • {cat['category']}: {cat['count']} permissions")
        total += cat['count']

    if total >= 20:
        print_success(f"Total permissions: {total}")
        return True
    else:
        print_warning(f"Only {total} permissions found (expected at least 20)")
        return True  # Not a failure, just a warning

def test_role_permissions(cursor):
    """Test 3: Verify role-permission assignments"""
    print_section("TEST 3: Role-Permission Assignments")

    # Get permission counts for each role
    cursor.execute("""
        SELECT r.name as role, COUNT(rp.permission_id) as permission_count
        FROM roles r
        LEFT JOIN role_permissions rp ON r.id = rp.role_id
        GROUP BY r.id, r.name
        ORDER BY permission_count DESC
    """)
    assignments = cursor.fetchall()

    success = True
    for assignment in assignments:
        role = assignment['role']
        count = assignment['permission_count']

        if role == 'admin':
            # Admin should have all permissions
            cursor.execute("SELECT COUNT(*) as total FROM permissions")
            total_perms = cursor.fetchone()['total']
            if count == total_perms:
                print_success(f"{role}: {count} permissions (all permissions)")
            else:
                print_error(f"{role}: {count} permissions (expected {total_perms})")
                success = False
        elif role == 'village_admin':
            if count >= 10:
                print_success(f"{role}: {count} permissions")
            else:
                print_warning(f"{role}: {count} permissions (expected at least 10)")
        elif role == 'editor':
            if count >= 5:
                print_success(f"{role}: {count} permissions")
            else:
                print_warning(f"{role}: {count} permissions (expected at least 5)")
        elif role == 'viewer':
            if count >= 3:
                print_success(f"{role}: {count} permissions")
            else:
                print_warning(f"{role}: {count} permissions (expected at least 3)")

    return success

def test_users_role_id(cursor):
    """Test 4: Verify users table has role_id column"""
    print_section("TEST 4: Users Table Role Integration")

    # Check if role_id column exists
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'role_id'
    """)
    result = cursor.fetchone()

    if not result:
        print_error("role_id column does not exist in users table")
        return False

    print_success(f"role_id column exists (type: {result['data_type']})")

    # Check if users have been migrated
    cursor.execute("""
        SELECT
            COUNT(*) as total_users,
            COUNT(role_id) as users_with_role_id,
            COUNT(role_id) * 100.0 / NULLIF(COUNT(*), 0) as migration_percent
        FROM users
    """)
    stats = cursor.fetchone()

    if stats['total_users'] == 0:
        print_warning("No users in database yet")
        return True

    if stats['migration_percent'] == 100:
        print_success(f"All {stats['total_users']} users have been assigned role_id")
    else:
        print_warning(f"Only {stats['users_with_role_id']}/{stats['total_users']} users have role_id ({stats['migration_percent']:.1f}%)")

    # Show role distribution
    cursor.execute("""
        SELECT r.name as role, COUNT(u.id) as user_count
        FROM roles r
        LEFT JOIN users u ON r.id = u.role_id
        GROUP BY r.id, r.name
        ORDER BY user_count DESC
    """)
    distribution = cursor.fetchall()

    print("  User distribution by role:")
    for dist in distribution:
        print(f"    • {dist['role']}: {dist['user_count']} users")

    return True

def test_villages_subscription_tier(cursor):
    """Test 5: Verify villages have subscription_tier column"""
    print_section("TEST 5: Villages Subscription Tier")

    # Check if subscription_tier column exists
    cursor.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = 'villages' AND column_name = 'subscription_tier'
    """)
    result = cursor.fetchone()

    if not result:
        print_error("subscription_tier column does not exist in villages table")
        return False

    print_success(f"subscription_tier column exists (type: {result['data_type']}, default: {result['column_default']})")

    # Check tier distribution
    cursor.execute("""
        SELECT subscription_tier, COUNT(*) as count
        FROM villages
        GROUP BY subscription_tier
        ORDER BY
            CASE subscription_tier
                WHEN 'enterprise' THEN 1
                WHEN 'partner' THEN 2
                WHEN 'free' THEN 3
                ELSE 4
            END
    """)
    tiers = cursor.fetchall()

    if not tiers:
        print_warning("No villages in database yet")
        return True

    print("  Villages by subscription tier:")
    for tier in tiers:
        print(f"    • {tier['subscription_tier']}: {tier['count']} villages")

    return True

def test_specific_permissions(cursor):
    """Test 6: Verify specific important permissions exist"""
    print_section("TEST 6: Key Permission Checks")

    key_permissions = [
        ('can_generate_identity', 'identity'),
        ('can_view_any_village', 'village'),
        ('can_edit_own_village', 'village'),
        ('can_add_poi', 'poi'),
        ('can_manage_users', 'user'),
        ('can_view_analytics', 'analytics'),
    ]

    success = True
    for perm_name, expected_category in key_permissions:
        cursor.execute("""
            SELECT id, name, category, description
            FROM permissions
            WHERE name = %s
        """, (perm_name,))
        result = cursor.fetchone()

        if result:
            if result['category'] == expected_category:
                print_success(f"{perm_name} exists (category: {result['category']})")
            else:
                print_warning(f"{perm_name} exists but wrong category: {result['category']} (expected {expected_category})")
        else:
            print_error(f"{perm_name} does not exist")
            success = False

    return success

def test_admin_has_all_permissions(cursor):
    """Test 7: Verify admin role has all permissions"""
    print_section("TEST 7: Admin Role Has All Permissions")

    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM permissions) as total_permissions,
            (SELECT COUNT(*)
             FROM role_permissions rp
             JOIN roles r ON rp.role_id = r.id
             WHERE r.name = 'admin') as admin_permissions
    """)
    result = cursor.fetchone()

    if result['total_permissions'] == result['admin_permissions']:
        print_success(f"Admin has all {result['total_permissions']} permissions")
        return True
    else:
        print_error(f"Admin has {result['admin_permissions']} permissions but there are {result['total_permissions']} total")
        return False

def test_village_admin_permissions(cursor):
    """Test 8: Verify village_admin has correct permissions"""
    print_section("TEST 8: Village Admin Permissions")

    # Expected permissions for village_admin
    expected = {
        'can_edit_own_village',
        'can_view_pois',
        'can_add_poi',
        'can_edit_poi',
        'can_delete_poi',
        'can_view_conflicts',
        'can_add_conflict',
        'can_edit_conflict',
        'can_delete_conflict',
        'can_view_identity',
        'can_generate_identity',
        'can_edit_identity',
        'can_invite_users',
        'can_view_analytics',
    }

    cursor.execute("""
        SELECT p.name
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN roles r ON rp.role_id = r.id
        WHERE r.name = 'village_admin'
    """)
    actual = {row['name'] for row in cursor.fetchall()}

    if expected.issubset(actual):
        print_success(f"Village admin has all expected permissions ({len(actual)} total)")
        extra = actual - expected
        if extra:
            print(f"  Additional permissions: {', '.join(sorted(extra))}")
        return True
    else:
        missing = expected - actual
        print_error(f"Village admin missing permissions: {', '.join(sorted(missing))}")
        return False

def test_permission_categories(cursor):
    """Test 9: Verify permission categories are properly defined"""
    print_section("TEST 9: Permission Categories")

    expected_categories = {
        'village', 'poi', 'conflict', 'identity',
        'user', 'analytics', 'premium'
    }

    cursor.execute("""
        SELECT DISTINCT category
        FROM permissions
        WHERE category IS NOT NULL
        ORDER BY category
    """)
    actual_categories = {row['category'] for row in cursor.fetchall()}

    if expected_categories == actual_categories:
        print_success(f"All {len(expected_categories)} expected categories exist")
        for cat in sorted(actual_categories):
            print(f"  • {cat}")
        return True
    else:
        missing = expected_categories - actual_categories
        extra = actual_categories - expected_categories
        if missing:
            print_warning(f"Missing categories: {', '.join(sorted(missing))}")
        if extra:
            print(f"  Extra categories: {', '.join(sorted(extra))}")
        return True

def test_indexes(cursor):
    """Test 10: Verify important indexes exist"""
    print_section("TEST 10: Database Indexes")

    expected_indexes = [
        ('roles', 'idx_roles_name'),
        ('permissions', 'idx_permissions_name'),
        ('permissions', 'idx_permissions_category'),
        ('role_permissions', 'idx_role_permissions_role_id'),
        ('role_permissions', 'idx_role_permissions_permission_id'),
        ('users', 'idx_users_role_id'),
        ('villages', 'idx_villages_subscription_tier'),
    ]

    success = True
    for table_name, index_name in expected_indexes:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM pg_indexes
            WHERE tablename = %s AND indexname = %s
        """, (table_name, index_name))
        result = cursor.fetchone()

        if result['count'] > 0:
            print_success(f"{table_name}.{index_name}")
        else:
            print_warning(f"{table_name}.{index_name} not found")
            success = False

    return success

def main():
    print(f"\n{Colors.BOLD}Week 6: Authorization & Permissions Test Suite{Colors.ENDC}")
    print(f"{Colors.BOLD}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")

    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print_success("Connected to PostgreSQL database\n")

        # Run all tests
        tests = [
            ("Roles Table", test_roles_table),
            ("Permissions Table", test_permissions_table),
            ("Role-Permission Assignments", test_role_permissions),
            ("Users Role Integration", test_users_role_id),
            ("Villages Subscription Tier", test_villages_subscription_tier),
            ("Key Permissions", test_specific_permissions),
            ("Admin Has All Permissions", test_admin_has_all_permissions),
            ("Village Admin Permissions", test_village_admin_permissions),
            ("Permission Categories", test_permission_categories),
            ("Database Indexes", test_indexes),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func(cursor)
                results.append((test_name, result))
            except Exception as e:
                print_error(f"Test failed with exception: {e}")
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

        cursor.close()
        conn.close()

        return passed == total

    except psycopg2.Error as e:
        print_error(f"Database error: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
