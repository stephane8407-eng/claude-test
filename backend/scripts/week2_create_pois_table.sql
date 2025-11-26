-- Create pois table for village-specific points of interest
CREATE TABLE pois (
    id SERIAL PRIMARY KEY,

    -- Multi-tenancy: POIs belong to a village
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,

    -- POI type
    poi_type_id INTEGER NOT NULL REFERENCES poi_types(id),

    -- Basic info
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Location
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    address TEXT,

    -- Additional attributes (flexible JSON)
    attributes JSONB DEFAULT '{}'::jsonb,
    -- Example: {"surface_area_m2": 1500, "construction_year": 1850, "protected": true}

    -- Visibility & status
    is_public BOOLEAN DEFAULT true, -- Whether POI is visible on public map
    status VARCHAR(20) DEFAULT 'active', -- "active", "archived", "pending_review"

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by_user_id INTEGER, -- Future: link to user who created it

    -- Source information
    source VARCHAR(100), -- "manual_entry", "import", "ai_scraped", "partner_data"
    source_url TEXT
);

-- Indexes
CREATE INDEX idx_pois_village ON pois(village_id);
CREATE INDEX idx_pois_type ON pois(poi_type_id);
CREATE INDEX idx_pois_status ON pois(status);
CREATE INDEX idx_pois_public ON pois(is_public);

-- Composite index for common query pattern
CREATE INDEX idx_pois_village_type ON pois(village_id, poi_type_id);

-- Spatial index for geographic queries
CREATE INDEX idx_pois_location ON pois USING gist(
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

COMMENT ON TABLE pois IS 'Village-specific points of interest - multi-tenant with flexible attributes';
COMMENT ON COLUMN pois.village_id IS 'Links POI to owning village (multi-tenancy)';
COMMENT ON COLUMN pois.attributes IS 'Flexible JSON for POI-specific data (size, year, features, etc.)';
COMMENT ON COLUMN pois.is_public IS 'Whether POI appears on public village map';
