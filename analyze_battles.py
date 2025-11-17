#!/usr/bin/env python3
"""
Battle Data Analyzer
Analyzes battle CSV data to show statistics and quality metrics.

Usage:
    python analyze_battles.py battles.csv
"""

import sys
import csv
from collections import Counter, defaultdict
import re


def analyze_battle_csv(filename):
    """Analyze a battle CSV file and print statistics."""

    print(f"\n{'='*60}")
    print(f"BATTLE DATA ANALYSIS: {filename}")
    print(f"{'='*60}\n")

    battles = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        battles = list(reader)

    total = len(battles)
    print(f"📊 Total Battles: {total}\n")

    # Analyze fields
    print(f"{'='*60}")
    print("FIELD COMPLETENESS")
    print(f"{'='*60}")

    fields = ['name', 'year', 'date', 'location', 'participants', 'outcome']
    for field in fields:
        filled = sum(1 for b in battles if b.get(field, '').strip())
        pct = (filled / total * 100) if total > 0 else 0
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        print(f"{field:15s} {bar} {filled:4d}/{total:4d} ({pct:5.1f}%)")

    # Year distribution
    print(f"\n{'='*60}")
    print("BATTLES BY CENTURY")
    print(f"{'='*60}")

    years = []
    for b in battles:
        year_str = b.get('year', '').strip()
        if year_str and year_str.isdigit():
            years.append(int(year_str))

    if years:
        century_counts = Counter()
        for year in years:
            century = (year // 100) * 100
            century_counts[century] += 1

        for century in sorted(century_counts.keys()):
            count = century_counts[century]
            bar = '█' * (count * 50 // max(century_counts.values()))
            print(f"{century:4d}s: {bar} ({count} battles)")

    # Location analysis
    print(f"\n{'='*60}")
    print("TOP LOCATIONS")
    print(f"{'='*60}")

    # Extract country/region from location
    locations = []
    for b in battles:
        loc = b.get('location', '').strip()
        if loc:
            # Extract last part after comma (usually country)
            parts = [p.strip() for p in loc.split(',')]
            if parts:
                locations.append(parts[-1])

    if locations:
        loc_counts = Counter(locations).most_common(10)
        max_count = loc_counts[0][1] if loc_counts else 1

        for loc, count in loc_counts:
            bar = '█' * (count * 40 // max_count)
            print(f"{loc[:30]:30s} {bar} ({count})")

    # Participants analysis
    print(f"\n{'='*60}")
    print("TOP PARTICIPANTS")
    print(f"{'='*60}")

    participants_all = []
    for b in battles:
        parts = b.get('participants', '').strip()
        if parts:
            # Split on 'vs' and extract combatants
            sides = re.split(r'\s+vs\.?\s+|\s+v\.?\s+', parts, flags=re.IGNORECASE)
            for side in sides:
                side_clean = side.strip()
                if side_clean:
                    participants_all.append(side_clean)

    if participants_all:
        part_counts = Counter(participants_all).most_common(10)
        max_count = part_counts[0][1] if part_counts else 1

        for part, count in part_counts:
            bar = '█' * (count * 40 // max_count)
            print(f"{part[:30]:30s} {bar} ({count})")

    # Year range
    if years:
        print(f"\n{'='*60}")
        print("TEMPORAL COVERAGE")
        print(f"{'='*60}")
        print(f"Earliest battle: {min(years)}")
        print(f"Latest battle:   {max(years)}")
        print(f"Time span:       {max(years) - min(years)} years")

    # Treasure hunting relevance
    print(f"\n{'='*60}")
    print("TREASURE HUNTING RELEVANCE")
    print(f"{'='*60}")

    france_uk_belgium = sum(1 for b in battles
                           if any(x in b.get('location', '').lower()
                                 for x in ['france', 'england', 'scotland', 'wales', 'belgium', 'flanders']))

    medieval = sum(1 for b in battles
                  if b.get('year', '').strip().isdigit() and 1000 <= int(b.get('year', '0')) <= 1500)

    early_modern = sum(1 for b in battles
                      if b.get('year', '').strip().isdigit() and 1500 < int(b.get('year', '0')) <= 1700)

    sieges = sum(1 for b in battles
                if 'siege' in b.get('name', '').lower())

    print(f"France/UK/Belgium:   {france_uk_belgium:4d} ({france_uk_belgium/total*100:5.1f}%)")
    print(f"Medieval (1000-1500):{medieval:4d} ({medieval/total*100:5.1f}%)")
    print(f"Early Modern (1500-1700): {early_modern:4d} ({early_modern/total*100:5.1f}%)")
    print(f"Sieges:              {sieges:4d} ({sieges/total*100:5.1f}%)")

    # Data quality score
    print(f"\n{'='*60}")
    print("DATA QUALITY SCORE")
    print(f"{'='*60}")

    quality_score = 0
    quality_max = 0

    # Name completeness (20 points)
    quality_max += 20
    name_filled = sum(1 for b in battles if b.get('name', '').strip())
    quality_score += int((name_filled / total) * 20) if total > 0 else 0

    # Year completeness (20 points)
    quality_max += 20
    year_filled = sum(1 for b in battles if b.get('year', '').strip())
    quality_score += int((year_filled / total) * 20) if total > 0 else 0

    # Location completeness (20 points)
    quality_max += 20
    loc_filled = sum(1 for b in battles if b.get('location', '').strip())
    quality_score += int((loc_filled / total) * 20) if total > 0 else 0

    # Participants completeness (20 points)
    quality_max += 20
    part_filled = sum(1 for b in battles if b.get('participants', '').strip())
    quality_score += int((part_filled / total) * 20) if total > 0 else 0

    # Outcome completeness (20 points)
    quality_max += 20
    out_filled = sum(1 for b in battles if b.get('outcome', '').strip())
    quality_score += int((out_filled / total) * 20) if total > 0 else 0

    quality_pct = (quality_score / quality_max * 100) if quality_max > 0 else 0

    bar = '█' * int(quality_pct / 5) + '░' * (20 - int(quality_pct / 5))
    print(f"\nQuality Score: {bar} {quality_score}/{quality_max} ({quality_pct:.1f}%)")

    if quality_pct >= 80:
        print("✓ Excellent data quality!")
    elif quality_pct >= 60:
        print("✓ Good data quality")
    elif quality_pct >= 40:
        print("⚠ Fair data quality - consider enrichment")
    else:
        print("⚠ Poor data quality - needs significant enrichment")

    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}")
    print("1. Add GPS coordinates via geocoding")
    print("2. Merge with archaeological finds (PAS database)")
    print("3. Calculate treasure probability scores")
    print("4. Import into Leaflet.js GIS map")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_battles.py <battles.csv>")
        sys.exit(1)

    try:
        analyze_battle_csv(sys.argv[1])
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
