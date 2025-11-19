-- ============================================
-- SPV TREASURE MAP - PHASE 1 MVP SCHEMA
-- ============================================
-- Purpose: Core schema for Chirac + Stevenage pilots
-- Timeline: Week 1-2
-- Features: Battles, Places, AI Context, Basic Users, Analytics
-- What's NOT here: Subscriptions, Routes, Business Directory (Phase 2-3)
-- ============================================

-- Enable PostGIS extension (for spatial data)
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- LAYER 0: BATTLES (3,439 battles ready to import)
-- ============================================

CREATE TABLE battles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    war_period VARCHAR(100), -- "WW1", "WW2", "Napoleonic", "Medieval", "Roman", etc.
    start_date DATE,
    end_date DATE,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    country VARCHAR(2), -- ISO code: FR, UK, BE
    sides_involved TEXT[], -- Array: ["Allies", "Axis"]
    outcome VARCHAR(50), -- "Allied victory", "German victory", "Inconclusive", etc.
    significance VARCHAR(20), -- "minor", "moderate", "major"
    casualties_estimated INTEGER,
    sources TEXT[], -- Array of URLs
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Spatial index for finding battles near locations
CREATE INDEX idx_battles_location ON battles USING gist(
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

-- Indexes for filtering
CREATE INDEX idx_battles_period ON battles(war_period);
CREATE INDEX idx_battles_country ON battles(country);
CREATE INDEX idx_battles_significance ON battles(significance);

COMMENT ON TABLE battles IS 'Layer 0: All battles across FR, UK, BE (3,439 total)';
COMMENT ON COLUMN battles.war_period IS 'Used for map filtering: WW1, WW2, Napoleonic, Medieval, etc.';
COMMENT ON COLUMN battles.significance IS 'For prioritizing display: minor/moderate/major';

-- ============================================
-- LAYER 1: PLACES (100 test villages → scale to 10,000)
-- ============================================

CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(2) NOT NULL, -- FR, UK, BE
    admin_code VARCHAR(20), -- INSEE code (FR), ONS code (UK), Statbel (BE)
    centroid_lat DECIMAL(10, 7) NOT NULL,
    centroid_lng DECIMAL(10, 7) NOT NULL,
    population INTEGER,
    area_km2 DECIMAL(10, 2),
    depth_level VARCHAR(20) DEFAULT 'light', -- "light", "partner", "flagship"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Spatial index for finding nearby places
CREATE INDEX idx_places_location ON places USING gist(
    ST_SetSRID(ST_MakePoint(centroid_lng, centroid_lat), 4326)
);

-- Indexes for filtering
CREATE INDEX idx_places_country ON places(country);
CREATE INDEX idx_places_depth ON places(depth_level);
CREATE INDEX idx_places_name ON places(name);

COMMENT ON TABLE places IS 'Layer 1: Villages, towns, communes - starts with 100, scales to 10,000';
COMMENT ON COLUMN places.depth_level IS 'Content depth: light (auto-generated), partner (£500/year), flagship (£1,500/year)';
COMMENT ON COLUMN places.admin_code IS 'Official government code for matching with INSEE/ONS datasets';

-- ============================================
-- LAYER 2: AI CONTEXT (AI scraper output - 260K chars per village)
-- ============================================

CREATE TABLE place_contexts (
    id SERIAL PRIMARY KEY,
    place_id INTEGER REFERENCES places(id) ON DELETE CASCADE,

    -- Processed summaries
    ai_summary TEXT, -- 2-3 paragraph overview
    key_events JSONB, -- [{date, title, description, source}]
    mentioned_units TEXT[], -- Military units found (e.g., ["British 5th Division", "German 6th Army"])
    nearby_places INTEGER[], -- Array of place IDs (for "See also" links)
    legends_summary TEXT, -- Brief folklore summary if found
    impact_today TEXT, -- Past → Present connection (key differentiator!)

    -- Metadata
    sources TEXT[], -- Array of URLs where info was scraped
    scraping_method VARCHAR(20) DEFAULT 'ai-led', -- "basic", "ai-led"
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    raw_intelligence_json JSONB, -- Full scraper output (all 260K chars for reference)
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_place_contexts_place ON place_contexts(place_id);
CREATE INDEX idx_place_contexts_confidence ON place_contexts(confidence_score);
CREATE INDEX idx_place_contexts_updated ON place_contexts(last_updated);

COMMENT ON TABLE place_contexts IS 'Layer 2: AI-generated intelligence about each place (from scraper)';
COMMENT ON COLUMN place_contexts.confidence_score IS 'AI assessment: 0-100 (Chirac: 72, Manot: 78, Exideuil: 82)';
COMMENT ON COLUMN place_contexts.raw_intelligence_json IS 'Full scraper output (260K+ chars) - keep for reference/debugging';
COMMENT ON COLUMN place_contexts.impact_today IS 'KEY FEATURE: How this place''s history affects it today';

-- ============================================
-- USERS (Basic - just for admin access in MVP)
-- ============================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- bcrypt hashed
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    user_role VARCHAR(20) DEFAULT 'free', -- "admin", "free" (add more roles in Phase 2)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(user_role);

COMMENT ON TABLE users IS 'MVP: Just admin access. Phase 2 will add: founding_member, commune_admin, explorer';

-- ============================================
-- ANALYTICS (Simple event logging for MVP)
-- ============================================

CREATE TABLE usage_events (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- "page_view", "map_click", "battle_view", "place_view"

    -- References (nullable - not every event has all)
    place_id INTEGER REFERENCES places(id) ON DELETE SET NULL,
    battle_id INTEGER REFERENCES battles(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, -- NULL if anonymous

    -- Session tracking
    session_id VARCHAR(100), -- Browser session ID
    ip_address_hash VARCHAR(64), -- Hashed for privacy (GDPR-friendly)
    user_agent TEXT, -- Browser info
    referrer VARCHAR(500), -- Where did they come from?

    -- Flexible data
    metadata JSONB, -- Any additional event-specific data

    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_events_type ON usage_events(event_type);
CREATE INDEX idx_usage_events_place ON usage_events(place_id);
CREATE INDEX idx_usage_events_battle ON usage_events(battle_id);
CREATE INDEX idx_usage_events_timestamp ON usage_events(timestamp);
CREATE INDEX idx_usage_events_session ON usage_events(session_id);

COMMENT ON TABLE usage_events IS 'Simple event logging. Phase 2 will add pre-computed daily_analytics for dashboards';
COMMENT ON COLUMN usage_events.ip_address_hash IS 'SHA256 hashed for privacy - cannot reverse to real IP';

-- ============================================
-- HELPER FUNCTIONS (useful for queries)
-- ============================================

-- Function to find battles near a place (within X km)
CREATE OR REPLACE FUNCTION battles_near_place(
    p_place_id INTEGER,
    p_radius_km DECIMAL DEFAULT 50
)
RETURNS TABLE (
    battle_id INTEGER,
    battle_name VARCHAR(255),
    distance_km DECIMAL,
    war_period VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.id,
        b.name,
        ROUND(
            ST_Distance(
                ST_SetSRID(ST_MakePoint(p.centroid_lng, p.centroid_lat), 4326)::geography,
                ST_SetSRID(ST_MakePoint(b.longitude, b.latitude), 4326)::geography
            ) / 1000, 2
        ) AS distance_km,
        b.war_period
    FROM battles b
    CROSS JOIN places p
    WHERE p.id = p_place_id
        AND ST_DWithin(
            ST_SetSRID(ST_MakePoint(p.centroid_lng, p.centroid_lat), 4326)::geography,
            ST_SetSRID(ST_MakePoint(b.longitude, b.latitude), 4326)::geography,
            p_radius_km * 1000 -- Convert km to meters
        )
    ORDER BY distance_km;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION battles_near_place IS 'Find all battles within X km of a place - useful for "Nearby battles" section';

-- Function to find places near a battle (within X km)
CREATE OR REPLACE FUNCTION places_near_battle(
    p_battle_id INTEGER,
    p_radius_km DECIMAL DEFAULT 20
)
RETURNS TABLE (
    place_id INTEGER,
    place_name VARCHAR(255),
    distance_km DECIMAL,
    depth_level VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        ROUND(
            ST_Distance(
                ST_SetSRID(ST_MakePoint(b.longitude, b.latitude), 4326)::geography,
                ST_SetSRID(ST_MakePoint(p.centroid_lng, p.centroid_lat), 4326)::geography
            ) / 1000, 2
        ) AS distance_km,
        p.depth_level
    FROM places p
    CROSS JOIN battles b
    WHERE b.id = p_battle_id
        AND ST_DWithin(
            ST_SetSRID(ST_MakePoint(b.longitude, b.latitude), 4326)::geography,
            ST_SetSRID(ST_MakePoint(p.centroid_lng, p.centroid_lat), 4326)::geography,
            p_radius_km * 1000
        )
    ORDER BY distance_km;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION places_near_battle IS 'Find all places within X km of a battle - useful for "Affected villages" section';

-- ============================================
-- SAMPLE DATA QUERIES (for testing after import)
-- ============================================

-- Example: Find all WW1 battles in France
-- SELECT * FROM battles WHERE war_period = 'WW1' AND country = 'FR' ORDER BY name;

-- Example: Get Chirac's AI context
-- SELECT ai_summary, confidence_score FROM place_contexts
-- JOIN places ON places.id = place_contexts.place_id
-- WHERE places.name = 'Chirac';

-- Example: Find battles near Chirac (within 50km)
-- SELECT * FROM battles_near_place(1, 50); -- Assuming Chirac is ID 1

-- Example: Count events by type today
-- SELECT event_type, COUNT(*)
-- FROM usage_events
-- WHERE DATE(timestamp) = CURRENT_DATE
-- GROUP BY event_type;

-- ============================================
-- DEFERRED TO PHASE 2 (Week 3)
-- ============================================
-- These tables will be added via migration when needed:
-- - Add subscription columns to places table
-- - local_businesses (sponsor directory)
-- - daily_analytics (pre-computed stats)
-- - routes (auto-generated + hand-crafted)
-- - route_stops
--
-- See: IMPLEMENTATION_ROADMAP.md for details
-- ============================================

-- Schema version tracking
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO schema_version (version, description)
VALUES (1, 'Phase 1 MVP: Battles, Places, AI Context, Basic Users, Analytics');

-- ============================================
-- END OF PHASE 1 MVP SCHEMA
-- ============================================
