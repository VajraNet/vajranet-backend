# 🏛️ VajraNet — Shared System Architecture Blueprint

## 1. High-Level Ecosystem Architecture

VajraNet is a unified disaster emergency response ecosystem engineered for extreme resilience during telecommunication blackouts.

```
                         VAJRANET ECOSYSTEM
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
    CITIZEN ANDROID        GOVERNMENT WEB         VOLUNTEER WEB
   (Native Kotlin App)    (EOC Control Room)    (Field Operations)
          │                      │                      │
          │                      └──────────┬───────────┘
          │                                 │
          │                           FastAPI Core
          │                                 │
          │                        Supabase PostgreSQL
          │
          │
          └───── Tri-Tier Failover ───────┐
                                          │
                                   Nearby Devices (BLE / Wi-Fi Direct)
                                          │
                                        Relay (TTL <= 5)
                                          │
                                       Gateway (Internet Active)
                                          │
                                   POST /api/v1/gateway/sync
                                          │
                                     FastAPI Core
```

---

## 2. Tri-Tier Communication Failover Strategy

| Tier | Network Condition | Primary Communication Path | Protocol / Technology |
|---|---|---|---|
| **Tier 1** | Internet Active (Wi-Fi / 4G / 5G) | Citizen App ➔ Cloud Backend ➔ EOC / Volunteers | HTTPS / REST (`POST /api/v1/sos`) |
| **Tier 2** | Degraded Cellular (SMS Only, No Net) | Citizen App ➔ Nearest Trusted Emergency Contact | Android Telephony / SMS Intent (`Intent.ACTION_SENDTO`) ➔ Ingestion via `POST /api/v1/devices/trusted/relay-sos` |
| **Tier 3** | Complete Blackout (Zero Net + Zero Cell) | Citizen App ➔ Nearby Peer Mesh ➔ Cloud Gateway ➔ EOC | Google Play Services Nearby Connections (`Strategy.P2P_CLUSTER`) ➔ `POST /api/v1/gateway/sync` |

---

## 3. The Canonical SOS Lifecycle

There is exactly **ONE** logical SOS distress event for each emergency incident:

1. **Generation:** Device A generates unique `message_id = "VJ-SOS-DEL-89241"`, records timestamp, GPS coordinates, and victim details.
2. **Local Persistence:** Event is stored in Device A's Room database and unacknowledged DTN buffer.
3. **Multi-Hop Propagation:**
   - Device A relays packet to Device B (`hops = 0`).
   - Device B verifies deduplication, increments `hops = 1`, and relays to Device C (`hops = 1`).
4. **Autonomous Gateway Ingestion:**
   - Device C detects active internet connection.
   - Device C batch-posts the packet to `POST /api/v1/gateway/sync`.
   - Backend ingests the packet into `sos_alerts` and `offline_events`, maintaining original `message_id = "VJ-SOS-DEL-89241"`.
   - Backend returns HTTP 200 with `accepted: ["VJ-SOS-DEL-89241"]`.
5. **Reverse `GATEWAY_ACK` Delivery Confirmation:**
   - Device C broadcasts `GATEWAY_ACK` (refId: `"VJ-SOS-DEL-89241"`) back across the mesh to Device B.
   - Device B relays `GATEWAY_ACK` to Device A.
   - Device A updates UI to **Official Acknowledgment Confirmed**.
6. **EOC Triage:** The Government Control Room displays the alert on the live tactical situation map with real-time status updates (`ACTIVE` ➔ `ACKNOWLEDGED` ➔ `IN_PROGRESS` ➔ `RESOLVED`).

---

## 4. Single Authoritative Source of Truth
* All emergency resources (shelters, hospital beds, ICU counts, relief supplies, official evacuation bulletins) reside authoritatively in `vajranet-backend`.
* **VajraAI** and all frontend applications query the central backend directly.
* Duplicate, divergent, or isolated databases are strictly prohibited.
