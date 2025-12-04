-- ============================================
-- SPV TREASURE MAP - PHASE E WEEK 1 MIGRATION
-- ============================================
-- Purpose: Project Management Dashboard (Kanban)
-- Date: December 4, 2025
-- Adds: project_instances, grant_applications, village_media
-- Note: Adapted to work with existing schema (villages table, etc.)
-- ============================================

-- ============================================
-- PROJECT INSTANCES (Kanban-style project tracking)
-- ============================================
-- This table tracks execution of projects (from village_identities.selected_projects)
-- using a 5-stage Kanban workflow: exploring → planning → in_progress → completed → abandoned

CREATE TABLE IF NOT EXISTS project_instances (
    id SERIAL PRIMARY KEY,
    village_id INTEGER REFERENCES villages(id) ON DELETE CASCADE,
    identity_id INTEGER REFERENCES village_identities(id) ON DELETE SET NULL,

    -- Project data (from generated identity or custom)
    project_data JSONB NOT NULL,
    -- Contains: {title, description, tier, budget_min, budget_max, timeline_months,
    --            difficulty, funding_sources[], inspired_by, first_steps[], case_study}

    -- Execution tracking
    status VARCHAR(20) DEFAULT 'exploring',
    -- Status values: 'exploring', 'planning', 'in_progress', 'completed', 'abandoned'

    priority INTEGER CHECK (priority BETWEEN 1 AND 5) DEFAULT 3,

    -- Project details
    notes TEXT, -- Mayor's notes about the project
    budget_estimated_min INTEGER, -- Euros
    budget_estimated_max INTEGER, -- Euros
    budget_actual INTEGER, -- Actual spent (updated during execution)

    timeline_months INTEGER, -- Expected duration
    timeline_actual_months INTEGER, -- Actual duration (after completion)

    -- Progress tracking
    completed_steps TEXT[], -- Array of completed step descriptions
    next_steps TEXT[], -- Array of upcoming step descriptions

    -- Attachments
    attachments JSONB DEFAULT '[]'::jsonb,
    -- Array of: {filename, url, mime_type, size, uploaded_at, uploaded_by}

    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    abandoned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_instances_village ON project_instances(village_id);
CREATE INDEX IF NOT EXISTS idx_project_instances_identity ON project_instances(identity_id);
CREATE INDEX IF NOT EXISTS idx_project_instances_status ON project_instances(status);
CREATE INDEX IF NOT EXISTS idx_project_instances_priority ON project_instances(priority);

COMMENT ON TABLE project_instances IS 'Phase E: Track execution of village projects (Kanban-style)';
COMMENT ON COLUMN project_instances.status IS 'exploring → planning → in_progress → completed/abandoned';
COMMENT ON COLUMN project_instances.project_data IS 'Full project details from generation or custom input';
COMMENT ON COLUMN project_instances.priority IS '1 (lowest) to 5 (highest)';

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_project_instances_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS project_instances_updated_at ON project_instances;
CREATE TRIGGER project_instances_updated_at
    BEFORE UPDATE ON project_instances
    FOR EACH ROW
    EXECUTE FUNCTION update_project_instances_updated_at();

-- ============================================
-- GRANT APPLICATIONS (Track grant submissions)
-- ============================================

CREATE TABLE IF NOT EXISTS grant_applications (
    id SERIAL PRIMARY KEY,
    project_instance_id INTEGER REFERENCES project_instances(id) ON DELETE CASCADE,
    funding_program_id INTEGER REFERENCES funding_programs(id) ON DELETE SET NULL,

    -- Application status
    status VARCHAR(50) DEFAULT 'draft',
    -- Status values: 'draft', 'submitted', 'under_review', 'approved', 'rejected', 'abandoned'

    -- Generated content (from Claude API)
    generated_content TEXT, -- Full application text

    -- Submission details
    amount_requested INTEGER, -- Euros
    amount_approved INTEGER, -- Euros (if approved)

    submitted_date DATE,
    decision_date DATE,
    decision_notes TEXT,

    -- Documents
    documents JSONB DEFAULT '[]'::jsonb,
    -- Array of: {filename, url, mime_type, size, uploaded_at, doc_type}

    -- Notes
    notes TEXT, -- Internal notes about the application

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_grant_applications_project ON grant_applications(project_instance_id);
CREATE INDEX IF NOT EXISTS idx_grant_applications_program ON grant_applications(funding_program_id);
CREATE INDEX IF NOT EXISTS idx_grant_applications_status ON grant_applications(status);
CREATE INDEX IF NOT EXISTS idx_grant_applications_submitted ON grant_applications(submitted_date);

COMMENT ON TABLE grant_applications IS 'Phase E: Track grant applications for project instances';
COMMENT ON COLUMN grant_applications.generated_content IS 'AI-generated application text (pre-populated)';
COMMENT ON COLUMN grant_applications.status IS 'draft → submitted → under_review → approved/rejected';

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_grant_applications_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS grant_applications_updated_at ON grant_applications;
CREATE TRIGGER grant_applications_updated_at
    BEFORE UPDATE ON grant_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_grant_applications_updated_at();

-- ============================================
-- VILLAGE MEDIA (Photos, videos, documents)
-- ============================================

CREATE TABLE IF NOT EXISTS village_media (
    id SERIAL PRIMARY KEY,
    village_id INTEGER REFERENCES villages(id) ON DELETE CASCADE,

    -- Media type
    media_type VARCHAR(20) NOT NULL, -- 'photo', 'video', 'document'
    category VARCHAR(50), -- 'heritage', 'nature', 'community', 'economy', 'events'

    -- File details
    url VARCHAR(500) NOT NULL, -- S3 or local path
    thumbnail_url VARCHAR(500), -- For photos/videos
    filename VARCHAR(255),
    file_size INTEGER, -- Bytes
    mime_type VARCHAR(100),

    -- Metadata
    caption TEXT,
    alt_text VARCHAR(255), -- For accessibility

    -- AUTOMATIC GEOLOCATION FROM EXIF
    latitude DECIMAL(10, 7), -- Extracted from GPS EXIF data
    longitude DECIMAL(10, 7),
    photo_taken_at TIMESTAMP, -- From EXIF DateTimeOriginal

    -- Display settings
    is_hero BOOLEAN DEFAULT FALSE, -- Hero image for village page
    display_order INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,

    -- Audit
    uploaded_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_village_media_village ON village_media(village_id);
CREATE INDEX IF NOT EXISTS idx_village_media_type ON village_media(media_type);
CREATE INDEX IF NOT EXISTS idx_village_media_category ON village_media(category);
CREATE INDEX IF NOT EXISTS idx_village_media_published ON village_media(is_published);

COMMENT ON TABLE village_media IS 'Phase E: Photos, videos, documents uploaded by village admins';
COMMENT ON COLUMN village_media.latitude IS 'Auto-extracted from photo EXIF GPS data';
COMMENT ON COLUMN village_media.photo_taken_at IS 'When photo was taken (from EXIF), not upload date';

-- ============================================
-- UPDATE schema_version
-- ============================================

INSERT INTO schema_version (version, description)
VALUES (3, 'Phase E Week 1: Project Instances (Kanban), Grant Applications, Village Media')
ON CONFLICT DO NOTHING;

-- ============================================
-- END OF PHASE E WEEK 1 MIGRATION
-- ============================================
