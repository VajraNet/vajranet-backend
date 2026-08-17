# 📝 VajraNet Ecosystem Changelog

All notable architectural, API, and cross-repository modifications are recorded in this file.

---

## [1.0.0] — 2026-08-16

### 🏛️ Orchestration & Multi-Agent Architecture
* **Initialized Control Center:** Created `.agents/` central control directory inside `vajranet-backend` with dedicated agent specifications (`@orchestrator`, `@backend-agent`, `@frontend-agent`, `@android-agent`, `@vajraai-agent`, `@docs-agent`).
* **Established Governance:** Enforced 15 inviolable development rules (`RULES.md`), 12-step decision loop (`AGENT.md`), and cross-agent communication pipeline (`WORKFLOW.md`).

### 🛠️ Backend (`vajranet-backend`)
* **Fixed Runtime Bug on Volunteers List:** Added safe attribute access (`getattr(v, 'is_verified', True)`) in `app/api/v1/volunteers.py` to prevent 500 error on `GET /api/v1/volunteers`.
* **Completed Supabase DDL:** Added `trusted_devices` table and indexes (`idx_trusted_devices_user_id`, `idx_trusted_devices_phone`) to `schema.sql`.
* **Exported TrustedDevice Model:** Added `TrustedDevice` to `__all__` in `app/models/__init__.py`.
* **Harmonized Gateway Payload Fields:** Updated `app/services/gateway_service.py` to support both `payload.get("message")` and `payload.get("notes")` during offline gateway SOS ingestion.
* **Enforced Strict Government RBAC:** Restricted `/government/sos`, `/government/sos/{id}`, `/government/incidents`, and `/government/incidents/{id}` strictly to `UserRole.GOVERNMENT` and `UserRole.ADMIN`.
* **Test Verification:** Passed 30/30 Pytest test suites (100%).

### 🤖 VajraAI (`VajraAi`)
* **Fixed Missing Model Imports:** Imported `Shelter, Hospital, ReliefCenter, Announcement, EmergencyIncident` in `backend/main.py` allowing clean startup database seeding.
* **Fixed Local SOS Fallback Crash:** Corrected `EmergencyIncident` instantiation in `backend/app/api/v1/ai.py` to match exact database columns.
* **Build Verification:** Passed 7/7 backend Pytest tests and successfully built React frontend with Vite.

### 📱 Citizen Android Native App (`demo-vajra`)
* **Architecture Verification:** Validated 100% native Kotlin + Jetpack Compose app with Google Nearby Connections `Strategy.P2P_CLUSTER` mesh networking.
* **Tri-Tier Failover Verification:** Validated online SOS, SMS fallback with nearest trusted responder discovery, multi-hop relay (TTL max 5 hops), epidemic DTN buffering, and reverse `GATEWAY_ACK` confirmation.

### 🖥️ Government & Volunteer Frontend (`vajranet-frontend`)
* **Tactical EOC UI Verification:** Validated high-contrast control room dark theme, GIS situation map, and live SOS queue triage.
* **Production Build:** Verified Vite bundling with 1,884 modules transformed in 4.69s.

### 📚 Technical Documentation (`vajranet-docs`)
* **Authored `OFFLINE_P2P_TEST.md`:** Comprehensive 3-device physical testing runbook with sequence diagrams and pass/fail criteria.
* **Aligned API Reference (`03_API_REFERENCE.md`):** Updated hospital attributes (`emergency_available`), announcement attributes (`content`, `area`), AI chat response schemas, and SMS relay endpoint (`POST /api/v1/devices/trusted/relay-sos`).
* **Aligned Database Schema (`04_DATABASE_SCHEMA.md`):** Updated table names (`offline_events`, `fundraising_campaigns`, `devices`, `emergency_contacts`, `trusted_devices`).
