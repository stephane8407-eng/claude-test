-- Week 3: Identity Engine Infrastructure
-- 3 tables for identity analysis and AI-generated themes

-- ==========================================
-- Table 1: identity_categories (6 categories)
-- ==========================================

CREATE TABLE identity_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- "infrastructure", "economy", "identity", "demographics", "governance", "tourism"
    name_fr VARCHAR(50), -- French: "infrastructure", "économie", "identité", "démographie", "gouvernance", "tourisme"
    icon VARCHAR(50), -- Icon identifier: "building", "coins", "flag", "users", "landmark", "map"
    color VARCHAR(7), -- Hex color: "#3B82F6"
    description TEXT,
    example_themes TEXT, -- Examples: "Phoenix Village (infrastructure), Sleeping Waters (economy)"
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert the 6 core categories
INSERT INTO identity_categories (name, name_fr, icon, color, description, example_themes) VALUES
('infrastructure', 'Infrastructure', 'building', '#3B82F6', 'How wars shaped roads, walls, bridges, and built environment', 'Phoenix Village (rebuilt after destruction)'),
('economy', 'Économie', 'coins', '#10B981', 'How conflicts affected trade, agriculture, industry, and wealth', 'Sleeping Waters (economic decline after wars)'),
('identity', 'Identité', 'flag', '#8B5CF6', 'How history created festivals, traditions, symbols, and collective memory', 'Villages Brûlés (burned village identity)'),
('demographics', 'Démographie', 'users', '#F59E0B', 'How wars affected population, migration, family structures', 'Migration Hub (refugees settled here)'),
('governance', 'Gouvernance', 'landmark', '#EF4444', 'How conflicts shaped political structures, administration, laws', 'Border Village (governance changed with borders)'),
('tourism', 'Tourisme', 'map', '#06B6D4', 'How history can be monetized through heritage tourism today', 'Heritage Trail (tourist circuit opportunity)');

CREATE INDEX idx_identity_categories_name ON identity_categories(name);


-- ==========================================
-- Table 2: identity_themes (AI-generated village stories)
-- ==========================================

CREATE TABLE identity_themes (
    id SERIAL PRIMARY KEY,
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES identity_categories(id),

    -- Core Identity
    theme_name VARCHAR(100) NOT NULL, -- "Phoenix Village", "Sleeping Waters", etc.
    theme_name_fr VARCHAR(100),
    tagline VARCHAR(200), -- One-sentence summary
    tagline_fr VARCHAR(200),

    -- AI-Generated Content
    story_markdown TEXT NOT NULL, -- Full identity story (markdown format)
    impact_summary TEXT, -- 2-3 sentence summary of modern impact

    -- Evidence & Sources
    evidence_conflicts INTEGER[], -- Array of conflict IDs supporting this theme
    evidence_pois INTEGER[], -- Array of POI IDs supporting this theme
    evidence_data JSONB, -- Supporting data: {"population_decline": "45% since 1900", "wars_experienced": 7}

    -- Actionable Projects (Tourism Monetization)
    project_ideas JSONB, -- Array of projects: [{"title": "QR Route", "budget": "€2000", "roi": "€8000/year"}]

    -- Metadata
    confidence_score DECIMAL(3,2), -- 0.00-1.00 (how strong is the evidence?)
    is_featured BOOLEAN DEFAULT FALSE, -- Show on village homepage
    display_order INTEGER DEFAULT 0, -- Sort order on village page

    -- AI Generation Tracking
    ai_model VARCHAR(50), -- "claude-sonnet-4-20250514"
    ai_prompt_version VARCHAR(20), -- "v1.2" (for tracking prompt improvements)
    generated_at TIMESTAMP DEFAULT NOW(),
    reviewed_by_human BOOLEAN DEFAULT FALSE,
    human_edits_made BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(village_id, category_id, theme_name) -- One theme per category per village
);

CREATE INDEX idx_identity_themes_village ON identity_themes(village_id);
CREATE INDEX idx_identity_themes_category ON identity_themes(category_id);
CREATE INDEX idx_identity_themes_featured ON identity_themes(is_featured);
CREATE INDEX idx_identity_themes_conflicts ON identity_themes USING gin(evidence_conflicts);
CREATE INDEX idx_identity_themes_pois ON identity_themes USING gin(evidence_pois);

COMMENT ON TABLE identity_themes IS 'AI-generated village identity stories based on historical analysis';
COMMENT ON COLUMN identity_themes.evidence_conflicts IS 'Array of conflict IDs that support this identity theme';
COMMENT ON COLUMN identity_themes.confidence_score IS 'How strongly does evidence support this theme? 0.0 = weak, 1.0 = very strong';


-- ==========================================
-- Table 3: village_data_snapshots (pre-computed analytics)
-- ==========================================

CREATE TABLE village_data_snapshots (
    id SERIAL PRIMARY KEY,
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,

    -- Data Collection Timestamp
    snapshot_date TIMESTAMP DEFAULT NOW(),
    data_version VARCHAR(20) DEFAULT 'v1.0', -- Track schema versions

    -- Conflict Summary (Pre-computed for AI)
    total_conflicts INTEGER DEFAULT 0,
    conflicts_by_period JSONB, -- {"Medieval": 25, "WW1": 3, "WW2": 5}
    conflicts_by_type JSONB, -- {"siege": 12, "battle": 8, "raid": 5}
    most_destructive_conflicts JSONB, -- Top 5 worst conflicts with details
    conflict_density_score DECIMAL(5,2), -- Conflicts per 100 years

    -- POI Summary
    total_pois INTEGER DEFAULT 0,
    pois_by_type JSONB, -- {"church": 3, "château": 1, "pond": 15}
    heritage_buildings INTEGER DEFAULT 0, -- Count of historical buildings

    -- Demographics (Future: INSEE API)
    current_population INTEGER,
    population_peak INTEGER,
    population_peak_year INTEGER,
    population_decline_pct DECIMAL(5,2), -- Percentage decline from peak

    -- Economy (Future: INSEE API)
    primary_industry VARCHAR(100), -- "Agriculture", "Tourism", "Manufacturing"
    unemployment_rate DECIMAL(5,2),
    median_income INTEGER,

    -- Geographic Context
    distance_to_major_city INTEGER, -- km to nearest city >50k population
    border_proximity BOOLEAN DEFAULT FALSE, -- Within 20km of national border?
    strategic_location TEXT, -- "Trade route", "River crossing", "Mountain pass"

    -- Computed Scores (For AI Prompts)
    conflict_trauma_score DECIMAL(3,2), -- 0.00-1.00 (how traumatic was history?)
    resilience_score DECIMAL(3,2), -- 0.00-1.00 (how well did village recover?)
    heritage_richness_score DECIMAL(3,2), -- 0.00-1.00 (how much heritage to monetize?)
    tourism_potential_score DECIMAL(3,2), -- 0.00-1.00 (tourism opportunity?)

    -- AI Usage Tracking
    used_for_identity_generation BOOLEAN DEFAULT FALSE,
    identity_generation_timestamp TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_village_data_snapshots_village ON village_data_snapshots(village_id);
CREATE INDEX idx_village_data_snapshots_date ON village_data_snapshots(snapshot_date DESC);

COMMENT ON TABLE village_data_snapshots IS 'Pre-computed village data for efficient AI identity generation';
COMMENT ON COLUMN village_data_snapshots.conflict_density_score IS 'Number of conflicts per 100 years of village history';
COMMENT ON COLUMN village_data_snapshots.conflict_trauma_score IS 'How traumatic was the village history? Used in AI prompts';
