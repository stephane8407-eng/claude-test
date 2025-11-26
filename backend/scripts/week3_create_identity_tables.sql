-- Week 3: Identity Engine Infrastructure
-- Create tables for identity categories, themes, and village data snapshots

-- 1. Identity Categories (6 impact categories from Week 1 conflict framework)
CREATE TABLE identity_categories (
    id SERIAL PRIMARY KEY,

    -- Category definition
    name VARCHAR(50) NOT NULL UNIQUE, -- "infrastructure", "economy", "identity", "demographics", "governance", "tourism"
    display_name VARCHAR(100) NOT NULL,
    description TEXT,

    -- Display settings
    icon VARCHAR(50),
    color VARCHAR(7) DEFAULT '#3B82F6',
    sort_order INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_identity_categories_sort ON identity_categories(sort_order);

COMMENT ON TABLE identity_categories IS 'Impact categories for analyzing village identity from conflicts and POIs';

-- Insert the 6 categories
INSERT INTO identity_categories (name, display_name, description, icon, color, sort_order) VALUES
('infrastructure', 'Infrastructure', 'Physical traces: ruins, roads, fortifications, monuments', 'building', '#10B981', 1),
('economy', 'Economy', 'Economic impact: trade routes, markets, industries, resources', 'currency', '#F59E0B', 2),
('identity', 'Identity', 'Cultural identity: heroes, myths, traditions, collective memory', 'star', '#DC2626', 3),
('demographics', 'Demographics', 'Population impact: migrations, casualties, settlement patterns', 'users', '#8B5CF6', 4),
('governance', 'Governance', 'Political legacy: borders, institutions, laws, power structures', 'shield', '#3B82F6', 5),
('tourism', 'Tourism', 'Tourism potential: memorials, museums, heritage sites, stories', 'map', '#06B6D4', 6);


-- 2. Identity Themes (AI-generated village stories)
CREATE TABLE identity_themes (
    id SERIAL PRIMARY KEY,

    -- Links to village
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,

    -- Theme content (AI-generated)
    title VARCHAR(255) NOT NULL,
    tagline VARCHAR(500),
    description TEXT,

    -- Narrative elements
    story_arc TEXT, -- The village's historical journey
    key_moments JSONB, -- [{year, event, significance}, ...]
    recurring_themes TEXT[], -- ["resilience", "transformation", "crossroads"]

    -- Personality traits
    village_personality JSONB, -- {traits: ["resilient", "proud"], voice_tone: "stoic"}

    -- Projects and opportunities (linked to categories)
    project_opportunities JSONB, -- [{category: "tourism", project: "Memorial trail", partners: ["DRAC"]}]

    -- AI generation metadata
    generated_by VARCHAR(50), -- "claude-3-5-sonnet", "gpt-4"
    generation_prompt TEXT,
    generation_cost_usd DECIMAL(10, 4),

    -- Versioning
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    replaced_by_id INTEGER REFERENCES identity_themes(id),

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_identity_themes_village ON identity_themes(village_id);
CREATE INDEX idx_identity_themes_active ON identity_themes(is_active);
CREATE INDEX idx_identity_themes_version ON identity_themes(village_id, version);

COMMENT ON TABLE identity_themes IS 'AI-generated identity themes and narratives for villages';
COMMENT ON COLUMN identity_themes.key_moments IS 'Timeline of defining moments in village history';
COMMENT ON COLUMN identity_themes.project_opportunities IS 'AI-suggested projects by category with potential partners';


-- 3. Village Data Snapshots (pre-computed analytics)
CREATE TABLE village_data_snapshots (
    id SERIAL PRIMARY KEY,

    -- Links to village
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,

    -- Snapshot metadata
    snapshot_date TIMESTAMP NOT NULL DEFAULT NOW(),
    snapshot_type VARCHAR(50) DEFAULT 'full', -- "full", "conflicts_only", "pois_only"

    -- Data counts
    total_conflicts INTEGER DEFAULT 0,
    total_pois INTEGER DEFAULT 0,
    total_battles INTEGER DEFAULT 0, -- Global battles near village

    -- Conflicts by period
    conflicts_by_period JSONB, -- {ancient: 5, medieval: 20, ww1: 15, ww2: 83}
    conflicts_by_type JSONB, -- {battle: 10, siege: 5, skirmish: 104}

    -- POIs by type
    pois_by_type JSONB, -- {pond: 15, church: 3, château: 1}
    pois_by_category JSONB, -- {water: 15, religious: 3, heritage: 1}

    -- Computed scores (0-100)
    trauma_score INTEGER, -- How much suffering (conflicts, casualties)
    resilience_score INTEGER, -- Recovery and continuity (POIs, reconstruction)
    heritage_score INTEGER, -- Cultural richness (monuments, traditions)
    tourism_potential_score INTEGER, -- Visitability (sites, stories, accessibility)

    -- Impact Today by category (from conflicts)
    impact_today JSONB, -- {infrastructure: {...}, economy: {...}, etc.}

    -- Geographic data
    bbox JSONB, -- Bounding box of all village data
    centroid_lat DECIMAL(10, 7),
    centroid_lon DECIMAL(10, 7),

    -- Computation metadata
    computation_time_ms INTEGER,
    data_quality_score INTEGER, -- 0-100: completeness and accuracy

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_village_data_snapshots_village ON village_data_snapshots(village_id);
CREATE INDEX idx_village_data_snapshots_date ON village_data_snapshots(snapshot_date DESC);
CREATE INDEX idx_village_data_snapshots_type ON village_data_snapshots(snapshot_type);

-- Index for finding latest snapshot
CREATE INDEX idx_village_data_snapshots_latest ON village_data_snapshots(village_id, snapshot_date DESC);

COMMENT ON TABLE village_data_snapshots IS 'Pre-computed analytics snapshots for villages';
COMMENT ON COLUMN village_data_snapshots.trauma_score IS 'Computed from conflicts: casualties, destruction, suffering (0-100)';
COMMENT ON COLUMN village_data_snapshots.resilience_score IS 'Computed from POIs and reconstruction: recovery capacity (0-100)';
COMMENT ON COLUMN village_data_snapshots.heritage_score IS 'Computed from POIs and sites: cultural richness (0-100)';
COMMENT ON COLUMN village_data_snapshots.tourism_potential_score IS 'Computed from sites and stories: visitability (0-100)';
