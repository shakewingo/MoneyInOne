-- Initialize MoneyInOne database
-- This script runs when the PostgreSQL container first starts

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database user if not exists (handled by POSTGRES_USER env var)
-- Database and user are created automatically by the postgres image

-- Set timezone
SET timezone = 'UTC';

-- Create initial schema placeholder (tables will be created by Alembic migrations)
-- This file ensures the database is properly initialized
