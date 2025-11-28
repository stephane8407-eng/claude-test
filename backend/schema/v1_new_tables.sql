-- V1 Product Spec: New Tables Migration
-- Creates: topics, sponsors, sponsor_slots, projects
-- Date: November 28, 2024

-- ==========================================
-- Table 1: topics (SEO Landing Pages)
-- ==========================================

CREATE TABLE IF NOT EXISTS topics (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    short_description TEXT,
    long_description TEXT,              -- 300-800 words for SEO
    hero_image_url VARCHAR(500),
    tags TEXT[],                        -- For auto-association with entities
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_topics_slug ON topics(slug);
CREATE INDEX idx_topics_tags ON topics USING gin(tags);

COMMENT ON TABLE topics IS 'Theme-based SEO landing pages for tourism discovery';
COMMENT ON COLUMN topics.tags IS 'Tags used to auto-associate villages, routes, and places with this topic';
COMMENT ON COLUMN topics.long_description IS 'SEO-optimized content, 300-800 words recommended';


-- ==========================================
-- Table 2: sponsors (Partners and Advertisers)
-- ==========================================

CREATE TABLE IF NOT EXISTS sponsors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    short_description TEXT,
    type VARCHAR(50) NOT NULL,          -- 'local_business', 'regional_partner', 'founding_partner'
    sector VARCHAR(100),                -- 'real_estate', 'bank', 'tourism', 'eco', etc.
    regions TEXT[],                     -- Administrative regions or free tags
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sponsors_slug ON sponsors(slug);
CREATE INDEX idx_sponsors_type ON sponsors(type);
CREATE INDEX idx_sponsors_sector ON sponsors(sector);
CREATE INDEX idx_sponsors_regions ON sponsors USING gin(regions);
CREATE INDEX idx_sponsors_active ON sponsors(is_active);

COMMENT ON TABLE sponsors IS 'Partners and advertisers supporting the platform';
COMMENT ON COLUMN sponsors.type IS 'Sponsor tier: local_business, regional_partner, or founding_partner';
COMMENT ON COLUMN sponsors.sector IS 'Business sector for filtering and matching';


-- ==========================================
-- Table 3: sponsor_slots (Links Sponsors to Objects)
-- ==========================================

CREATE TABLE IF NOT EXISTS sponsor_slots (
    id SERIAL PRIMARY KEY,
    sponsor_id INTEGER NOT NULL REFERENCES sponsors(id) ON DELETE CASCADE,
    object_type VARCHAR(50) NOT NULL,   -- 'settlement', 'route', 'topic'
    object_id INTEGER NOT NULL,
    position VARCHAR(20) DEFAULT 'primary',  -- 'primary', 'secondary'
    start_date DATE,
    end_date DATE,
    impression_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sponsor_slots_sponsor ON sponsor_slots(sponsor_id);
CREATE INDEX idx_sponsor_slots_object ON sponsor_slots(object_type, object_id);
CREATE INDEX idx_sponsor_slots_dates ON sponsor_slots(start_date, end_date);
CREATE INDEX idx_sponsor_slots_active ON sponsor_slots(is_active);

COMMENT ON TABLE sponsor_slots IS 'Links sponsors to villages, routes, or topics with analytics';
COMMENT ON COLUMN sponsor_slots.object_type IS 'Type of object being sponsored: settlement, route, or topic';
COMMENT ON COLUMN sponsor_slots.position IS 'Display position: primary (featured) or secondary';
COMMENT ON COLUMN sponsor_slots.impression_count IS 'Number of times this sponsor slot was displayed';
COMMENT ON COLUMN sponsor_slots.click_count IS 'Number of clicks on sponsor link';


-- ==========================================
-- Table 4: projects (AI-Suggested Initiatives)
-- ==========================================

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    settlement_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    short_description TEXT,
    status VARCHAR(50) DEFAULT 'idea',  -- 'idea', 'planned', 'in_progress', 'completed'
    themes TEXT[],
    source VARCHAR(50) DEFAULT 'manual', -- 'ai_suggested', 'manual'
    priority INTEGER DEFAULT 0,         -- For ordering (higher = more important)
    estimated_budget VARCHAR(100),      -- e.g., "€2,000-5,000"
    estimated_roi VARCHAR(100),         -- e.g., "€8,000/year"
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_settlement ON projects(settlement_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_source ON projects(source);
CREATE INDEX idx_projects_themes ON projects USING gin(themes);

COMMENT ON TABLE projects IS 'AI-suggested and manually created village development initiatives';
COMMENT ON COLUMN projects.source IS 'Origin of project: ai_suggested (from identity engine) or manual';
COMMENT ON COLUMN projects.status IS 'Project lifecycle: idea, planned, in_progress, completed';


-- ==========================================
-- Add update triggers for updated_at columns
-- ==========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Topics trigger
DROP TRIGGER IF EXISTS update_topics_updated_at ON topics;
CREATE TRIGGER update_topics_updated_at
    BEFORE UPDATE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Sponsors trigger
DROP TRIGGER IF EXISTS update_sponsors_updated_at ON sponsors;
CREATE TRIGGER update_sponsors_updated_at
    BEFORE UPDATE ON sponsors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Sponsor slots trigger
DROP TRIGGER IF EXISTS update_sponsor_slots_updated_at ON sponsor_slots;
CREATE TRIGGER update_sponsor_slots_updated_at
    BEFORE UPDATE ON sponsor_slots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Projects trigger
DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
