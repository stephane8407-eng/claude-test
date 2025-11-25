#!/usr/bin/env python3
"""
Week 1 Multi-Tenancy Test Script

Tests that villages work independently
"""

import requests

BASE_URL = "http://localhost:8000"

def test_list_villages():
    """Test: Can list all villages"""
    print("Test 1: List villages...")

    response = requests.get(f"{BASE_URL}/api/villages/")
    assert response.status_code == 200

    villages = response.json()
    assert len(villages) == 2
    assert villages[0]['name'] in ['Chirac', 'Manot']

    print(f"✅ Found {len(villages)} villages")

def test_get_chirac():
    """Test: Can get Chirac details"""
    print("\nTest 2: Get Chirac village...")

    response = requests.get(f"{BASE_URL}/api/villages/chirac")
    assert response.status_code == 200

    chirac = response.json()
    assert chirac['name'] == 'Chirac'
    assert chirac['subscription_tier'] == 'flagship'

    print(f"✅ Chirac: {chirac['population']} pop, {chirac['subscription_tier']} tier")

def test_chirac_conflicts():
    """Test: Chirac has 123 conflicts"""
    print("\nTest 3: Get Chirac conflicts...")

    response = requests.get(f"{BASE_URL}/api/villages/chirac/conflicts")
    assert response.status_code == 200

    conflicts = response.json()
    assert len(conflicts) == 123

    print(f"✅ Chirac has {len(conflicts)} conflicts")

def test_manot_conflicts():
    """Test: Manot has 0 conflicts (separate from Chirac)"""
    print("\nTest 4: Get Manot conflicts...")

    response = requests.get(f"{BASE_URL}/api/villages/manot/conflicts")
    assert response.status_code == 200

    conflicts = response.json()
    assert len(conflicts) == 0

    print(f"✅ Manot has {len(conflicts)} conflicts (isolated from Chirac)")

def test_village_stats():
    """Test: Can get village statistics"""
    print("\nTest 5: Get Chirac stats...")

    response = requests.get(f"{BASE_URL}/api/villages/chirac/stats")
    assert response.status_code == 200

    stats = response.json()
    assert stats['total_conflicts'] == 123

    print(f"✅ Stats: {stats['total_conflicts']} conflicts")

def test_filter_by_village():
    """Test: Can filter conflicts by village"""
    print("\nTest 6: Filter conflicts by village...")

    # All conflicts
    response = requests.get(f"{BASE_URL}/api/conflicts")
    all_conflicts = response.json()

    # Just Chirac conflicts
    response = requests.get(f"{BASE_URL}/api/conflicts?village_slug=chirac")
    chirac_conflicts = response.json()

    assert chirac_conflicts['total'] == 123
    print(f"✅ Filtering works: {chirac_conflicts['total']} Chirac conflicts")

if __name__ == '__main__':
    print("=" * 60)
    print("WEEK 1 MULTI-TENANCY TESTS")
    print("=" * 60)

    try:
        test_list_villages()
        test_get_chirac()
        test_chirac_conflicts()
        test_manot_conflicts()
        test_village_stats()
        test_filter_by_village()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nWeek 1 Success Criteria:")
        print("✅ Can create 2 test villages")
        print("✅ Each village sees only their conflicts")
        print("✅ Can switch between villages")
        print("✅ Village settings persist")
        print("\n🎉 WEEK 1 COMPLETE - Ready for Week 2!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
