-- Create poi_types table for flexible POI categories
CREATE TABLE poi_types (
    id SERIAL PRIMARY KEY,

    -- Basic info
    name VARCHAR(100) NOT NULL UNIQUE, -- "pond", "church", "château", "mill", etc.
    name_plural VARCHAR(100), -- "ponds", "churches", "châteaux"
    category VARCHAR(50) NOT NULL, -- "water", "religious", "heritage", "nature", "infrastructure"

    -- Display settings
    icon VARCHAR(50), -- Icon identifier for map display
    color VARCHAR(7) DEFAULT '#3B82F6', -- Hex color for map markers

    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_poi_types_category ON poi_types(category);

COMMENT ON TABLE poi_types IS 'POI type definitions - shared across all villages';
COMMENT ON COLUMN poi_types.category IS 'Broad category for filtering (water, religious, heritage, etc.)';
COMMENT ON COLUMN poi_types.icon IS 'Icon identifier for frontend display';
