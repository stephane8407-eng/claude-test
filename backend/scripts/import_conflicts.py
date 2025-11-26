#!/usr/bin/env python3
import json, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.local_conflict import LocalConflict
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://spv_admin@localhost:5432/spv_treasure_map')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def parse_date(date_str):
    if not date_str:
        return None, None, None
    
    date_text = date_str.strip()
    
    # BC dates
    if 'BC' in date_text.upper() or 'BCE' in date_text.upper():
        return None, date_text, 'circa'
    
    # Try to parse
    for fmt, precision in [('%Y-%m-%d', 'day'), ('%Y-%m', 'month'), ('%Y', 'year')]:
        try:
            clean_date = date_text.split()[0] if ' ' in date_text else date_text
            date_obj = datetime.strptime(clean_date, fmt).date()
            return date_obj, date_text, precision
        except ValueError:
            continue
    
    return None, date_text, 'circa'

def import_conflicts(json_file: str):
    print(f"\n📂 Reading {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    conflicts_data = data.get('conflicts', [])
    print(f"✅ Found {len(conflicts_data)} conflicts\n")
    
    stats = {'total': len(conflicts_data), 'inserted': 0, 'skipped': 0, 'by_period': {}}
    db = SessionLocal()
    
    try:
        for i, cd in enumerate(conflicts_data, 1):
            try:
                name = cd.get('name', 'Unnamed')
                period = cd.get('period', 'Unknown')
                lat, lng = cd.get('latitude'), cd.get('longitude')
                
                stats['by_period'][period] = stats['by_period'].get(period, 0) + 1
                
                if db.query(LocalConflict).filter(LocalConflict.name == name).first():
                    stats['skipped'] += 1
                    continue
                
                if not lat or not lng:
                    continue
                
                date_obj, date_str, date_precision = parse_date(cd.get('date', ''))
                
                conflict = LocalConflict(
                    name=name,
                    date=date_obj,
                    date_str=date_str,
                    date_precision=date_precision,
                    location=cd.get('location', ''),
                    latitude=float(lat),
                    longitude=float(lng),
                    conflict_type=cd.get('conflict_type', 'battle'),
                    period=period,
                    participants=cd.get('participants', []),
                    casualties=cd.get('casualties'),
                    outcome=cd.get('outcome', ''),
                    strategic_importance=cd.get('description', ''),
                    impact_today=cd.get('impact_today', {}),
                    sources=cd.get('sources', []),
                    confidence_score=cd.get('confidence_score', 50),
                    scraper_location_name='Chirac',
                    scraper_department='Charente',
                    scraper_region='Nouvelle-Aquitaine',
                    scraper_radius_km=100.0
                )
                
                db.add(conflict)
                stats['inserted'] += 1
                if stats['inserted'] % 10 == 0:
                    print(f"✅ Imported {stats['inserted']}...")
                    
            except Exception as e:
                print(f"❌ {cd.get('name', 'unknown')}: {e}")
        
        db.commit()
        print(f"\n💾 Committed {stats['inserted']} conflicts")
    finally:
        db.close()
    
    print("\n" + "="*70)
    print("📊 IMPORT SUMMARY")
    print("="*70)
    print(f"Total: {stats['total']}")
    print(f"✅ Imported: {stats['inserted']}")
    print(f"⏭️ Skipped: {stats['skipped']}")
    print("\n📈 By Period:")
    for period, count in sorted(stats['by_period'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {period}: {count}")
    print("="*70)
    print(f"\n✅ IMPORT COMPLETE! Refresh map to see {stats['inserted']} new markers!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_conflicts.py <json_file>")
        sys.exit(1)
    import_conflicts(sys.argv[1])
