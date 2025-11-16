-- Supabase PostgreSQL Database Schema for ScholarSphere
-- Run this in Supabase SQL Editor to create all tables

-- Enable UUID extension (if needed)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    student_id VARCHAR(8) UNIQUE,
    birthday DATE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'provider', 'admin')),
    profile_picture VARCHAR(255),
    year_level VARCHAR(20),
    course VARCHAR(50),
    organization VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Awards table
CREATE TABLE IF NOT EXISTS awards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    award_type VARCHAR(100) NOT NULL,
    award_title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    academic_year VARCHAR(20),
    award_date DATE,
    upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Credentials table
CREATE TABLE IF NOT EXISTS credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    credential_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    status VARCHAR(20) DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'pending_review', 'approved', 'rejected')),
    upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Scholarships table
CREATE TABLE IF NOT EXISTS scholarships (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    provider_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'active', 'closed')),
    deadline DATE,
    amount VARCHAR(100),
    requirements TEXT,
    applications_count INTEGER NOT NULL DEFAULT 0,
    pending_count INTEGER NOT NULL DEFAULT 0,
    approved_count INTEGER NOT NULL DEFAULT 0,
    disapproved_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Scholarship Applications table
CREATE TABLE IF NOT EXISTS scholarship_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scholarship_id INTEGER NOT NULL REFERENCES scholarships(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'withdrawn')),
    application_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(user_id, scholarship_id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Schedule table
CREATE TABLE IF NOT EXISTS schedule (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES scholarship_applications(id) ON DELETE CASCADE,
    provider_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    schedule_date DATE,
    schedule_time VARCHAR(10),
    location VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Application Remarks table
CREATE TABLE IF NOT EXISTS application_remarks (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES scholarship_applications(id) ON DELETE CASCADE,
    provider_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    remark_text TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'review' CHECK (status IN ('review', 'approved', 'rejected')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Scholarship Application Files table
CREATE TABLE IF NOT EXISTS scholarship_application_files (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES scholarship_applications(id) ON DELETE CASCADE,
    credential_id INTEGER NOT NULL REFERENCES credentials(id) ON DELETE CASCADE,
    requirement_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(application_id, credential_id, requirement_type)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_student_id ON users(student_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_awards_user_id ON awards(user_id);
CREATE INDEX IF NOT EXISTS idx_credentials_user_id ON credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_scholarships_provider_id ON scholarships(provider_id);
CREATE INDEX IF NOT EXISTS idx_scholarships_status ON scholarships(status);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON scholarship_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_scholarship_id ON scholarship_applications(scholarship_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON scholarship_applications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_user_id ON schedule(user_id);
CREATE INDEX IF NOT EXISTS idx_schedule_provider_id ON schedule(provider_id);
CREATE INDEX IF NOT EXISTS idx_remarks_app_id ON application_remarks(application_id);
CREATE INDEX IF NOT EXISTS idx_remarks_provider_id ON application_remarks(provider_id);
CREATE INDEX IF NOT EXISTS idx_application_files_app_id ON scholarship_application_files(application_id);
CREATE INDEX IF NOT EXISTS idx_application_files_cred_id ON scholarship_application_files(credential_id);
CREATE INDEX IF NOT EXISTS idx_application_files_req_type ON scholarship_application_files(requirement_type);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'All tables and indexes created successfully!';
END $$;

