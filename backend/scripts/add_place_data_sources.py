#!/usr/bin/env python3
"""
Migration: Add place_data_sources table for future-proof multi-source data collection
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://spv_admin@localhost:5432/spv_treasure_map"
)

def run_migration():
    print("🔄 Starting migration: add_place_data_sources")
    print(f"📊 Database: {DATABASE_URL.split('@')[1]}")
    
    engine = create_engine(DATABASE_URL)
    
    migration_sql = """
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                      WHERE table_name = 'place_data_sources') THEN
            
            CREATE TABLE place_data_sources (
                id SERIAL PRIMARY KEY,
                place_id INTEGER REFERENCES places(id) ON DELETE CASCADE,
                source_type VARCHAR(50) NOT NULL,
                source_name TEXT,
                source_url TEXT,
                license_type VARCHAR(100),
                attribution TEXT,
                confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
                data_collected JSONB,
                cost_usd DECIMAL(10, 4) DEFAULT 0.0000,
                collected_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX idx_pds_place_id ON place_data_sources(place_id);
            CREATE INDEX idx_pds_source_type ON place_data_sources(source_type);
            CREATE INDEX idx_pds_collected_at ON place_data_sources(collected_at);
            CREATE INDEX idx_pds_confidence ON place_data_sources(confidence_score);
            CREATE INDEX idx_pds_cost ON place_data_sources(cost_usd);
            
            RAISE NOTICE '✅ Created place_data_sources table';
        ELSE
            RAISE NOTICE '⚠️  Table already exists - skipping';
        END IF;
    END $$;
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(migration_sql))
            conn.commit()
            
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name = 'place_data_sources'
            """))
            
            if result.fetchone()[0] == 1:
                print("\n✅ SUCCESS! Migration completed")
                print("\n🎯 Database is now future-proof!")
                print("   You can add new data sources without breaking existing data.")
                return True
            else:
                print("\n❌ ERROR: Table not found after creation")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  MIGRATION: Add place_data_sources Table")
    print("="*60 + "\n")
    
    success = run_migration()
    sys.exit(0 if success else 1)
