-- V1 Product Spec: ALTER TABLE Migration
-- Adds missing fields to: villages, pois, local_conflicts, qr_routes
-- Date: November 28, 2024

-- ==========================================
-- Table 1: villages (Settlement entity)
-- ==========================================
-- Adding: summary_identity, long_identity, live_here_summary, hero_image_url, themes

ALTER TABLE villages
    ADD COLUMN IF NOT EXISTS summary_identity TEXT,
    ADD COLUMN IF NOT EXISTS long_identity TEXT,
    ADD COLUMN IF NOT EXISTS live_here_summary TEXT,
    ADD COLUMN IF NOT EXISTS hero_image_url VARCHAR(500),
    ADD COLUMN IF NOT EXISTS themes TEXT[];

-- Add index for theme-based filtering
CREATE INDEX IF NOT EXISTS idx_villages_themes ON villages USING gin(themes);

COMMENT ON COLUMN villages.summary_identity IS 'Short tagline for public display (1-2 sentences)';
COMMENT ON COLUMN villages.long_identity IS '1-3 paragraph narrative describing village identity';
COMMENT ON COLUMN villages.live_here_summary IS 'Content for "Living here" section on public page';
COMMENT ON COLUMN villages.hero_image_url IS 'URL to hero image for public village page';
COMMENT ON COLUMN villages.themes IS 'Array of theme tags for filtering (e.g., ww2, medieval, ponds)';


-- ==========================================
-- Table 2: pois (Place entity)
-- ==========================================
-- Adding: slug, hero_image_url, access, themes, status (rename if needed)

-- First check if status column exists and has correct definition
-- The existing status column is VARCHAR(20) default 'active', we need 'draft'/'published'

ALTER TABLE pois
    ADD COLUMN IF NOT EXISTS slug VARCHAR(100),
    ADD COLUMN IF NOT EXISTS hero_image_url VARCHAR(500),
    ADD COLUMN IF NOT EXISTS access VARCHAR(50) DEFAULT 'public',
    ADD COLUMN IF NOT EXISTS themes TEXT[];

-- Add unique constraint on slug (only if column was just added or doesn't have constraint)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'pois_slug_key' AND conrelid = 'pois'::regclass
    ) THEN
        -- Create unique index instead of constraint to handle NULLs gracefully
        CREATE UNIQUE INDEX IF NOT EXISTS idx_pois_slug_unique ON pois(slug) WHERE slug IS NOT NULL;
    END IF;
END $$;

-- Add index for theme-based filtering
CREATE INDEX IF NOT EXISTS idx_pois_themes ON pois USING gin(themes);
CREATE INDEX IF NOT EXISTS idx_pois_access ON pois(access);

COMMENT ON COLUMN pois.slug IS 'URL-friendly unique identifier for public pages';
COMMENT ON COLUMN pois.hero_image_url IS 'URL to hero image for place detail page';
COMMENT ON COLUMN pois.access IS 'Access type: public, private, ruin, restricted';
COMMENT ON COLUMN pois.themes IS 'Array of theme tags for filtering';

-- Note: existing 'status' column uses 'active'/'inactive', spec wants 'draft'/'published'
-- We'll keep both patterns - 'status' for admin visibility, could add 'publish_status' if needed


-- ==========================================
-- Table 3: local_conflicts (Event entity)
-- ==========================================
-- Adding: slug, event_type, scale, themes
-- Note: conflict_type already exists, event_type is more generic

ALTER TABLE local_conflicts
    ADD COLUMN IF NOT EXISTS slug VARCHAR(100),
    ADD COLUMN IF NOT EXISTS event_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS scale VARCHAR(20),
    ADD COLUMN IF NOT EXISTS themes TEXT[];

-- Add unique index on slug
CREATE UNIQUE INDEX IF NOT EXISTS idx_local_conflicts_slug_unique
    ON local_conflicts(slug) WHERE slug IS NOT NULL;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_local_conflicts_event_type ON local_conflicts(event_type);
CREATE INDEX IF NOT EXISTS idx_local_conflicts_scale ON local_conflicts(scale);
CREATE INDEX IF NOT EXISTS idx_local_conflicts_themes ON local_conflicts USING gin(themes);

COMMENT ON COLUMN local_conflicts.slug IS 'URL-friendly unique identifier for public pages';
COMMENT ON COLUMN local_conflicts.event_type IS 'Event type: battle, siege, festival, flood, etc.';
COMMENT ON COLUMN local_conflicts.scale IS 'Scale of event: local, regional, national';
COMMENT ON COLUMN local_conflicts.themes IS 'Array of theme tags for filtering';


-- ==========================================
-- Table 4: qr_routes (Route entity)
-- ==========================================
-- Adding: slug, hero_image_url, gpx_url, distance_km, route_type, school_friendly, themes, waypoints
-- Note: Some fields may already exist with different names

ALTER TABLE qr_routes
    ADD COLUMN IF NOT EXISTS slug VARCHAR(100),
    ADD COLUMN IF NOT EXISTS hero_image_url VARCHAR(500),
    ADD COLUMN IF NOT EXISTS gpx_url VARCHAR(500),
    ADD COLUMN IF NOT EXISTS distance_km DECIMAL(5,2),
    ADD COLUMN IF NOT EXISTS route_type VARCHAR(50),
    ADD COLUMN IF NOT EXISTS school_friendly BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS themes TEXT[],
    ADD COLUMN IF NOT EXISTS waypoints JSONB;

-- Rename existing columns to match spec if needed
-- estimated_duration_minutes -> duration_minutes (spec uses duration_minutes)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'qr_routes' AND column_name = 'estimated_duration_minutes'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'qr_routes' AND column_name = 'duration_minutes'
    ) THEN
        ALTER TABLE qr_routes RENAME COLUMN estimated_duration_minutes TO duration_minutes;
    END IF;
END $$;

-- Add duration_minutes if it doesn't exist after potential rename
ALTER TABLE qr_routes
    ADD COLUMN IF NOT EXISTS duration_minutes INTEGER;

-- Add unique index on slug
CREATE UNIQUE INDEX IF NOT EXISTS idx_qr_routes_slug_unique
    ON qr_routes(slug) WHERE slug IS NOT NULL;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_qr_routes_route_type ON qr_routes(route_type);
CREATE INDEX IF NOT EXISTS idx_qr_routes_school_friendly ON qr_routes(school_friendly);
CREATE INDEX IF NOT EXISTS idx_qr_routes_themes ON qr_routes USING gin(themes);
CREATE INDEX IF NOT EXISTS idx_qr_routes_difficulty ON qr_routes(difficulty);

COMMENT ON COLUMN qr_routes.slug IS 'URL-friendly unique identifier for public pages';
COMMENT ON COLUMN qr_routes.hero_image_url IS 'URL to hero image for route detail page';
COMMENT ON COLUMN qr_routes.gpx_url IS 'URL to GPX file for route mapping';
COMMENT ON COLUMN qr_routes.distance_km IS 'Total route distance in kilometers';
COMMENT ON COLUMN qr_routes.duration_minutes IS 'Estimated time to complete route in minutes';
COMMENT ON COLUMN qr_routes.route_type IS 'Type of route: walk, hike, cycle, trail_run';
COMMENT ON COLUMN qr_routes.school_friendly IS 'Whether route is suitable for school groups';
COMMENT ON COLUMN qr_routes.themes IS 'Array of theme tags for filtering';
COMMENT ON COLUMN qr_routes.waypoints IS 'Array of waypoint objects: [{lat, lng, name, description, placeId?}]';


-- ==========================================
-- Helper function to generate slugs
-- ==========================================

CREATE OR REPLACE FUNCTION generate_slug(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(
        regexp_replace(
            regexp_replace(
                regexp_replace(
                    -- Remove accents (basic French)
                    translate(input_text,
                        'àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ',
                        'aaaeeeeiioouuycAAÄEEEEIIOOUUUYC'),
                    '[^a-zA-Z0-9\s-]', '', 'g'  -- Remove special chars
                ),
                '\s+', '-', 'g'  -- Replace spaces with hyphens
            ),
            '-+', '-', 'g'  -- Collapse multiple hyphens
        )
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION generate_slug IS 'Generates URL-friendly slug from text input';


-- ==========================================
-- Backfill slugs for existing records
-- ==========================================

-- Generate slugs for POIs that don't have one
UPDATE pois
SET slug = generate_slug(name) || '-' || id
WHERE slug IS NULL;

-- Generate slugs for local_conflicts that don't have one
UPDATE local_conflicts
SET slug = generate_slug(name) || '-' || id
WHERE slug IS NULL;

-- Generate slugs for qr_routes that don't have one
UPDATE qr_routes
SET slug = generate_slug(name) || '-' || id
WHERE slug IS NULL;


-- ==========================================
-- Verification queries (run these to verify)
-- ==========================================

-- Check villages columns
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'villages'
-- AND column_name IN ('summary_identity', 'long_identity', 'live_here_summary', 'hero_image_url', 'themes');

-- Check pois columns
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'pois'
-- AND column_name IN ('slug', 'hero_image_url', 'access', 'themes');

-- Check local_conflicts columns
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'local_conflicts'
-- AND column_name IN ('slug', 'event_type', 'scale', 'themes');

-- Check qr_routes columns
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'qr_routes'
-- AND column_name IN ('slug', 'hero_image_url', 'gpx_url', 'distance_km', 'duration_minutes', 'route_type', 'school_friendly', 'themes', 'waypoints');
