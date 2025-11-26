#!/usr/bin/env python3
"""
Generate data snapshot for Chirac village
This computes all the stats needed for AI identity generation
Run: python backend/scripts/week3_generate_chirac_snapshot.py
"""
import sys
sys.path.insert(0, '/Users/stephanevergnaud/Documents/treasure-hunting/claude-test/backend')

from app.database import SessionLocal
from app.models import Village, LocalConflict, POI, VillageDataSnapshot
from sqlalchemy import func
from collections import Counter

def generate_chirac_snapshot():
    db = SessionLocal()

    try:
        # Get Chirac
        chirac = db.query(Village).filter(Village.slug == "chirac").first()
        if not chirac:
            print("❌ Chirac village not found!")
            return

        print(f"✅ Found Chirac (ID: {chirac.id})")

        # Clear existing snapshots
        db.query(VillageDataSnapshot).filter(VillageDataSnapshot.village_id == chirac.id).delete()
        db.commit()
        print("🧹 Cleared existing snapshots")

        # ==================================
        # COMPUTE CONFLICT DATA
        # ==================================

        conflicts = db.query(LocalConflict).filter(LocalConflict.village_id == chirac.id).all()
        total_conflicts = len(conflicts)
        print(f"\n📊 Analyzing {total_conflicts} conflicts...")

        # Group by period
        conflicts_by_period = {}
        for conflict in conflicts:
            period = conflict.period or "Unknown"
            conflicts_by_period[period] = conflicts_by_period.get(period, 0) + 1

        # Group by type (use conflict_type field directly)
        conflicts_by_type = {}
        for conflict in conflicts:
            conflict_type = conflict.conflict_type or "unknown"
            conflicts_by_type[conflict_type] = conflicts_by_type.get(conflict_type, 0) + 1

        # Most destructive (sort by confidence_score)
        most_destructive = sorted(
            conflicts,
            key=lambda c: c.confidence_score if c.confidence_score else 0,
            reverse=True
        )[:5]

        most_destructive_data = [
            {
                "id": c.id,
                "name": c.name,
                "year": c.date.year if c.date else None,
                "period": c.period,
                "confidence_score": c.confidence_score,
                "outcome": c.outcome[:200] if c.outcome else None
            }
            for c in most_destructive
        ]

        # Conflict density (conflicts per 100 years)
        # Chirac data spans ~2500 years (500 BC to 2000 AD)
        conflict_density = round(total_conflicts / 25, 2)  # 25 centuries

        print(f"   Conflicts by period: {conflicts_by_period}")
        print(f"   Conflict density: {conflict_density} per century")

        # ==================================
        # COMPUTE POI DATA
        # ==================================

        pois = db.query(POI).filter(POI.village_id == chirac.id).all()
        total_pois = len(pois)
        print(f"\n🏛️ Analyzing {total_pois} POIs...")

        # Group by type
        pois_by_type = {}
        heritage_count = 0
        for poi in pois:
            # Group by type_id
            type_id = str(poi.poi_type_id) if poi.poi_type_id else "unknown"
            pois_by_type[f"type_{type_id}"] = pois_by_type.get(f"type_{type_id}", 0) + 1

            # Count heritage buildings (check attributes for heritage info)
            if poi.attributes and poi.attributes.get('heritage_status'):
                heritage_count += 1

        print(f"   POIs by type: {pois_by_type}")
        print(f"   Heritage buildings: {heritage_count}")

        # ==================================
        # COMPUTE SCORES
        # ==================================

        # Conflict trauma score (0.0-1.0)
        # Based on: conflict density, destructive events
        trauma_score = min(1.0, conflict_density / 10)  # 10+ conflicts/century = max trauma

        # Resilience score (0.0-1.0)
        # Based on: still exists, has heritage, population
        resilience_score = 0.75  # Chirac survived, has POIs, still populated

        # Heritage richness score (0.0-1.0)
        # Based on: number of heritage POIs, diversity
        heritage_score = min(1.0, heritage_count / 10)  # 10+ heritage = max

        # Tourism potential score (0.0-1.0)
        # Based on: conflicts + POIs + heritage
        tourism_score = min(1.0, (total_conflicts / 100 + total_pois / 20 + heritage_count / 10) / 3)

        print(f"\n🎯 Computed Scores:")
        print(f"   Trauma: {trauma_score:.2f}")
        print(f"   Resilience: {resilience_score:.2f}")
        print(f"   Heritage: {heritage_score:.2f}")
        print(f"   Tourism Potential: {tourism_score:.2f}")

        # ==================================
        # CREATE SNAPSHOT
        # ==================================

        snapshot = VillageDataSnapshot(
            village_id=chirac.id,
            data_version="v1.0",

            # Conflict data
            total_conflicts=total_conflicts,
            conflicts_by_period=conflicts_by_period,
            conflicts_by_type=conflicts_by_type,
            most_destructive_conflicts=most_destructive_data,
            conflict_density_score=conflict_density,

            # POI data
            total_pois=total_pois,
            pois_by_type=pois_by_type,
            heritage_buildings=heritage_count,

            # Demographics (placeholder - will add INSEE data later)
            current_population=800,
            population_peak=1200,
            population_peak_year=1850,
            population_decline_pct=33.33,

            # Economy (placeholder)
            primary_industry="Agriculture",

            # Geography (Chirac context)
            distance_to_major_city=45,  # ~45km to Angoulême
            border_proximity=False,
            strategic_location="River crossing, trade route",

            # Computed scores
            conflict_trauma_score=trauma_score,
            resilience_score=resilience_score,
            heritage_richness_score=heritage_score,
            tourism_potential_score=tourism_score
        )

        db.add(snapshot)
        db.commit()

        print(f"\n🎉 SUCCESS! Created data snapshot for Chirac")
        print(f"   Snapshot ID: {snapshot.id}")
        print(f"   Ready for AI identity generation in Week 4!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_chirac_snapshot()
