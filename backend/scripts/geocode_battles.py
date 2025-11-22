#!/usr/bin/env python3
"""
Geocode battles using Nominatim API (OpenStreetMap).

This script reads a CSV file with battle data and adds:
- latitude
- longitude
- country code (FR, UK, BE, etc.)
- war_period (inferred from year)

Uses Nominatim API (free, no API key required).
Rate limit: 1 request per second.

Usage:
    python geocode_battles.py <input_csv> <output_csv>

Example:
    python geocode_battles.py ../../comprehensive_battles.csv ../../all_battles_geocoded.csv
"""

import csv
import time
import sys
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple

# Nominatim API configuration
# Note: Nominatim can be restrictive. Alternative: Use Photon API (photon.komoot.io)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "SPV-Treasure-Map/1.0 (https://github.com/stephane8407-eng/claude-test; contact via GitHub)"
RATE_LIMIT_SECONDS = 1.5  # 1.5 seconds per request (be respectful)

# War period inference based on year
def infer_war_period(year: int) -> str:
    """Infer war period from battle year."""
    if year >= 1914 and year <= 1918:
        return "WW1"
    elif year >= 1939 and year <= 1945:
        return "WW2"
    elif year >= 1792 and year <= 1815:
        return "Napoleonic Wars"
    elif year >= 1337 and year <= 1453:
        return "Hundred Years War"
    elif year >= 500 and year <= 1500:
        return "Medieval"
    elif year >= 1618 and year <= 1648:
        return "Thirty Years War"
    elif year >= 1701 and year <= 1714:
        return "War of Spanish Succession"
    elif year >= 1756 and year <= 1763:
        return "Seven Years War"
    elif year >= 1861 and year <= 1865:
        return "American Civil War"
    elif year >= 1950 and year <= 1953:
        return "Korean War"
    elif year >= 1955 and year <= 1975:
        return "Vietnam War"
    elif year >= 1991 and year <= 1991:
        return "Gulf War"
    else:
        return "Other"


def geocode_location(location: str) -> Optional[Dict]:
    """
    Geocode a location string using Nominatim API.

    Args:
        location: Location string (e.g., "Hastings, England")

    Returns:
        Dictionary with 'lat', 'lon', 'country_code' or None if failed
    """
    try:
        params = {
            'q': location,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }

        headers = {
            'User-Agent': USER_AGENT,
            'Referer': 'https://github.com/stephane8407-eng/claude-test',
            'Accept-Language': 'en'
        }

        response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)

        # Check for rate limiting
        if response.status_code == 429:
            print(f"  ⚠️  Rate limited. Waiting 5 seconds...")
            time.sleep(5)
            response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)

        response.raise_for_status()

        results = response.json()

        if results and len(results) > 0:
            result = results[0]
            return {
                'lat': float(result['lat']),
                'lon': float(result['lon']),
                'country_code': result.get('address', {}).get('country_code', '').upper()
            }
        else:
            return None

    except Exception as e:
        print(f"  ⚠️  Geocoding error for '{location}': {e}")
        return None


def geocode_battles(input_csv: str, output_csv: str):
    """
    Geocode all battles from input CSV and write to output CSV.

    Args:
        input_csv: Path to input CSV file
        output_csv: Path to output CSV file
    """
    print(f"🗺️  SPV Treasure Map - Battle Geocoding")
    print(f"=" * 60)
    print(f"Input:  {input_csv}")
    print(f"Output: {output_csv}")
    print(f"Rate:   {RATE_LIMIT_SECONDS} seconds per request")
    print(f"=" * 60)
    print()

    # Read input CSV
    print("📖 Reading input CSV...")
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        battles = list(reader)

    total_battles = len(battles)
    print(f"✅ Found {total_battles} battles to geocode")
    print()

    # Estimate time
    estimated_minutes = (total_battles * RATE_LIMIT_SECONDS) / 60
    print(f"⏱️  Estimated time: {estimated_minutes:.1f} minutes ({estimated_minutes/60:.1f} hours)")
    print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Geocode each battle
    geocoded_battles = []
    success_count = 0
    failed_count = 0
    start_time = time.time()

    for i, battle in enumerate(battles, 1):
        location = battle.get('location', '').strip()
        year = int(battle.get('year', 0)) if battle.get('year', '').isdigit() else 0

        print(f"[{i}/{total_battles}] {battle.get('name', 'Unknown')[:50]}")
        print(f"  Location: {location}")

        # Geocode
        geo_data = geocode_location(location)

        if geo_data:
            battle['latitude'] = geo_data['lat']
            battle['longitude'] = geo_data['lon']
            battle['country'] = geo_data['country_code']
            battle['war_period'] = infer_war_period(year)
            battle['significance'] = 'moderate'  # Default, can be updated later
            battle['casualties_estimated'] = ''  # Can be added later
            battle['sides_involved'] = battle.get('participants', '')

            success_count += 1
            print(f"  ✅ {geo_data['lat']:.4f}, {geo_data['lon']:.4f} ({geo_data['country_code']})")
        else:
            battle['latitude'] = ''
            battle['longitude'] = ''
            battle['country'] = ''
            battle['war_period'] = infer_war_period(year) if year > 0 else ''
            battle['significance'] = ''
            battle['casualties_estimated'] = ''
            battle['sides_involved'] = battle.get('participants', '')

            failed_count += 1
            print(f"  ❌ Geocoding failed")

        geocoded_battles.append(battle)

        # Progress report every 100 battles
        if i % 100 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            remaining = (total_battles - i) / rate if rate > 0 else 0
            print()
            print(f"📊 Progress: {i}/{total_battles} ({i/total_battles*100:.1f}%)")
            print(f"   Success: {success_count} | Failed: {failed_count} | Success rate: {success_count/i*100:.1f}%")
            print(f"   Elapsed: {elapsed/60:.1f} min | Remaining: {remaining/60:.1f} min")
            print()

        # Rate limiting
        time.sleep(RATE_LIMIT_SECONDS)

    # Final statistics
    elapsed_total = time.time() - start_time
    print()
    print(f"=" * 60)
    print(f"✅ GEOCODING COMPLETE")
    print(f"=" * 60)
    print(f"Total battles:    {total_battles}")
    print(f"Successfully geocoded: {success_count} ({success_count/total_battles*100:.1f}%)")
    print(f"Failed:          {failed_count} ({failed_count/total_battles*100:.1f}%)")
    print(f"Total time:      {elapsed_total/60:.1f} minutes ({elapsed_total/3600:.2f} hours)")
    print(f"End time:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Write output CSV
    print(f"💾 Writing output CSV: {output_csv}")

    # Define output fieldnames
    output_fieldnames = [
        'name', 'year', 'date', 'location', 'participants', 'outcome',
        'latitude', 'longitude', 'country', 'war_period', 'significance',
        'casualties_estimated', 'sides_involved'
    ]

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(geocoded_battles)

    print(f"✅ Output saved: {output_csv}")
    print()

    # Summary by country
    country_counts = {}
    for battle in geocoded_battles:
        if battle.get('country'):
            country_counts[battle['country']] = country_counts.get(battle['country'], 0) + 1

    if country_counts:
        print("📍 Battles by country:")
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {country}: {count}")

    # Summary by war period
    period_counts = {}
    for battle in geocoded_battles:
        if battle.get('war_period'):
            period_counts[battle['war_period']] = period_counts.get(battle['war_period'], 0) + 1

    if period_counts:
        print()
        print("⚔️  Battles by war period:")
        for period, count in sorted(period_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {period}: {count}")

    print()
    print("🎉 Done!")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python geocode_battles.py <input_csv> <output_csv>")
        print()
        print("Example:")
        print("  python geocode_battles.py ../../comprehensive_battles.csv ../../all_battles_geocoded.csv")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_csv = sys.argv[2]

    geocode_battles(input_csv, output_csv)
