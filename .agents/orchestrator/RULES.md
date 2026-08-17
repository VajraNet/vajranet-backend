# 📜 VajraNet Multi-Agent Development Rules

All agents operating in the VajraNet ecosystem MUST adhere to these 15 inviolable rules at all times.

---

## 1. The 15 Inviolable Development Rules

1. **Never Fake Core Functionality:**
   Do not mock or fabricate emergency radios, BLE signal strengths, Nearby Connections links, mesh relays, gateway submissions, or delivery confirmations. Represent hardware state honestly.

2. **Never Claim a Test Passed Without Running It:**
   Execute actual test commands (`python -m pytest`, `npm run build`, `gradlew`) and report real terminal outputs.

3. **Never Overwrite Uncommitted User Work:**
   Inspect `git status` before touching files. Preserve user work and stash/commit cleanly.

4. **Never Delete Existing Working Functionality:**
   Refactor and extend without breaking existing feature sets.

5. **Never Break API Contracts Silently:**
   Any change to endpoints, request bodies, response models, query parameters, status codes, or enums MUST be routed through `@orchestrator` and updated in `.agents/shared/API_CONTRACT.md`.

6. **Never Duplicate SOS Implementations:**
   There is exactly ONE canonical SOS architecture. Online uses `POST /api/v1/sos`, SMS fallback uses registered trusted contacts, and Offline Mesh uses `POST /api/v1/gateway/sync`. All paths preserve the originating `message_id`.

7. **Never Create Duplicate Emergency Resource Databases:**
   `vajranet-backend` (PostgreSQL / Supabase) is the single authoritative source of truth for shelters, hospitals, relief centers, announcements, and incidents. VajraAI and clients must consume from the main backend.

8. **Never Use Mock Authentication in Production:**
   Enforce real Supabase JWT Bearer token authentication and role checking (`CITIZEN`, `VOLUNTEER`, `GOVERNMENT`, `ADMIN`).

9. **Never Fake Mesh Devices in Android UI:**
   Android mesh screens must query real Google Nearby Connections `P2P_CLUSTER` discovery and real Bluetooth/Wi-Fi Direct hardware states.

10. **Never Fake Gateway Synchronization:**
    Gateway sync must genuinely batch-post un-synced offline packets to the cloud backend and return cryptographic/reverse `GATEWAY_ACK` packets across the mesh.

11. **Never Expose Sensitive Citizen Information Unnecessarily:**
    Enforce citizen data privacy; only authorized government command centers and assigned rescue squads may access full victim profiles.

12. **Never Modify Unrelated Repositories Directly:**
    Each agent owns strictly its designated repository. Cross-repository changes MUST be coordinated by `@orchestrator`.

13. **Prefer Simple, Resilient Architecture:**
    Avoid unnecessary microservices, message queues (Kafka/RabbitMQ), or container orchestration where FastAPI, PostgreSQL, React, and Native Android provide cleaner, lower-latency emergency response.

14. **Preserve Existing UI Aesthetic & Mission Control Styling:**
    Government UI must look like an authentic Indian District Emergency Operations Centre / Police Control Room, NOT a generic AI SaaS dashboard.

15. **Coordinate All Cross-Repository Changes Through `@orchestrator`:**
    No agent may unilaterally alter shared models, schemas, or network assumptions without orchestrator mediation.

---

## 2. Git & Working Safety Rules

* **Pre-Flight Inspection:** Always run `git status -s` before modifying code.
* **Prohibited Git Commands:**
  - `git reset --hard` (Strictly forbidden without explicit user command)
  - `git clean -fd` (Strictly forbidden)
  - Blind `git checkout .`
* **Commit Standards:** Use clear, conventional commit messages:
  - `feat: implement idempotent gateway sync`
  - `fix: resolve volunteer list attribute error`
  - `docs: update offline mesh protocol spec`
