-- V1 Product Spec: Create QR Tables
-- Creates missing tables: qr_routes, qr_codes, qr_scans
-- Date: November 28, 2024

-- ==========================================
-- Table 1: qr_routes (Tourism walking routes)
-- ==========================================

CREATE TABLE IF NOT EXISTS qr_routes (
    id SERIAL PRIMARY KEY,
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,

    -- Route information
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE,
    description TEXT,

    -- V1 Spec: Route details
    hero_image_url VARCHAR(500),
    gpx_url VARCHAR(500),
    distance_km DECIMAL(5,2),
    duration_minutes INTEGER,
    route_type VARCHAR(50),              -- 'walk', 'hike', 'cycle', 'trail_run'
    difficulty VARCHAR(20),              -- 'easy', 'medium', 'hard'
    school_friendly BOOLEAN DEFAULT FALSE,
    themes TEXT[],
    waypoints JSONB,                     -- Array of {lat, lng, name, description, placeId?}

    -- Legacy fields
    poi_ids JSONB,                       -- JSON array of POI IDs in route order
    distance_meters INTEGER,

    -- Status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_qr_routes_village ON qr_routes(village_id);
CREATE INDEX IF NOT EXISTS idx_qr_routes_slug ON qr_routes(slug);
CREATE INDEX IF NOT EXISTS idx_qr_routes_route_type ON qr_routes(route_type);
CREATE INDEX IF NOT EXISTS idx_qr_routes_difficulty ON qr_routes(difficulty);
CREATE INDEX IF NOT EXISTS idx_qr_routes_school_friendly ON qr_routes(school_friendly);
CREATE INDEX IF NOT EXISTS idx_qr_routes_themes ON qr_routes USING gin(themes);
CREATE INDEX IF NOT EXISTS idx_qr_routes_active ON qr_routes(is_active);

COMMENT ON TABLE qr_routes IS 'Tourism walking routes linking multiple POIs';
COMMENT ON COLUMN qr_routes.waypoints IS 'Array of waypoint objects: [{lat, lng, name, description, placeId?}]';
COMMENT ON COLUMN qr_routes.gpx_url IS 'URL to GPX file for route mapping';


-- ==========================================
-- Table 2: qr_codes (Trackable QR codes)
-- ==========================================

CREATE TABLE IF NOT EXISTS qr_codes (
    id SERIAL PRIMARY KEY,
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,
    poi_id INTEGER REFERENCES pois(id) ON DELETE SET NULL,
    battle_id INTEGER REFERENCES battles(id) ON DELETE SET NULL,
    route_id INTEGER REFERENCES qr_routes(id) ON DELETE SET NULL,

    -- QR code identifier (unique short code, e.g., "spv-chirac-001")
    code VARCHAR(50) UNIQUE NOT NULL,

    -- QR code metadata
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Target URL (where the QR code redirects)
    target_url TEXT NOT NULL,

    -- Stored QR code image URL (path to generated image)
    qr_image_url TEXT,

    -- Tracking
    scan_count INTEGER DEFAULT 0 NOT NULL,
    last_scanned_at TIMESTAMP,

    -- Status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_qr_codes_village ON qr_codes(village_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_code ON qr_codes(code);
CREATE INDEX IF NOT EXISTS idx_qr_codes_poi ON qr_codes(poi_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_battle ON qr_codes(battle_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_route ON qr_codes(route_id);
CREATE INDEX IF NOT EXISTS idx_qr_codes_active ON qr_codes(is_active);

COMMENT ON TABLE qr_codes IS 'Trackable QR codes for POIs, battles, and routes';
COMMENT ON COLUMN qr_codes.code IS 'Unique short code for QR (e.g., spv-chirac-001)';


-- ==========================================
-- Table 3: qr_scans (Scan analytics)
-- ==========================================

CREATE TABLE IF NOT EXISTS qr_scans (
    id SERIAL PRIMARY KEY,
    qr_code_id INTEGER NOT NULL REFERENCES qr_codes(id) ON DELETE CASCADE,

    -- Scan metadata
    scanned_at TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Device info (from user agent)
    user_agent TEXT,
    device_type VARCHAR(50),             -- 'mobile', 'tablet', 'desktop'
    browser VARCHAR(100),
    os VARCHAR(100),

    -- Location (if available)
    ip_address VARCHAR(45),              -- IPv4 or IPv6
    country VARCHAR(2),
    city VARCHAR(100),

    -- Referrer
    referrer TEXT,

    -- Session tracking (optional)
    session_id VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_qr_scans_qr_code ON qr_scans(qr_code_id);
CREATE INDEX IF NOT EXISTS idx_qr_scans_scanned_at ON qr_scans(scanned_at DESC);
CREATE INDEX IF NOT EXISTS idx_qr_scans_device_type ON qr_scans(device_type);

COMMENT ON TABLE qr_scans IS 'Individual QR code scan events for analytics';


-- ==========================================
-- Add update triggers
-- ==========================================

-- qr_routes trigger
DROP TRIGGER IF EXISTS update_qr_routes_updated_at ON qr_routes;
CREATE TRIGGER update_qr_routes_updated_at
    BEFORE UPDATE ON qr_routes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- qr_codes trigger
DROP TRIGGER IF EXISTS update_qr_codes_updated_at ON qr_codes;
CREATE TRIGGER update_qr_codes_updated_at
    BEFORE UPDATE ON qr_codes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ==========================================
-- Verification
-- ==========================================

-- Verify tables were created
SELECT 'qr_routes' as table_name, COUNT(*) as row_count FROM qr_routes
UNION ALL
SELECT 'qr_codes', COUNT(*) FROM qr_codes
UNION ALL
SELECT 'qr_scans', COUNT(*) FROM qr_scans;
