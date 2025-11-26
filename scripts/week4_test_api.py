#!/usr/bin/env python3
"""
Week 4: Test the Identity Theme API

Tests the GET endpoint to retrieve generated identity themes for Chirac
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_identity_themes():
    """Test GET /api/villages/{village_slug}/identity endpoint"""

    print("=" * 80)
    print("TESTING IDENTITY THEME API")
    print("=" * 80)
    print()

    print("1. Testing GET /api/villages/chirac/identity")
    print("   Fetching all identity themes for Chirac...")
    print()

    try:
        response = requests.get(f"{BASE_URL}/api/villages/chirac/identity")

        if response.status_code == 200:
            themes = response.json()
            print(f"   ✓ Success! Found {len(themes)} themes")
            print()

            for i, theme in enumerate(themes, 1):
                print(f"   Theme {i}: {theme['theme_name']}")
                print(f"      Category: {theme['category']['name']}")
                print(f"      Tagline: {theme['tagline']}")
                print(f"      Story length: {len(theme['story_markdown'])} chars")
                print(f"      Project ideas: {len(theme['project_ideas'])}")
                print(f"      Confidence: {theme['confidence_score']}")
                print(f"      AI Model: {theme['ai_model']}")
                print()

            return True
        else:
            print(f"   ✗ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_get_identity_summary():
    """Test GET /api/villages/{village_slug}/identity-summary endpoint"""

    print()
    print("2. Testing GET /api/villages/chirac/identity-summary")
    print("   Fetching identity summary...")
    print()

    try:
        response = requests.get(f"{BASE_URL}/api/villages/chirac/identity-summary")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success!")
            print(f"   Village: {data['village']['name']}")
            print(f"   Total themes: {data['total_themes']}")
            print(f"   Featured themes: {len(data['featured_themes'])}")
            print()
            return True
        else:
            print(f"   ✗ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_get_theme_detail():
    """Test GET /api/villages/{village_slug}/identity/{theme_id} endpoint"""

    print()
    print("3. Testing GET /api/villages/chirac/identity/1")
    print("   Fetching detailed theme...")
    print()

    try:
        response = requests.get(f"{BASE_URL}/api/villages/chirac/identity/1")

        if response.status_code == 200:
            theme = response.json()
            print(f"   ✓ Success!")
            print(f"   Theme: {theme['theme_name']}")
            print()
            print("   Story excerpt:")
            print(f"   {theme['story_markdown'][:200]}...")
            print()
            print("   Project ideas:")
            for project in theme['project_ideas']:
                print(f"   - {project['title']} ({project['difficulty']}, impact: {project['estimated_impact']})")
            print()
            return True
        else:
            print(f"   ✗ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

if __name__ == "__main__":
    print()
    print("Starting API tests...")
    print("(Make sure the backend server is running on localhost:8000)")
    print()

    test1 = test_get_identity_themes()
    test2 = test_get_identity_summary()
    test3 = test_get_theme_detail()

    print()
    print("=" * 80)
    if test1 and test2 and test3:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 80)
    print()
