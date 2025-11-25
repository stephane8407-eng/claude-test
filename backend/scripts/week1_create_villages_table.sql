-- Create villages table for multi-tenancy
CREATE TABLE villages (
    id SERIAL PRIMARY KEY,

    -- Basic info
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(255) NOT NULL UNIQUE, -- URL-friendly: "chirac", "manot"
    description TEXT,

    -- Location
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    country VARCHAR(2) NOT NULL, -- "FR", "UK", "BE"
    department VARCHAR(100), -- "Charente", "Hertfordshire"
    region VARCHAR(100), -- "Nouvelle-Aquitaine"

    -- Village details
    population INTEGER,
    area_km2 DECIMAL(10, 2),

    -- Subscription & features
    subscription_tier VARCHAR(20) DEFAULT 'free', -- "free", "partner", "flagship"
    subscription_status VARCHAR(20) DEFAULT 'active', -- "active", "expired", "trial"
    subscription_expires_at DATE,

    -- Settings (JSONB for flexibility)
    settings JSONB DEFAULT '{
        "brand_color": "#3B82F6",
        "show_conflicts": true,
        "show_ponds": false,
        "show_routes": false,
        "public_page_enabled": false
    }'::jsonb,

    -- Identity themes (will be populated by AI later)
    identity_themes JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_villages_slug ON villages(slug);
CREATE INDEX idx_villages_country ON villages(country);
CREATE INDEX idx_villages_tier ON villages(subscription_tier);
CREATE INDEX idx_villages_status ON villages(subscription_status);

-- Spatial index for finding nearby villages
CREATE INDEX idx_villages_location ON villages USING gist(
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);

COMMENT ON TABLE villages IS 'Multi-tenant villages - each village has its own space';
COMMENT ON COLUMN villages.settings IS 'Flexible JSON settings per village';
COMMENT ON COLUMN villages.identity_themes IS 'AI-generated themes stored as JSON after analysis';
