-- Initialize database for SentinelGuard
-- This script runs when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create indexes for performance
-- These will be created by Alembic migrations, but we add some basic ones here

-- Grant permissions to the sentinel user
GRANT ALL PRIVILEGES ON DATABASE sentinelguard TO sentinel;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sentinel;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sentinel;

-- Create initial configuration (optional - can be done via API)
-- This is commented out as it should be handled by the application

-- INSERT INTO endpoint_configs (endpoint, rate_limit, window_seconds, score_threshold, created_at, updated_at)
-- VALUES 
--   ('/api/v1/default', 100, 60, 50, NOW(), NOW()),
--   ('/api/v1/admin/', 10, 60, 30, NOW(), NOW()),
--   ('/api/v1/auth/login', 5, 300, 40, NOW(), NOW());

COMMIT;
