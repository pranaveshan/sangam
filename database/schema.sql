-- SANGAM Platform Database Schema
-- PostgreSQL with PostGIS extension

-- Enable PostGIS for geographic data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create ENUM types
CREATE TYPE user_role AS ENUM ('citizen', 'government', 'university_staff', 'student', 'industry');
CREATE TYPE challenge_status AS ENUM ('submitted', 'under_review', 'validated', 'matched', 'rejected', 'duplicate');
CREATE TYPE project_status AS ENUM ('university_accepted', 'team_formed', 'industry_collaboration', 'prototype', 'testing', 'pilot', 'completed', 'cancelled');
CREATE TYPE urgency_level AS ENUM ('low', 'medium', 'high', 'critical');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role user_role NOT NULL,
    organization VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_demo_data BOOLEAN DEFAULT FALSE
);

-- Universities table
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    state VARCHAR(100),
    district VARCHAR(100),
    established_year INTEGER,
    website VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_demo_data BOOLEAN DEFAULT FALSE
);

-- University departments and expertise
CREATE TABLE university_expertise (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    department VARCHAR(255) NOT NULL,
    research_area VARCHAR(255) NOT NULL,
    faculty_count INTEGER,
    lab_facilities TEXT[],
    keywords TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Challenges table
CREATE TABLE challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    location_name VARCHAR(255) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    location GEOGRAPHY(POINT, 4326),
    photo_url VARCHAR(500),
    document_url VARCHAR(500),
    video_url VARCHAR(500),
    community_impact TEXT,
    people_affected INTEGER,
    urgency urgency_level NOT NULL,
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    status challenge_status DEFAULT 'submitted',
    submitted_by INTEGER REFERENCES users(id),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP,
    validated_by INTEGER REFERENCES users(id),
    is_demo_data BOOLEAN DEFAULT FALSE
);

-- AI Analysis table
CREATE TABLE ai_analysis (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER REFERENCES challenges(id) ON DELETE CASCADE,
    domain VARCHAR(100) NOT NULL,
    subdomain VARCHAR(100),
    confidence_score DECIMAL(3, 2),
    priority_score DECIMAL(3, 1) NOT NULL,
    people_affected_score INTEGER,
    urgency_score INTEGER,
    severity_score INTEGER,
    geographic_spread_score INTEGER,
    keywords TEXT[],
    classification_reason TEXT,
    similar_challenge_ids INTEGER[],
    recommended_action VARCHAR(100),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- University matching results
CREATE TABLE university_matches (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER REFERENCES challenges(id) ON DELETE CASCADE,
    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
    match_score DECIMAL(3, 2) NOT NULL,
    matching_departments TEXT[],
    matching_expertise TEXT[],
    matching_reason TEXT,
    rank INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER REFERENCES challenges(id),
    university_id INTEGER REFERENCES universities(id),
    project_name VARCHAR(255) NOT NULL,
    project_description TEXT,
    goal TEXT,
    status project_status DEFAULT 'university_accepted',
    accepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    is_demo_data BOOLEAN DEFAULT FALSE
);

-- Teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    team_name VARCHAR(255) NOT NULL,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team members table
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(100),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, user_id)
);

-- Faculty mentors table
CREATE TABLE faculty_mentors (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    department VARCHAR(255),
    expertise_area VARCHAR(255),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Industry partners table
CREATE TABLE industry_partners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    sector VARCHAR(100),
    website VARCHAR(255),
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    csr_focus_areas TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_demo_data BOOLEAN DEFAULT FALSE
);

-- Industry collaborations table
CREATE TABLE industry_collaborations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    partner_id INTEGER REFERENCES industry_partners(id) ON DELETE CASCADE,
    collaboration_type VARCHAR(100),
    support_description TEXT,
    resources_offered TEXT[],
    mentorship_offered BOOLEAN DEFAULT FALSE,
    funding_amount DECIMAL(12, 2),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Milestones table
CREATE TABLE milestones (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sequence_order INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    progress_percentage INTEGER DEFAULT 0,
    target_date DATE,
    completed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Community feedback table
CREATE TABLE community_feedback (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    submitted_by INTEGER REFERENCES users(id),
    rating DECIMAL(2, 1),
    feedback_text TEXT,
    problem_improvement TEXT,
    photo_evidence_url VARCHAR(500),
    deployment_confirmed BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Impact metrics table
CREATE TABLE impact_metrics (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    people_reached INTEGER DEFAULT 0,
    communities_reached INTEGER DEFAULT 0,
    districts_covered TEXT[],
    solution_adopted BOOLEAN DEFAULT FALSE,
    impact_description TEXT,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_challenges_status ON challenges(status);
CREATE INDEX idx_challenges_district ON challenges(district);
CREATE INDEX idx_challenges_submitted_at ON challenges(submitted_at DESC);
CREATE INDEX idx_challenges_location ON challenges USING GIST(location);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_university ON projects(university_id);
CREATE INDEX idx_ai_analysis_domain ON ai_analysis(domain);
CREATE INDEX idx_university_matches_challenge ON university_matches(challenge_id, match_score DESC);
