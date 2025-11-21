-- ============================================
-- MIGRATION 001: Performance Indexes
-- ============================================
-- Purpose: Add indexes to optimize enhanced API queries
-- Applied: [DATE]
-- ============================================

-- Full-text search optimization
-- Create GIN index for array search on sides_involved
CREATE INDEX IF NOT EXISTS idx_battles_sides_involved_gin
ON battles USING GIN(sides_involved);

-- Create index for case-insensitive name search
CREATE INDEX IF NOT EXISTS idx_battles_name_lower
ON battles (LOWER(name));

-- Create index for case-insensitive outcome search
CREATE INDEX IF NOT EXISTS idx_battles_outcome_lower
ON battles (LOWER(outcome));

-- Bounding box search optimization
-- Composite index for lat/lng range queries
CREATE INDEX IF NOT EXISTS idx_battles_lat_lng
ON battles (latitude, longitude);

-- Date range queries optimization
CREATE INDEX IF NOT EXISTS idx_battles_start_date
ON battles (start_date) WHERE start_date IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_battles_end_date
ON battles (end_date) WHERE end_date IS NOT NULL;

-- Casualties queries optimization
CREATE INDEX IF NOT EXISTS idx_battles_casualties
ON battles (casualties_estimated) WHERE casualties_estimated IS NOT NULL;

-- Composite indexes for common filter combinations
CREATE INDEX IF NOT EXISTS idx_battles_period_country
ON battles (war_period, country);

CREATE INDEX IF NOT EXISTS idx_battles_period_significance
ON battles (war_period, significance);

-- Update schema version
INSERT INTO schema_version (version, description)
VALUES (2, 'Migration 001: Added performance indexes for enhanced API queries')
ON CONFLICT (version) DO NOTHING;

-- ============================================
-- ANALYZE TABLES (update statistics for query planner)
-- ============================================
ANALYZE battles;

-- ============================================
-- VERIFY INDEXES
-- ============================================
-- Run this to see all indexes:
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'battles' ORDER BY indexname;

COMMENT ON INDEX idx_battles_sides_involved_gin IS 'GIN index for fast array search in sides_involved field';
COMMENT ON INDEX idx_battles_name_lower IS 'Case-insensitive search on battle names';
COMMENT ON INDEX idx_battles_outcome_lower IS 'Case-insensitive search on battle outcomes';
COMMENT ON INDEX idx_battles_lat_lng IS 'Composite index for bounding box queries';
