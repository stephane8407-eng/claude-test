#!/usr/bin/env python3
"""
Import geocoded battles into PostgreSQL database.

Reads the geocoded CSV file and imports battles with coordinates
into the SPV Treasure Map database.

Usage:
    python import_battles.py <geocoded_csv>

Example:
    python import_battles.py ../../all_battles_geocoded.csv

Requirements:
    - PostgreSQL database 'spv_treasure_map' must exist
    - Database user 'spv_admin' with password configured in .env
    - PostGIS extension enabled
"""

import csv
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import engine, SessionLocal
from app.models import Battle


def parse_date(date_str: str) -> datetime.date:
    """
    Parse date string to date object.

    Handles various formats:
    - "14 October 1066"
    - "27 July 1214"
    - "26 August 1346"
    - Date ranges (returns start date)
    """
    if not date_str or date_str.strip() == '':
        return None

    try:
        # Try multiple date formats
        for fmt in [
            '%d %B %Y',     # 14 October 1066
            '%B %d %Y',     # October 14 1066
            '%Y-%m-%d',     # 1066-10-14
            '%d/%m/%Y',     # 14/10/1066
        ]:
            try:
                # Handle date ranges (take first date)
                date_clean = date_str.split('–')[0].split('-')[0].strip()
                return datetime.strptime(date_clean, fmt).date()
            except ValueError:
                continue

        # If all formats fail, return None
        return None

    except Exception as e:
        print(f"  ⚠️  Date parse error for '{date_str}': {e}")
        return None


def parse_sides_involved(participants: str) -> list:
    """
    Parse participants string into sides_involved array.

    Example: "Norman forces vs Anglo-Saxon forces" -> ["Norman forces", "Anglo-Saxon forces"]
    """
    if not participants or participants.strip() == '':
        return []

    # Split on common separators
    for separator in [' vs ', ' vs. ', ' v ', ' and ', ',']:
        if separator in participants:
            return [side.strip() for side in participants.split(separator)]

    # If no separator found, return as single item
    return [participants.strip()]


def import_battles(geocoded_csv: str):
    """
    Import geocoded battles from CSV into PostgreSQL.

    Args:
        geocoded_csv: Path to geocoded CSV file

    Returns:
        Statistics dictionary
    """
    print(f"💾 SPV Treasure Map - Battle Import")
    print(f"=" * 60)
    print(f"Input CSV: {geocoded_csv}")
    print(f"Database:  spv_treasure_map")
    print(f"=" * 60)
    print()

    # Read CSV
    print("📖 Reading geocoded CSV...")
    with open(geocoded_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        battles_data = list(reader)

    total_battles = len(battles_data)
    print(f"✅ Found {total_battles} battles in CSV")
    print()

    # Filter battles with coordinates
    valid_battles = [
        b for b in battles_data
        if b.get('latitude') and b.get('longitude') and
           b.get('latitude').strip() != '' and b.get('longitude').strip() != ''
    ]

    skipped_battles = total_battles - len(valid_battles)

    print(f"✅ Valid battles (with coordinates): {len(valid_battles)}")
    print(f"⚠️  Skipped (no coordinates): {skipped_battles}")
    print()

    if len(valid_battles) == 0:
        print("❌ No valid battles to import!")
        return

    # Create database session
    print("🔌 Connecting to database...")
    db = SessionLocal()

    try:
        # Check if battles table exists
        result = db.execute(text("SELECT COUNT(*) FROM battles"))
        existing_count = result.scalar()
        print(f"✅ Connected. Current battles in DB: {existing_count}")
        print()

        # Ask for confirmation if battles already exist
        if existing_count > 0:
            print(f"⚠️  WARNING: {existing_count} battles already exist in database.")
            response = input("Do you want to DELETE all existing battles and import new ones? (yes/no): ")
            if response.lower() == 'yes':
                print("🗑️  Deleting existing battles...")
                db.execute(text("DELETE FROM battles"))
                db.commit()
                print("✅ Existing battles deleted")
            else:
                print("ℹ️  Keeping existing battles. New battles will be added.")
            print()

        # Import battles
        print(f"📥 Importing {len(valid_battles)} battles...")
        success_count = 0
        failed_count = 0

        for i, battle_data in enumerate(valid_battles, 1):
            try:
                # Parse data
                latitude = float(battle_data['latitude'])
                longitude = float(battle_data['longitude'])
                year = int(battle_data['year']) if battle_data.get('year', '').isdigit() else None

                # Parse date
                start_date = parse_date(battle_data.get('date', ''))
                end_date = None  # TODO: Handle date ranges if needed

                # Parse sides
                sides = parse_sides_involved(battle_data.get('participants', ''))

                # Create battle record
                battle = Battle(
                    name=battle_data.get('name', 'Unknown Battle').strip(),
                    war_period=battle_data.get('war_period', '').strip() or None,
                    start_date=start_date,
                    end_date=end_date,
                    latitude=latitude,
                    longitude=longitude,
                    country=battle_data.get('country', '').strip()[:2] or None,
                    sides_involved=sides if sides else None,
                    outcome=battle_data.get('outcome', '').strip() or None,
                    significance=battle_data.get('significance', 'moderate').strip(),
                    casualties_estimated=int(battle_data['casualties_estimated']) if battle_data.get('casualties_estimated', '').isdigit() else None,
                    sources=[]  # TODO: Parse sources if available
                )

                db.add(battle)
                success_count += 1

                # Progress report every 100 battles
                if i % 100 == 0:
                    db.commit()  # Commit in batches
                    print(f"  Progress: {i}/{len(valid_battles)} ({i/len(valid_battles)*100:.1f}%)")

            except Exception as e:
                print(f"  ❌ Failed to import '{battle_data.get('name', 'Unknown')}': {e}")
                failed_count += 1
                continue

        # Final commit
        db.commit()

        print()
        print(f"=" * 60)
        print(f"✅ IMPORT COMPLETE")
        print(f"=" * 60)
        print(f"Total battles in CSV:     {total_battles}")
        print(f"Valid battles (coords):   {len(valid_battles)}")
        print(f"Successfully imported:    {success_count}")
        print(f"Failed:                   {failed_count}")
        print(f"Skipped (no coords):      {skipped_battles}")
        print()

        # Verify import
        result = db.execute(text("SELECT COUNT(*) FROM battles"))
        final_count = result.scalar()
        print(f"✅ Total battles in database: {final_count}")
        print()

        # Statistics by country
        result = db.execute(text("""
            SELECT country, COUNT(*) as count
            FROM battles
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
        """))

        print("📍 Battles by country:")
        for row in result:
            print(f"   {row[0]}: {row[1]}")
        print()

        # Statistics by war period
        result = db.execute(text("""
            SELECT war_period, COUNT(*) as count
            FROM battles
            WHERE war_period IS NOT NULL
            GROUP BY war_period
            ORDER BY count DESC
        """))

        print("⚔️  Battles by war period:")
        for row in result:
            print(f"   {row[0]}: {row[1]}")
        print()

        print("🎉 Import successful!")

    except Exception as e:
        print(f"❌ Import failed: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_battles.py <geocoded_csv>")
        print()
        print("Example:")
        print("  python import_battles.py ../../all_battles_geocoded.csv")
        sys.exit(1)

    geocoded_csv = sys.argv[1]

    if not os.path.exists(geocoded_csv):
        print(f"❌ Error: File not found: {geocoded_csv}")
        sys.exit(1)

    import_battles(geocoded_csv)
