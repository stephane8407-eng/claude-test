-- Village Identities Table
-- Stores AI-generated identity summaries, themes, and projects for villages
-- Created: Phase D - Identity Save & Publish

CREATE TABLE IF NOT EXISTS village_identities (
    id SERIAL PRIMARY KEY,
    village_id INTEGER NOT NULL REFERENCES villages(id) ON DELETE CASCADE,

    -- Identity text content
    identity_summary TEXT NOT NULL,
    identity_narrative TEXT NOT NULL,
    live_here_summary TEXT NOT NULL,

    -- Selected themes (array of theme objects)
    -- Each theme: { theme_name, confidence_score, theme_story, project_ideas }
    selected_themes JSONB NOT NULL DEFAULT '[]',

    -- Selected projects (array of project objects)
    -- Each project: { title, short_description, themes, status, source }
    selected_projects JSONB NOT NULL DEFAULT '[]',

    -- Publication status
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Only one active identity per village
    CONSTRAINT one_identity_per_village UNIQUE (village_id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_village_identities_village_id ON village_identities(village_id);
CREATE INDEX IF NOT EXISTS idx_village_identities_published ON village_identities(is_published);

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE village_identities TO spv_admin;
GRANT USAGE, SELECT ON SEQUENCE village_identities_id_seq TO spv_admin;

-- Create updated_at trigger function (if not exists)
CREATE OR REPLACE FUNCTION update_village_identities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for auto-updating updated_at
DROP TRIGGER IF EXISTS village_identities_updated_at ON village_identities;
CREATE TRIGGER village_identities_updated_at
    BEFORE UPDATE ON village_identities
    FOR EACH ROW
    EXECUTE FUNCTION update_village_identities_updated_at();

-- Also update the villages table with identity fields if not present
-- (These may already exist, so we use IF NOT EXISTS pattern)
DO $$
BEGIN
    -- Add summary_identity if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'villages' AND column_name = 'summary_identity'
    ) THEN
        ALTER TABLE villages ADD COLUMN summary_identity TEXT;
    END IF;

    -- Add long_identity if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'villages' AND column_name = 'long_identity'
    ) THEN
        ALTER TABLE villages ADD COLUMN long_identity TEXT;
    END IF;

    -- Add live_here_summary if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'villages' AND column_name = 'live_here_summary'
    ) THEN
        ALTER TABLE villages ADD COLUMN live_here_summary TEXT;
    END IF;
END $$;
