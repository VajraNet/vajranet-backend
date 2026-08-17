# 🤝 VajraNet — Cross-Repository Integration Rules

To maintain flawless interoperability between Backend, Frontend, Android, and VajraAI, all agents must comply with these technical integration standards:

---

## 1. Response Envelope Protocol

* **Standard API Responses:** Encapsulated in the canonical response envelope:
  ```json
  {
    "success": true,
    "data": { ... },
    "message": "Human-readable message"
  }
  ```
  - **Frontend / Axios Client:** Automatically unwrap `response.data.data` while preserving `message` for user notifications.
  - **Android Client:** Check `optBoolean("success")` and parse `optJSONObject("data")` or `optJSONArray("data")`.

* **Gateway Batch Sync Exception:** `POST /api/v1/gateway/sync` returns a top-level payload for mesh radio efficiency:
  ```json
  {
    "success": true,
    "accepted": ["VJ-SOS-DEL-89241"],
    "duplicates": [],
    "failed": []
  }
  ```

---

## 2. Geospatial Parameter Naming Conventions

* **Proximity Queries:** Always use standard query parameter names:
  - Latitude: `latitude` (Float, e.g. `28.6139`)
  - Longitude: `longitude` (Float, e.g. `77.2090`)
  - Radius: `radius_km` (Float, e.g. `15.0`)
* *Alias Support:* The backend tolerates `lat`, `lon`, `lng`, but client applications should standardize on `latitude` and `longitude`.

---

## 3. Authentication & Token Exchange

* **Header Format:** `Authorization: Bearer <JWT_TOKEN>`
* **Supabase JWT Specs:** HS256 algorithm with claims:
  - `sub`: User UUID (`VARCHAR(36)`)
  - `email`: User email address
  - `user_metadata.role`: Role string (`CITIZEN`, `VOLUNTEER`, `GOVERNMENT`, `ADMIN`)
* **Security Rule:** Never transmit long-lived JWTs via insecure iframe `postMessage` or exposed URL query parameters in production.

---

## 4. Offline Mesh & Gateway Ingestion Rule

* **Message Field Compatibility:** Gateway sync service must accept both:
  - `payload.get("message")`
  - `payload.get("notes")`
* **Canonical ID:** Client must generate `message_id` before transmission (e.g. `VJ-SOS-<UUID>`). Never allow the gateway to regenerate a new ID for an existing packet.
