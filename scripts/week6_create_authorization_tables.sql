-- Week 6: Authorization & Permissions Database Schema
-- Execute this script to add authorization tables

-- ============================================================================
-- CREATE roles table
-- ============================================================================

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- Insert default roles
INSERT INTO roles (name, description) VALUES
    ('admin', 'System administrator with full access to all villages and features'),
    ('village_admin', 'Village administrator with full access to their own village'),
    ('editor', 'Can edit content but cannot manage users or settings'),
    ('viewer', 'Read-only access')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- CREATE permissions table
-- ============================================================================

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name);
CREATE INDEX IF NOT EXISTS idx_permissions_category ON permissions(category);

-- Insert default permissions
INSERT INTO permissions (name, description, category) VALUES
    -- Village management
    ('can_view_any_village', 'Can view any village (system admin)', 'village'),
    ('can_edit_any_village', 'Can edit any village (system admin)', 'village'),
    ('can_edit_own_village', 'Can edit own village', 'village'),
    ('can_delete_village', 'Can delete villages', 'village'),

    -- POI management
    ('can_view_pois', 'Can view POIs', 'poi'),
    ('can_add_poi', 'Can add POIs to own village', 'poi'),
    ('can_edit_poi', 'Can edit POIs in own village', 'poi'),
    ('can_delete_poi', 'Can delete POIs from own village', 'poi'),

    -- Conflict management
    ('can_view_conflicts', 'Can view conflicts', 'conflict'),
    ('can_add_conflict', 'Can add conflicts to own village', 'conflict'),
    ('can_edit_conflict', 'Can edit conflicts in own village', 'conflict'),
    ('can_delete_conflict', 'Can delete conflicts from own village', 'conflict'),

    -- Identity management
    ('can_view_identity', 'Can view identity themes', 'identity'),
    ('can_generate_identity', 'Can generate AI identity themes', 'identity'),
    ('can_edit_identity', 'Can edit identity themes', 'identity'),
    ('can_delete_identity', 'Can delete identity themes', 'identity'),

    -- User management
    ('can_manage_users', 'Can manage all users', 'user'),
    ('can_invite_users', 'Can invite users to own village', 'user'),

    -- Analytics & Premium features
    ('can_view_analytics', 'Can view analytics', 'analytics'),
    ('can_generate_qr', 'Can generate QR codes', 'premium'),
    ('can_export_data', 'Can export data', 'premium')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- CREATE role_permissions junction table
-- ============================================================================

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);

-- Assign permissions to admin role (all permissions)
INSERT INTO role_permissions (role_id, permission_id)
SELECT
    (SELECT id FROM roles WHERE name = 'admin'),
    id
FROM permissions
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Assign permissions to village_admin role
INSERT INTO role_permissions (role_id, permission_id)
SELECT
    (SELECT id FROM roles WHERE name = 'village_admin'),
    id
FROM permissions
WHERE name IN (
    'can_edit_own_village',
    'can_view_pois',
    'can_add_poi',
    'can_edit_poi',
    'can_delete_poi',
    'can_view_conflicts',
    'can_add_conflict',
    'can_edit_conflict',
    'can_delete_conflict',
    'can_view_identity',
    'can_generate_identity',
    'can_edit_identity',
    'can_invite_users',
    'can_view_analytics'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Assign permissions to editor role
INSERT INTO role_permissions (role_id, permission_id)
SELECT
    (SELECT id FROM roles WHERE name = 'editor'),
    id
FROM permissions
WHERE name IN (
    'can_view_pois',
    'can_add_poi',
    'can_edit_poi',
    'can_view_conflicts',
    'can_add_conflict',
    'can_edit_conflict',
    'can_view_identity'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Assign permissions to viewer role
INSERT INTO role_permissions (role_id, permission_id)
SELECT
    (SELECT id FROM roles WHERE name = 'viewer'),
    id
FROM permissions
WHERE name IN (
    'can_view_pois',
    'can_view_conflicts',
    'can_view_identity'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- ============================================================================
-- UPDATE users table to use role_id
-- ============================================================================

-- Add role_id column if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS role_id INTEGER REFERENCES roles(id);

-- Migrate existing users based on their role string
UPDATE users SET role_id = (SELECT id FROM roles WHERE name = 'admin') WHERE role = 'admin';
UPDATE users SET role_id = (SELECT id FROM roles WHERE name = 'village_admin') WHERE role = 'village_admin';
UPDATE users SET role_id = (SELECT id FROM roles WHERE name = 'viewer') WHERE role = 'user';
UPDATE users SET role_id = (SELECT id FROM roles WHERE name = 'viewer') WHERE role_id IS NULL;

-- Add NOT NULL constraint after migration
ALTER TABLE users ALTER COLUMN role_id SET NOT NULL;

-- Create index on role_id
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);

-- ============================================================================
-- ADD subscription_tier to villages table
-- ============================================================================

ALTER TABLE villages ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';

-- Possible values: 'free', 'partner', 'enterprise'
CREATE INDEX IF NOT EXISTS idx_villages_subscription_tier ON villages(subscription_tier);

-- Set existing villages to free tier
UPDATE villages SET subscription_tier = 'free' WHERE subscription_tier IS NULL;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify tables exist
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('roles', 'permissions', 'role_permissions')
ORDER BY table_name;

-- Show roles and permission counts
SELECT
    r.name as role,
    r.description,
    COUNT(rp.permission_id) as permission_count
FROM roles r
LEFT JOIN role_permissions rp ON r.id = rp.role_id
GROUP BY r.id, r.name, r.description
ORDER BY r.name;

-- Show all permissions
SELECT category, COUNT(*) as permission_count
FROM permissions
GROUP BY category
ORDER BY category;
