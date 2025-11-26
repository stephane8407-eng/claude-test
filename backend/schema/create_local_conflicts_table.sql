-- ============================================
-- LOCAL CONFLICTS TABLE - Phase 2
-- ============================================
-- Purpose: Store AI-scraped conflict events from ai_conflict_scraper.py
-- Data source: ConflictEvent objects with 6-category impact framework
-- ============================================

CREATE TABLE local_conflicts (
    id SERIAL PRIMARY KEY,

    -- Basic Information
    name VARCHAR(500) NOT NULL,
    date DATE,
    date_str VARCHAR(50), -- Store original date string (e.g., "1944-07-31")
    date_precision VARCHAR(20), -- "day", "month", "year", "circa"
    location VARCHAR(500) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),

    -- Conflict Classification
    conflict_type VARCHAR(50), -- "battle", "siege", "skirmish", "raid", "occupation", "bombardment", "other"
    period VARCHAR(50), -- "ancient", "medieval", "renaissance", "revolutionary", "napoleonic", "ww1", "ww2", "modern"
    duration VARCHAR(100), -- "1 day", "2 weeks", etc.

    -- Participants & Outcome (JSONB for complex structure)
    participants JSONB, -- Array of {name, side, role}
    casualties JSONB, -- {side1: int, side2: int, civilians: int} or "unknown"
    outcome TEXT,

    -- Context & Analysis
    strategic_importance TEXT,
    preceding_events TEXT,
    consequences TEXT,

    -- 6-Category Impact Framework
    impact_today JSONB, -- {infrastructure, economy, identity, demographics, governance, tourism}

    -- Metadata
    sources TEXT[], -- Array of source descriptions
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),

    -- Scraping Metadata
    scraper_location_name VARCHAR(255), -- Original search location (e.g., "Chirac")
    scraper_department VARCHAR(255), -- Department searched
    scraper_region VARCHAR(255), -- Region searched
    scraper_timestamp TIMESTAMP,
    scraper_radius_km DECIMAL(6, 2), -- Search radius used

    -- Foreign Key (optional - links to places table if matching place exists)
    place_id INTEGER REFERENCES places(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Spatial index for finding conflicts near locations
CREATE INDEX idx_local_conflicts_location ON local_conflicts USING gist(
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

-- Indexes for filtering
CREATE INDEX idx_local_conflicts_period ON local_conflicts(period);
CREATE INDEX idx_local_conflicts_type ON local_conflicts(conflict_type);
CREATE INDEX idx_local_conflicts_date ON local_conflicts(date);
CREATE INDEX idx_local_conflicts_place_id ON local_conflicts(place_id);
CREATE INDEX idx_local_conflicts_confidence ON local_conflicts(confidence_score);

-- GIN indexes for JSONB columns (enables efficient querying)
CREATE INDEX idx_local_conflicts_participants ON local_conflicts USING gin(participants);
CREATE INDEX idx_local_conflicts_impact_today ON local_conflicts USING gin(impact_today);

COMMENT ON TABLE local_conflicts IS 'AI-scraped local conflict events with 6-category impact framework';
COMMENT ON COLUMN local_conflicts.date_precision IS 'Indicates reliability of date: day (most precise) > month > year > circa';
COMMENT ON COLUMN local_conflicts.participants IS 'JSONB array: [{name, side, role}, ...]';
COMMENT ON COLUMN local_conflicts.casualties IS 'JSONB object: {side1, side2, civilians} or string "unknown"';
COMMENT ON COLUMN local_conflicts.impact_today IS 'JSONB object: {infrastructure, economy, identity, demographics, governance, tourism}';
COMMENT ON COLUMN local_conflicts.confidence_score IS '0-100 score based on source quality and data completeness';
COMMENT ON COLUMN local_conflicts.scraper_location_name IS 'Location name used in ai_conflict_scraper.py search';
