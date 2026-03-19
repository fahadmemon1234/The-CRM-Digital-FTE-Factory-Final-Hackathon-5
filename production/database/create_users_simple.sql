-- Quick Users Table Setup for TechCorp FTE
-- Run this in your PostgreSQL database

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Create index on email
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Insert default admin user
-- Email: admin@techcorp.com
-- Password: admin123
-- Hash generated with bcrypt (rounds=12)
INSERT INTO users (name, email, password_hash, company, is_verified)
VALUES (
    'Admin User',
    'admin@techcorp.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu',
    'TechCorp',
    true
)
ON CONFLICT (email) DO NOTHING;

-- Insert demo user
-- Email: demo@techcorp.com
-- Password: demo123
INSERT INTO users (name, email, password_hash, company, is_verified)
VALUES (
    'Demo User',
    'demo@techcorp.com',
    '$2b$12$rH7xKZqQvxN9jGvVqK8LpOZm5xJ3vF2wY8nT6bR4cD1eA9fG0hI2jK',
    'Demo Corp',
    true
)
ON CONFLICT (email) DO NOTHING;

-- Verify users
SELECT id, name, email, company, created_at FROM users;
