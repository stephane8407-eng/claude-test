-- Week 5: Authentication System Database Tables
-- Execute this script to add authentication tables to the database

-- ============================================================================
-- UPDATE users table
-- ============================================================================

-- Add new columns to existing users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user' NOT NULL,
ADD COLUMN IF NOT EXISTS village_id INTEGER REFERENCES villages(id),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL,
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_village_id ON users(village_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Migrate user_role to role column if it exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'user_role'
    ) THEN
        UPDATE users SET role = user_role WHERE role = 'user';
    END IF;
END$$;

-- ============================================================================
-- CREATE api_keys table
-- ============================================================================

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- API key details
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100),
    last_used_at TIMESTAMP,

    -- Expiration
    expires_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);

-- ============================================================================
-- CREATE password_reset_tokens table
-- ============================================================================

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Token details
    token_hash VARCHAR(255) NOT NULL UNIQUE,

    -- Status
    used BOOLEAN DEFAULT FALSE NOT NULL,
    expires_at TIMESTAMP NOT NULL,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    used_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token_hash ON password_reset_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_used ON password_reset_tokens(used);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify tables exist
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('users', 'api_keys', 'password_reset_tokens')
ORDER BY table_name;
