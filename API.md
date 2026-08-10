# VAJRANET REST API Integration Contract

This document is the single source of truth for the **VajraNet** frontend team.

---

## 1. Base Configuration & Authentication

### Base URL
- **Local Development**: `http://localhost:8000/api/v1`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **Health Check**: `http://localhost:8000/health`

### Authentication
Send the Supabase JWT token in the `Authorization` header for protected endpoints:
```http
Authorization: Bearer <SUPABASE_JWT_TOKEN>
```

In local development / mock mode, you can test specific roles directly using test tokens:
- Citizen: `Bearer mock-citizen-token`
- Volunteer: `Bearer mock-volunteer-token`
- Government: `Bearer mock-government-token`
- Admin: `Bearer mock-admin-token`

---

## 2. Standard API Envelopes

### Success Envelope
All successful 2xx responses return:
```json
{
  "success": true,
  "data": { ... },
  "message": "Human-readable confirmation message"
}
```

### Error Envelope
All 4xx/5xx responses return:
```json
{
  "success": false,
  "data": null,
  "message": "Detailed explanation of the error"
}
```

---

## 3. User Roles & Permissions (RBAC)

| Role | Permissions & Responsibilities |
| :--- | :--- |
| **CITIZEN** | Create & track own SOS, report incidents, search nearby shelters/hospitals/relief centers, view emergency announcements, AI assistant. |
| **VOLUNTEER** | All citizen permissions + view open incidents, claim response tasks, update task progress, register private shelters & hospitals, manage relief fundraisers. |
| **GOVERNMENT** | Master disaster authority. Triage & resolve SOS alerts, verify and update incidents, publish emergency announcements, manage official shelters, hospitals, bed counts & relief centers. |
| **ADMIN** | Unrestricted system-wide management. |

---

## 4. Endpoints Quick Reference

| Module | Method | Endpoint | Auth | Role | Summary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth** | `GET` | `/auth/me` | Required | Any | Get user profile & role |
| **Auth** | `PATCH` | `/auth/me` | Required | Any | Update profile details |
| **Citizen** | `GET` | `/citizen/overview` | Required | CITIZEN+ | Citizen dashboard overview |
| **SOS** | `POST` | `/sos` | Optional | Any | Trigger SOS emergency alert |
| **SOS** | `GET` | `/sos/my` | Required | CITIZEN+ | View user's own SOS history |
| **SOS** | `GET` | `/sos/{id}` | Optional | Owner/Gov | Get SOS details |
| **Incidents** | `POST` | `/incidents` | Optional | Any | Report a disaster incident |
| **Incidents** | `GET` | `/incidents/my` | Required | Any | View reported incidents |
| **Incidents** | `GET` | `/incidents/{id}` | None | Public | Get incident details |
| **Shelters** | `GET` | `/shelters/nearby` | None | Public | Find nearby shelters sorted by distance |
| **Shelters** | `GET` | `/shelters/{id}` | None | Public | Get shelter capacity & details |
| **Hospitals** | `GET` | `/hospitals/nearby` | None | Public | Find hospitals & live bed counts |
| **Hospitals** | `GET` | `/hospitals/{id}` | None | Public | Get hospital details |
| **Relief** | `GET` | `/relief-centers/nearby`| None | Public | Find relief supply centers |
| **Relief** | `GET` | `/relief-centers/{id}` | None | Public | Get relief center details |
| **Announce** | `GET` | `/announcements` | None | Public | Get active emergency broadcasts |
| **Gov SOS** | `GET` | `/government/sos` | Required | GOVERNMENT | List all incoming SOS alerts |
| **Gov SOS** | `PATCH` | `/government/sos/{id}` | Required | GOVERNMENT | Update SOS status/severity |
| **Gov Inc** | `GET` | `/government/incidents`| Required | GOVERNMENT | List all disaster incidents |
| **Gov Inc** | `PATCH` | `/government/incidents/{id}`| Required| GOVERNMENT | Update incident status/severity |
| **Gov Ann** | `POST` | `/government/announcements`| Required | GOVERNMENT | Publish official broadcast |
| **Gov Ann** | `PATCH` | `/government/announcements/{id}`| Required| GOVERNMENT| Update announcement |
| **Gov Shelter**| `POST` | `/government/shelters` | Required | GOVERNMENT | Create official shelter |
| **Gov Shelter**| `PATCH`| `/government/shelters/{id}`| Required| GOVERNMENT| Update shelter capacity |
| **Gov Hosp** | `POST` | `/government/hospitals`| Required | GOVERNMENT | Register hospital |
| **Gov Hosp** | `PATCH`| `/government/hospitals/{id}`| Required| GOVERNMENT| Update bed/ICU counts |
| **Gov Relief**| `POST` | `/government/relief-centers`| Required| GOVERNMENT| Create relief center |
| **Gov Relief**| `PATCH`| `/government/relief-centers/{id}`| Required| GOVERNMENT| Update relief center |
| **Gov Dash** | `GET` | `/government/overview` | Required | GOVERNMENT | Master emergency dashboard |
| **Vol Profile**| `POST`| `/volunteers/profile` | Required | VOLUNTEER | Register volunteer profile |
| **Vol Profile**| `GET` | `/volunteers/profile` | Required | VOLUNTEER | View volunteer profile |
| **Vol Profile**| `PATCH`| `/volunteers/profile` | Required | VOLUNTEER | Update volunteer skills |
| **Vol Tasks**| `GET` | `/volunteers/incidents`| Required | VOLUNTEER | View claimable incidents |
| **Vol Tasks**| `POST`| `/volunteers/incidents/{id}/accept`| Required| VOLUNTEER| Claim response task |
| **Vol Tasks**| `PATCH`| `/volunteers/incidents/{id}/status`| Required| VOLUNTEER| Update task status |
| **Vol Shelter**| `POST`| `/volunteers/shelters` | Required | VOLUNTEER | Register private shelter |
| **Vol Hosp** | `POST` | `/volunteers/hospitals`| Required | VOLUNTEER | Register private hospital |
| **Vol Fund** | `POST` | `/volunteers/fundraisers`| Required | VOLUNTEER | Create relief campaign |
| **Vol Fund** | `GET` | `/volunteers/fundraisers`| Required | VOLUNTEER | List fundraisers |
| **Vol Dash** | `GET` | `/volunteers/overview` | Required | VOLUNTEER | Volunteer dashboard stats |
| **Gateway** | `POST` | `/gateway/sync` | None | Gateway | Sync offline mesh events |
| **Devices** | `POST` | `/devices/register` | Optional | Device | Register device telemetry |
| **Devices** | `GET` | `/devices/{device_id}`| None | Public | Get device status |
| **Media** | `POST` | `/media/signature` | Required | Any | Generate Cloudinary signature |
| **AI Chat** | `POST` | `/ai/chat` | None | Public | Disaster assistant guidance |

---

## 5. Detailed Endpoint Contracts

### 5.1 SOS Alert
#### `POST /api/v1/sos`
- **Auth**: Optional (auto-linked if authenticated)
- **Role**: Any
- **Request Body**:
```json
{
  "message": "Trapped in flood water on 2nd floor",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "severity": "CRITICAL",
  "origin_device_id": "DEV-ANDROID-01"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "data": {
    "id": "c1f7b0a8-...",
    "message_id": "VJ-SOS-98A1B2C3",
    "citizen_id": "00000000-0000-0000-0000-citizen00000",
    "origin_device_id": "DEV-ANDROID-01",
    "message": "Trapped in flood water on 2nd floor",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "severity": "CRITICAL",
    "status": "ACTIVE",
    "created_at": "2026-08-08T10:30:00Z",
    "received_at": "2026-08-08T10:30:01Z",
    "resolved_at": null
  },
  "message": "SOS alert registered successfully. Emergency authorities have been notified."
}
```

---

### 5.2 Nearby Shelters (Geographic Distance Search)
#### `GET /api/v1/shelters/nearby?latitude=28.6139&longitude=77.2090&radius_km=15`
- **Auth**: None
- **Query Params**:
  - `latitude` (float, required)
  - `longitude` (float, required)
  - `radius_km` (float, optional, default: 15.0)
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": [
    {
      "id": "e4a2-...",
      "name": "Central Sports Arena Shelter",
      "description": "High ground indoor shelter with backup power",
      "latitude": 28.6200,
      "longitude": 77.2150,
      "address": "Sector 4, Main Stadium Road",
      "capacity": 500,
      "occupied": 120,
      "available_capacity": 380,
      "status": "OPEN",
      "is_private": false,
      "distance_km": 0.91,
      "created_at": "2026-08-08T08:00:00Z",
      "updated_at": "2026-08-08T09:00:00Z"
    }
  ],
  "message": "Found 1 shelters within 15.0 km"
}
```

---

### 5.3 Offline Gateway Synchronization (Idempotent)
#### `POST /api/v1/gateway/sync`
- **Auth**: None (Gateway device sync)
- **Request Body**:
```json
{
  "gateway_id": "GW-DELHI-001",
  "events": [
    {
      "message_id": "VJ-OFFLINE-999",
      "type": "SOS",
      "created_at": "2026-08-08T09:15:00Z",
      "origin_device_id": "PHONE-MESH-44",
      "payload": {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "message": "Family stranded on rooftop",
        "severity": "CRITICAL"
      }
    }
  ]
}
```
- **Response `200 OK` (First Request)**:
```json
{
  "success": true,
  "accepted": ["VJ-OFFLINE-999"],
  "duplicates": [],
  "failed": []
}
```
- **Response `200 OK` (Second Request with Same Message ID)**:
```json
{
  "success": true,
  "accepted": [],
  "duplicates": ["VJ-OFFLINE-999"],
  "failed": []
}
```
*(No duplicate database records are ever created).*

---

### 5.4 VajraAI Emergency Assistant
#### `POST /api/v1/ai/chat`
- **Auth**: None (Public access for emergency queries)
- **Personas Supported**:
  - **Citizen**: Safety instructions (floods, earthquakes, fires, cyclones), nearest shelter routing, official announcements.
  - **Government EOC**: Situational data queries (e.g., *"Which areas currently have the highest number of SOS alerts?"*).
  - **Volunteers**: Operational guidance (e.g., *"Show me nearby incidents requiring assistance"*).
- **Request Body (Citizen Example)**:
```json
{
  "message": "What should I do during sudden heavy flooding?",
  "latitude": 28.6139,
  "longitude": 77.2090
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "reply": "Flood Safety Advisory: Move to higher ground immediately. Do not attempt to walk, swim, or drive through floodwaters...",
    "safety_advisory": "NOTICE: VajraAI assists human decision-makers by interpreting operational data and safety guidelines. It does not perform medical diagnosis, dispatch emergency vehicles directly, or replace human first responders.",
    "suggested_actions": [
      "Find nearby high-ground shelters",
      "Trigger SOS if trapped",
      "Check government announcements"
    ],
    "active_announcements_count": 2
  },
  "message": "AI safety response generated successfully"
}
```
- **Request Body (Government Example)**:
```json
{
  "message": "Which areas currently have the highest number of SOS alerts?"
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "reply": "Situational Awareness Summary: Currently tracking 14 active SOS alerts (6 CRITICAL priority) and 8 ongoing disaster incidents...",
    "safety_advisory": "NOTICE: VajraAI assists human decision-makers by interpreting operational data and safety guidelines...",
    "suggested_actions": [
      "Filter CRITICAL SOS alerts on map",
      "Publish area evacuation announcement",
      "Review open rescue incidents"
    ],
    "active_announcements_count": 2
  },
  "message": "AI safety response generated successfully"
}
```

