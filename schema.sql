-- =============================================================================
-- VAJRANET DISASTER COMMUNICATION & EMERGENCY RESPONSE DATABASE SCHEMA
-- PostgreSQL / Supabase SQL Schema (100% Idempotent & Production Ready)
-- =============================================================================

-- Enable pgcrypto / uuid-ossp for random UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- SAFE ENUM TYPES (Idempotent creation via DO blocks)
-- -----------------------------------------------------------------------------
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role_enum') THEN
        CREATE TYPE user_role_enum AS ENUM ('CITIZEN', 'VOLUNTEER', 'GOVERNMENT', 'ADMIN');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sos_severity_enum') THEN
        CREATE TYPE sos_severity_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sos_status_enum') THEN
        CREATE TYPE sos_status_enum AS ENUM ('ACTIVE', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED', 'CANCELLED');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incident_type_enum') THEN
        CREATE TYPE incident_type_enum AS ENUM (
            'FLOOD', 'EARTHQUAKE', 'FIRE', 'LANDSLIDE', 
            'ACCIDENT', 'BUILDING_COLLAPSE', 'MEDICAL', 'OTHER'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incident_severity_enum') THEN
        CREATE TYPE incident_severity_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incident_status_enum') THEN
        CREATE TYPE incident_status_enum AS ENUM ('REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'shelter_status_enum') THEN
        CREATE TYPE shelter_status_enum AS ENUM ('OPEN', 'LIMITED', 'FULL', 'CLOSED');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hospital_type_enum') THEN
        CREATE TYPE hospital_type_enum AS ENUM ('GOVERNMENT', 'PRIVATE');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'relief_center_status_enum') THEN
        CREATE TYPE relief_center_status_enum AS ENUM ('OPEN', 'LIMITED', 'CLOSED');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'announcement_type_enum') THEN
        CREATE TYPE announcement_type_enum AS ENUM (
            'ALERT', 'SAFETY_INSTRUCTION', 'EVACUATION', 
            'INCIDENT_UPDATE', 'SHELTER_INFO', 'GENERAL_UPDATE'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'announcement_priority_enum') THEN
        CREATE TYPE announcement_priority_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'volunteer_availability_enum') THEN
        CREATE TYPE volunteer_availability_enum AS ENUM ('AVAILABLE', 'BUSY', 'OFFLINE');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status_enum') THEN
        CREATE TYPE task_status_enum AS ENUM ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'fundraiser_status_enum') THEN
        CREATE TYPE fundraiser_status_enum AS ENUM ('ACTIVE', 'COMPLETED', 'PAUSED');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'offline_event_type_enum') THEN
        CREATE TYPE offline_event_type_enum AS ENUM ('SOS', 'INCIDENT', 'LOCATION');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'offline_event_status_enum') THEN
        CREATE TYPE offline_event_status_enum AS ENUM ('PROCESSED', 'DUPLICATE', 'FAILED');
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- 1. USERS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    role user_role_enum NOT NULL DEFAULT 'CITIZEN',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- -----------------------------------------------------------------------------
-- 2. SOS ALERTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sos_alerts (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    message_id VARCHAR(100) NOT NULL UNIQUE,
    citizen_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    origin_device_id VARCHAR(100),
    message TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    severity sos_severity_enum NOT NULL DEFAULT 'CRITICAL',
    status sos_status_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_sos_message_id ON sos_alerts(message_id);
CREATE INDEX IF NOT EXISTS idx_sos_status ON sos_alerts(status);
CREATE INDEX IF NOT EXISTS idx_sos_severity ON sos_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_sos_coords ON sos_alerts(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_sos_created_at ON sos_alerts(created_at DESC);

-- -----------------------------------------------------------------------------
-- 3. DISASTER INCIDENTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incidents (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    message_id VARCHAR(100) UNIQUE,
    reported_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    type incident_type_enum NOT NULL DEFAULT 'OTHER',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    severity incident_severity_enum NOT NULL DEFAULT 'MEDIUM',
    status incident_status_enum NOT NULL DEFAULT 'REPORTED',
    media_urls TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidents(type);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_coords ON incidents(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents(created_at DESC);

-- -----------------------------------------------------------------------------
-- 4. EMERGENCY SHELTERS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shelters (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    address VARCHAR(500) NOT NULL,
    capacity INT NOT NULL DEFAULT 100,
    occupied INT NOT NULL DEFAULT 0,
    status shelter_status_enum NOT NULL DEFAULT 'OPEN',
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    managed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shelters_coords ON shelters(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_shelters_status ON shelters(status);

-- -----------------------------------------------------------------------------
-- 5. HOSPITALS & EMERGENCY MEDICAL
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hospitals (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(255) NOT NULL,
    type hospital_type_enum NOT NULL DEFAULT 'GOVERNMENT',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    address VARCHAR(500) NOT NULL,
    emergency_available BOOLEAN NOT NULL DEFAULT TRUE,
    total_beds INT NOT NULL DEFAULT 50,
    available_beds INT NOT NULL DEFAULT 50,
    icu_total INT NOT NULL DEFAULT 10,
    icu_available INT NOT NULL DEFAULT 10,
    managed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hospitals_coords ON hospitals(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_hospitals_type ON hospitals(type);

-- -----------------------------------------------------------------------------
-- 6. RELIEF DISTRIBUTION CENTERS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS relief_centers (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    address VARCHAR(500) NOT NULL,
    items_available TEXT NOT NULL DEFAULT '["Food", "Water", "Medicine", "Clothing"]',
    status relief_center_status_enum NOT NULL DEFAULT 'OPEN',
    managed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_relief_centers_coords ON relief_centers(latitude, longitude);

-- -----------------------------------------------------------------------------
-- 7. OFFICIAL ANNOUNCEMENTS & BROADCASTS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS announcements (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type announcement_type_enum NOT NULL DEFAULT 'ALERT',
    area VARCHAR(255),
    priority announcement_priority_enum NOT NULL DEFAULT 'HIGH',
    created_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_announcements_priority ON announcements(priority);
CREATE INDEX IF NOT EXISTS idx_announcements_created_at ON announcements(created_at DESC);

-- -----------------------------------------------------------------------------
-- 8. VOLUNTEERS & RESPONSE TASKS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS volunteers (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    skills TEXT NOT NULL DEFAULT '[]',
    availability_status volunteer_availability_enum NOT NULL DEFAULT 'AVAILABLE',
    phone VARCHAR(50),
    location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS volunteer_tasks (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    incident_id VARCHAR(36) NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    volunteer_id VARCHAR(36) NOT NULL REFERENCES volunteers(id) ON DELETE CASCADE,
    status task_status_enum NOT NULL DEFAULT 'ACCEPTED',
    notes TEXT,
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_volunteer_tasks_incident ON volunteer_tasks(incident_id);
CREATE INDEX IF NOT EXISTS idx_volunteer_tasks_volunteer ON volunteer_tasks(volunteer_id);

-- -----------------------------------------------------------------------------
-- 9. FUNDRAISING CAMPAIGNS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fundraising_campaigns (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    target_amount DOUBLE PRECISION NOT NULL,
    raised_amount DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    beneficiary VARCHAR(255) NOT NULL,
    status fundraiser_status_enum NOT NULL DEFAULT 'ACTIVE',
    created_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 10. REGISTERED MESH DEVICES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS devices (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    device_id VARCHAR(100) NOT NULL UNIQUE,
    device_type VARCHAR(50) NOT NULL DEFAULT 'USER_PHONE',
    owner_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    battery_level INT,
    mesh_hop_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_devices_device_id ON devices(device_id);

-- -----------------------------------------------------------------------------
-- 11. OFFLINE EVENTS (IDEMPOTENT GATEWAY SYNC)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS offline_events (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    message_id VARCHAR(100) NOT NULL UNIQUE,
    gateway_id VARCHAR(100) NOT NULL,
    origin_device_id VARCHAR(100),
    event_type offline_event_type_enum NOT NULL,
    payload TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status offline_event_status_enum NOT NULL DEFAULT 'PROCESSED',
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_offline_events_message_id ON offline_events(message_id);
CREATE INDEX IF NOT EXISTS idx_offline_events_gateway ON offline_events(gateway_id);
