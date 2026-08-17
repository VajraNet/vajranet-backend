# 🗄️ VajraNet — Shared Data Models & Database Architecture

## 1. Database Specifications
* **Engine:** PostgreSQL 15+ (Supabase) in production / SQLite in local development.
* **ORM:** SQLAlchemy 2.0 Declarative with Type Annotations.
* **UUID Strategy:** Primary keys use UUID4 strings (`VARCHAR(36)`).
* **Timestamps:** UTC timezone-aware datetimes with automatic indexing.

---

## 2. Shared Table Definitions

### 2.1 `users`
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    role user_role_enum NOT NULL DEFAULT 'CITIZEN',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 2.2 `sos_alerts`
```sql
CREATE TABLE sos_alerts (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    message_id VARCHAR(100) NOT NULL UNIQUE,
    citizen_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    origin_device_id VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    severity sos_severity_enum NOT NULL DEFAULT 'CRITICAL',
    status sos_status_enum NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);
```

### 2.3 `incidents`
```sql
CREATE TABLE incidents (
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
```

### 2.4 `shelters`
```sql
CREATE TABLE shelters (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 100,
    occupied INTEGER NOT NULL DEFAULT 0,
    status shelter_status_enum NOT NULL DEFAULT 'OPEN',
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    managed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 2.5 `hospitals`
```sql
CREATE TABLE hospitals (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(255) NOT NULL,
    type hospital_type_enum NOT NULL DEFAULT 'GOVERNMENT',
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    total_beds INTEGER NOT NULL DEFAULT 0,
    available_beds INTEGER NOT NULL DEFAULT 0,
    icu_beds_total INTEGER NOT NULL DEFAULT 0,
    icu_beds_available INTEGER NOT NULL DEFAULT 0,
    emergency_available BOOLEAN NOT NULL DEFAULT TRUE,
    managed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 2.6 `relief_centers`
```sql
CREATE TABLE relief_centers (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    status relief_center_status_enum NOT NULL DEFAULT 'OPEN',
    items_available TEXT NOT NULL DEFAULT '["Food", "Water", "Medicine", "Clothing"]',
    managed_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 2.7 `announcements`
```sql
CREATE TABLE announcements (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type announcement_type_enum NOT NULL DEFAULT 'ALERT',
    priority announcement_priority_enum NOT NULL DEFAULT 'HIGH',
    area VARCHAR(255) NOT NULL DEFAULT 'All Areas',
    created_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 2.8 `devices` & `offline_events`
```sql
CREATE TABLE devices (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    device_id VARCHAR(100) NOT NULL UNIQUE,
    device_type VARCHAR(50) NOT NULL DEFAULT 'USER_PHONE',
    owner_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    battery_level INT,
    mesh_hop_count INT NOT NULL DEFAULT 0,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE offline_events (
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
```

### 2.9 `trusted_devices` & `emergency_contacts`
```sql
CREATE TABLE trusted_devices (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'GOVERNMENT',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE emergency_contacts (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    relation VARCHAR(50) NOT NULL DEFAULT 'Other',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```
