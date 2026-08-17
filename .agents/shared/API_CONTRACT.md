# 🔌 VajraNet — Shared Authoritative REST API Contract

**Base URL (Cloud):** `https://vajranet-backend.onrender.com/api/v1`  
**Base URL (Local):** `http://localhost:8000/api/v1`  
**Standard Envelope:** `{ "success": true, "data": Any, "message": str }`

---

## 1. Authentication & Headers
* **Header:** `Authorization: Bearer <SUPABASE_JWT_TOKEN>`
* **Development Tokens:**
  - Citizen: `Bearer mock-citizen-token`
  - Volunteer: `Bearer mock-volunteer-token`
  - Government EOC: `Bearer mock-government-token`
  - Admin: `Bearer mock-admin-token`

---

## 2. Core API Endpoint Registry

### 2.1 SOS Emergency Distress (`/sos`)
| Method | Endpoint | Auth | Request Body | Response Envelope `data` | Description |
|---|---|---|---|---|---|
| `POST` | `/sos` | Optional | `{ message, latitude, longitude, severity, origin_device_id, message_id? }` | `SOSResponse` | Creates new SOS alert or preserves existing `message_id` |
| `GET` | `/sos` | None | Query: `status`, `severity`, `skip`, `limit` | `List[SOSResponse]` | Public SOS stream for tactical map pins & responders |
| `GET` | `/sos/my` | Required | None | `List[SOSResponse]` | Returns SOS alerts created by authenticated citizen |
| `GET` | `/sos/{id}` | Optional | Path `id` | `SOSResponse` | Single SOS detail view |
| `PATCH` | `/sos/{id}` | Optional | `{ status, severity }` | `SOSResponse` | Update status (`ACTIVE`, `ACKNOWLEDGED`, `IN_PROGRESS`, `RESOLVED`) |
| `DELETE`| `/sos/{id}` | Optional | Path `id` | `{"id": str, "deleted": true}` | Purge SOS alert |

### 2.2 Offline Mesh Gateway Sync (`/gateway`)
| Method | Endpoint | Auth | Request Body | Direct JSON Response | Description |
|---|---|---|---|---|---|
| `POST` | `/gateway/sync` | None | `{ gateway_id: str, events: List[GatewayEventItem] }` | `{ "success": true, "accepted": List[str], "duplicates": List[str], "failed": List[str] }` | **Idempotent batch sync** for offline SOS, incidents & telemetry |

*Note: Gateway sync payload supports both `payload.get("message")` and `payload.get("notes")`.*

### 2.3 Disaster Incidents (`/incidents`)
| Method | Endpoint | Auth | Request Body | Response Envelope `data` | Description |
|---|---|---|---|---|---|
| `POST` | `/incidents` | Optional | `{ title, description, type, latitude, longitude, severity, media_urls: [] }` | `IncidentResponse` | Submit disaster report (Flood, Fire, Landslide, etc.) |
| `GET` | `/incidents` | None | Query: `type`, `severity`, `status`, `skip`, `limit` | `List[IncidentResponse]` | Public listing of all reported incidents |
| `GET` | `/incidents/my`| Required | None | `List[IncidentResponse]` | Incidents reported by current user |
| `PATCH` | `/incidents/{id}` | Optional | `{ title?, description?, severity?, status?, media_urls? }` | `IncidentResponse` | Edit or verify disaster report |

### 2.4 Emergency Resources (Shelters, Hospitals, Relief Centers)
| Resource | Method | Endpoint | Query Parameters | Response Fields |
|---|---|---|---|---|
| **Shelters** | `GET` | `/shelters/nearby` | `latitude`, `longitude`, `radius_km=15` | `id`, `name`, `capacity`, `occupied`, `available_capacity`, `status`, `distance_km` |
| **Hospitals**| `GET` | `/hospitals/nearby` | `latitude`, `longitude`, `radius_km=15` | `id`, `name`, `total_beds`, `available_beds`, `icu_beds_total`, `icu_beds_available`, `emergency_available`, `distance_km` |
| **Relief** | `GET` | `/relief-centers/nearby`| `latitude`, `longitude`, `radius_km=15`| `id`, `name`, `items_available`, `status`, `distance_km` |
| **Broadcasts**| `GET` | `/announcements` | `skip`, `limit` | `id`, `title`, `content`, `type`, `priority`, `area`, `created_at` |

### 2.5 Government Authority Command (`/government`)
| Method | Endpoint | Required Role | Request Body | Description |
|---|---|---|---|---|
| `GET` | `/government/overview` | `GOVERNMENT`, `ADMIN` | None | EOC master dashboard statistics |
| `GET` | `/government/sos` | `GOVERNMENT`, `ADMIN` | `status`, `severity` | Live EOC priority SOS triage stream |
| `PATCH` | `/government/sos/{id}` | `GOVERNMENT`, `ADMIN` | `{ status, severity }` | Update SOS triage lifecycle |
| `GET` | `/government/incidents` | `GOVERNMENT`, `ADMIN` | Filter queries | Command center incident sit-rep |
| `POST` | `/government/announcements` | `GOVERNMENT`, `ADMIN` | `{ title, content, type, priority, area }` | Broadcast official alert |
| `POST` | `/government/shelters` | `GOVERNMENT`, `ADMIN` | `ShelterCreate` (`is_private=False`) | Create official state shelter |
| `POST` | `/government/hospitals` | `GOVERNMENT`, `ADMIN` | `HospitalCreate` (`GOVERNMENT`) | Register official state hospital |

### 2.6 Volunteer Operations (`/volunteers`)
| Method | Endpoint | Required Role | Request / Response | Description |
|---|---|---|---|---|
| `GET` | `/volunteers/overview` | `VOLUNTEER`, `ADMIN` | Stats & active tasks | Volunteer dashboard summary |
| `GET` | `/volunteers/incidents` | None (Public) | List of claimable incidents | Nearby claimable response tasks |
| `POST` | `/volunteers/incidents/{id}/accept` | `VOLUNTEER`, `ADMIN` | Claims task ➔ moves to `IN_PROGRESS` | Volunteer squad task claim |
| `PATCH` | `/volunteers/incidents/{id}/status` | `VOLUNTEER`, `ADMIN` | Progress: `IN_PROGRESS` ➔ `COMPLETED` | Complete volunteer assignment |
| `POST` | `/volunteers/fundraisers` | `VOLUNTEER`, `ADMIN` | `{ title, description, target_amount, beneficiary }` | Create relief fundraiser |

### 2.7 Trusted SMS Relays & Emergency Contacts (`/devices`, `/emergency-contacts`)
| Method | Endpoint | Auth | Request / Body | Description |
|---|---|---|---|---|
| `POST` | `/devices/trusted/relay-sos` | None | `{ sender_phone, raw_sms }` | Ingest forwarded SMS distress alerts into backend |
| `GET` | `/devices/nearby` | None | `lat`, `lng`, `radius_km` | Find nearest responder phone for SMS dispatch |
| `GET/POST`| `/emergency-contacts` | Required | `{ name, phone, relation }` | Citizen emergency contacts (Max 5 enforced) |
| `POST` | `/media/signature` | Required | `{ folder, resource_type }` | Direct Cloudinary upload signature |
| `POST` | `/ai/chat` | None | `{ message, latitude, longitude }` | Deterministic AI safety advice & resource retrieval |
