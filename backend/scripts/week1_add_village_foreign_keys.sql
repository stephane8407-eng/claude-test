-- Add village_id to local_conflicts (links conflicts to villages)
ALTER TABLE local_conflicts
ADD COLUMN village_id INTEGER REFERENCES villages(id);

CREATE INDEX idx_local_conflicts_village ON local_conflicts(village_id);

COMMENT ON COLUMN local_conflicts.village_id IS 'Links conflict to owning village (multi-tenancy)';

-- Add village_id to places (if you want villages to own places)
ALTER TABLE places
ADD COLUMN village_id INTEGER REFERENCES villages(id);

CREATE INDEX idx_places_village ON places(village_id);

-- Note: battles table stays global (shared across all villages)
-- Only local_conflicts are village-specific

COMMENT ON COLUMN places.village_id IS 'Optional: links place to village for filtering';
