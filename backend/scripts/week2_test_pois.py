#!/usr/bin/env python3
"""
Week 2 POI System Test Script

Tests that flexible POI system works with village isolation
"""

import requests

BASE_URL = "http://localhost:8000"

def test_list_poi_types():
    """Test: Can list all POI types"""
    print("Test 1: List POI types...")

    response = requests.get(f"{BASE_URL}/api/pois/types")
    assert response.status_code == 200

    poi_types = response.json()
    assert len(poi_types) == 8  # pond, church, château, mill, fountain, cross, wash_house, war_memorial

    type_names = [pt['name'] for pt in poi_types]
    assert 'pond' in type_names
    assert 'church' in type_names
    assert 'château' in type_names

    print(f"✅ Found {len(poi_types)} POI types")

def test_chirac_pois():
    """Test: Chirac has 19 POIs"""
    print("\nTest 2: Get Chirac POIs...")

    response = requests.get(f"{BASE_URL}/api/pois/village/chirac")
    assert response.status_code == 200

    data = response.json()
    assert data['total_pois'] == 19

    # Check breakdown
    pois_by_type = data['pois_by_type']
    assert 'pond' in pois_by_type
    assert 'church' in pois_by_type
    assert 'château' in pois_by_type

    pond_count = len(pois_by_type['pond']['pois'])
    church_count = len(pois_by_type['church']['pois'])
    chateau_count = len(pois_by_type['château']['pois'])

    assert pond_count == 15
    assert church_count == 3
    assert chateau_count == 1

    print(f"✅ Chirac has {data['total_pois']} POIs ({pond_count} ponds, {church_count} churches, {chateau_count} château)")

def test_manot_pois():
    """Test: Manot has 0 POIs (village isolation)"""
    print("\nTest 3: Get Manot POIs...")

    response = requests.get(f"{BASE_URL}/api/pois/village/manot")
    assert response.status_code == 200

    data = response.json()
    assert data['total_pois'] == 0

    print(f"✅ Manot has {data['total_pois']} POIs (perfect isolation from Chirac)")

def test_chirac_poi_stats():
    """Test: Can get POI statistics for Chirac"""
    print("\nTest 4: Get Chirac POI stats...")

    response = requests.get(f"{BASE_URL}/api/pois/village/chirac/stats")
    assert response.status_code == 200

    stats = response.json()
    assert stats['total_pois'] == 19
    assert stats['by_type']['pond'] == 15
    assert stats['by_type']['church'] == 3
    assert stats['by_type']['château'] == 1

    print(f"✅ Stats: {stats['total_pois']} total, {stats['public_pois']} public")

def test_filter_by_village():
    """Test: Can filter POIs by village slug"""
    print("\nTest 5: Filter POIs by village...")

    # All POIs
    response = requests.get(f"{BASE_URL}/api/pois/")
    all_data = response.json()

    # Just Chirac POIs
    response = requests.get(f"{BASE_URL}/api/pois/?village_slug=chirac")
    chirac_data = response.json()

    assert chirac_data['total'] == 19

    print(f"✅ Filtering works: {chirac_data['total']} POIs for Chirac")

def test_get_specific_poi():
    """Test: Can get specific POI details"""
    print("\nTest 6: Get specific POI...")

    # Get Chirac POIs first to get an ID
    response = requests.get(f"{BASE_URL}/api/pois/village/chirac")
    data = response.json()

    # Get first pond POI ID
    first_pond = data['pois_by_type']['pond']['pois'][0]
    poi_id = first_pond['id']

    # Get specific POI
    response = requests.get(f"{BASE_URL}/api/pois/{poi_id}")
    assert response.status_code == 200

    poi = response.json()
    assert poi['id'] == poi_id
    assert 'poi_type' in poi
    assert poi['poi_type']['name'] == 'pond'

    print(f"✅ Retrieved POI: {poi['name']} (ID: {poi_id})")

if __name__ == '__main__':
    print("=" * 60)
    print("WEEK 2 POI SYSTEM TESTS")
    print("=" * 60)

    try:
        test_list_poi_types()
        test_chirac_pois()
        test_manot_pois()
        test_chirac_poi_stats()
        test_filter_by_village()
        test_get_specific_poi()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nWeek 2 Success Criteria:")
        print("✅ POI types table created (8 types)")
        print("✅ POIs table created with village_id")
        print("✅ Chirac has 19 POIs (15 ponds, 3 churches, 1 château)")
        print("✅ Manot has 0 POIs (perfect village isolation)")
        print("✅ API endpoints working (list, get, by-village, stats)")
        print("\n🎉 WEEK 2 COMPLETE - Flexible POI system ready!")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
