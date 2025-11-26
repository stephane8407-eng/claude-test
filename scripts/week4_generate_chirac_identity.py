#!/usr/bin/env python3
"""
Week 4: Generate AI Identity Themes for Chirac

This script generates 3 identity themes for Chirac village:
1. "Phoenix Village" (infrastructure category)
2. "Sleeping Waters" (economy category)
3. "Heritage Trail" (tourism category)
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Village, IdentityCategory, IdentityTheme, VillageDataSnapshot
from app.services.identity_generator import IdentityGenerator


def generate_chirac_themes():
    """Generate 3 identity themes for Chirac village"""

    db = SessionLocal()

    try:
        print("=" * 80)
        print("WEEK 4: AI IDENTITY THEME GENERATION FOR CHIRAC")
        print("=" * 80)
        print()

        # 1. Find Chirac village
        print("1. Looking up Chirac village...")
        village = db.query(Village).filter(Village.slug == 'chirac').first()

        if not village:
            print("   ERROR: Chirac village not found!")
            return False

        print(f"   ✓ Found: {village.name} (ID: {village.id})")
        print()

        # 2. Check data snapshot
        print("2. Checking for data snapshot...")
        snapshot = db.query(VillageDataSnapshot).filter(
            VillageDataSnapshot.village_id == village.id
        ).order_by(VillageDataSnapshot.snapshot_date.desc()).first()

        if not snapshot:
            print("   ERROR: No data snapshot found for Chirac!")
            return False

        print(f"   ✓ Data snapshot found:")
        print(f"     - Total conflicts: {snapshot.total_conflicts}")
        print(f"     - Total POIs: {snapshot.total_pois}")
        print(f"     - Conflict trauma score: {snapshot.conflict_trauma_score}")
        print(f"     - Resilience score: {snapshot.resilience_score}")
        print(f"     - Heritage richness score: {snapshot.heritage_richness_score}")
        print(f"     - Tourism potential score: {snapshot.tourism_potential_score}")
        print()

        # 3. Get the 3 target categories
        print("3. Looking up target categories...")
        target_categories = ['infrastructure', 'economy', 'tourism']

        categories = db.query(IdentityCategory).filter(
            IdentityCategory.name.in_(target_categories)
        ).all()

        if len(categories) != 3:
            print(f"   ERROR: Expected 3 categories, found {len(categories)}")
            return False

        print(f"   ✓ Found {len(categories)} categories:")
        for cat in categories:
            print(f"     - {cat.name} (ID: {cat.id})")
        print()

        # 4. Initialize AI generator
        print("4. Initializing Claude AI generator...")
        try:
            generator = IdentityGenerator()
            print(f"   ✓ Connected to Claude API (model: {generator.model})")
        except Exception as e:
            print(f"   ERROR: Failed to initialize generator: {e}")
            return False
        print()

        # 5. Generate themes
        print("5. Generating AI identity themes...")
        print("   (This may take 30-60 seconds per theme...)")
        print()

        generated_themes = []

        for i, category in enumerate(categories, 1):
            print(f"   [{i}/3] Generating theme for category: {category.name}...")

            try:
                # Generate theme
                theme_data = generator.generate_theme(db, village, category, snapshot)

                # Save to database
                theme = generator.save_theme_to_db(db, theme_data)

                print(f"        ✓ Generated: \"{theme.theme_name}\"")
                print(f"          Tagline: {theme.tagline}")
                print(f"          Confidence: {theme.confidence_score}")
                print(f"          Evidence conflicts: {len(theme.evidence_conflicts or [])}")
                print(f"          Evidence POIs: {len(theme.evidence_pois or [])}")
                print(f"          Project ideas: {len(theme.project_ideas or [])}")
                print()

                generated_themes.append(theme)

            except Exception as e:
                print(f"        ERROR: Failed to generate theme: {e}")
                continue

        # 6. Mark snapshot as used
        if generated_themes:
            print(f"6. Marking data snapshot as used for identity generation...")
            snapshot.used_for_identity_generation = True
            from datetime import datetime
            snapshot.identity_generation_timestamp = datetime.now()
            db.commit()
            print(f"   ✓ Snapshot marked as used")
            print()

        # 7. Summary
        print("=" * 80)
        print(f"GENERATION COMPLETE: {len(generated_themes)}/3 themes generated")
        print("=" * 80)
        print()

        for theme in generated_themes:
            print(f"Theme ID {theme.id}: {theme.theme_name}")
            print(f"  Category: {theme.category.name if theme.category else 'Unknown'}")
            print(f"  Tagline: {theme.tagline}")
            print(f"  Confidence: {theme.confidence_score}")
            print()

        return len(generated_themes) > 0

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = generate_chirac_themes()
    sys.exit(0 if success else 1)
