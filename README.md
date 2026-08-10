# ⚡ VajraNet — Authoritative Disaster Communication & Response Platform

> **Offline-capable emergency communication through peer-to-peer device relaying, connecting Citizens, Government Authorities (EOC), and Volunteer/Relief Networks.**

---

## 1. Core Concept & Product Flow

> **Citizen → SOS / Incident → Government + Volunteers**
>
> * **If Internet exists:** Send directly to the FastAPI cloud backend.
> * **If Internet does not exist:** Store the emergency locally in **Room Database** → relay through nearby VajraNet devices via P2P mesh (Nearby Connections / Wi-Fi Direct / Bluetooth) → reach an internet gateway device → synchronize to FastAPI backend (`POST /api/v1/gateway/sync`) → Government and Volunteers receive the emergency alert.

### Conceptual Flow

```text
                 CITIZEN
                    │
                   SOS
                    │
          ┌─────────┴─────────┐
          │                   │
      INTERNET             NO INTERNET
          │                   │
          ↓                   ↓
       BACKEND            LOCAL QUEUE (Room DB)
          │                   │
     ┌────┴────┐              ↓
     ↓         ↓         P2P MESH RELAY
 Government  Volunteers       │
                              ↓
                         Gateway Device
                              │
                              ↓
                        FastAPI Backend
                              │
                       ┌──────┴──────┐
                       ↓             ↓
                  Government     Volunteers
```

* **Online:** Real-time emergency coordination
* **Offline:** Delay-tolerant emergency delivery

---

## 2. Master System Architecture

```text
                         VAJRANET
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
  CITIZEN APP        GOVERNMENT DASHBOARD   VOLUNTEER PORTAL
  Android             Emergency EOC         NGOs / Private Bodies
       │                    │                    │
       │                    └────────┬───────────┘
       │                             │
       │                         FastAPI
       │                         Backend
       │                             │
       │                         Supabase (PostgreSQL)
       │
       │
       ├──── INTERNET ───────────────► Backend
       │
       │
       └──── NO INTERNET
                  │
             Nearby Devices
                  │
             P2P Relay/Mesh
                  │
          Internet Gateway Device
                  │
                  ▼
             FastAPI Backend
                  │
          ┌───────┴────────┐
          ▼                ▼
     Government        Volunteers
```

---

## 3. Technology Stack

| Component | Technology | Role & Scope |
| :--- | :--- | :--- |
| **Citizen App** | Native Android + Kotlin / Android APIs | Offline discovery, Room local storage, SOS trigger, incident reporting, Nearby resources, announcements, VajraAI |
| **Offline Communication** | Google Nearby Connections / Bluetooth / Wi-Fi Direct | Device discovery, peer communication, delay-tolerant mesh relay (`com.vajranet.offline.SERVICE_ID`, `P2P_STAR`) |
| **Local Offline Storage** | **Room Database** | Buffering unsent SOS signals & incident reports locally on Android native |
| **Government Dashboard** | React + TypeScript + Tailwind CSS | Emergency command EOC, triage SOS alerts, verify incidents, publish announcements, manage official shelters/hospitals/relief |
| **Volunteer Dashboard** | React + TypeScript + Tailwind CSS | Support response, claim tasks, register private shelters & private hospitals, manage disaster relief fundraisers |
| **Maps & GIS** | Leaflet | Real-time geospatial mapping of SOS distress coordinates, incidents, and emergency resources |
| **Backend API** | Python + FastAPI | REST APIs, Supabase Auth validation, RBAC, Gateway mesh synchronization, VajraAI service, analytics |
| **Database** | PostgreSQL / Supabase | Relational data persistence with geographic coordinate indexing |
| **Authentication** | Supabase Auth + JWT / RBAC | Role-based permissions: `CITIZEN`, `VOLUNTEER`, `GOVERNMENT`, `ADMIN` |
| **Media Storage** | Cloudinary | Signed secure disaster photo & incident evidence upload |
| **AI Assistant** | VajraAI Backend Service | Human-in-the-loop disaster safety guidance, EOC data interpretation, volunteer task guidance |
| **Backend Hosting** | Render | Automated web service deployment (`render.yaml`) |
| **Frontend Hosting** | Vercel | Production CDN deployment |
| **App Distribution** | APK / Android Device | Native citizen APK build |

---

## 4. Separation of Responsibilities

### 📱 Android Layer (Offline Mesh & Local Node)
* Google Nearby Connections (`com.vajranet.offline.SERVICE_ID`)
* Bluetooth / Wi-Fi Direct peer discovery
* Peer-to-peer message and SOS relaying
* **Room Database** local queue persistence
* Automatic gateway synchronization when internet becomes available

### ⚙️ Backend Layer (FastAPI Cloud Services)
* Authentication & RBAC token verification
* SOS triage and lifecycle management
* Disaster incident reporting and verification
* Resource management: Official shelters, government hospital bed/ICU tracking, relief distribution centers
* Emergency public announcements
* **Gateway Synchronization (`POST /api/v1/gateway/sync`)**: Idempotent deduplication of offline mesh events
* VajraAI disaster advisory service & situational statistics
* Analytics & EOC metrics

### 🏛️ Government Dashboard (Master Emergency Authority / EOC)
* **🚨 Emergency:** Incoming SOS alerts, triage, severity escalation, incident verification, multi-agency response coordination
* **📢 Public Information:** Evacuation orders, disaster bulletins, area-specific safety instructions
* **🏠 Shelters:** Official shelter locations, total capacity, occupancy, real-time availability
* **🏥 Hospitals:** Government hospital availability, general beds, ICU beds, trauma availability
* **📦 Relief:** Food, water, medicine, essential supply distribution centers
* **🗺️ Situational Awareness:** Geographic mapping of SOS alerts, incidents, and response resources

### 🤝 Volunteer Dashboard (Supporting Relief Network / NGOs)
* **🚑 Response:** View incidents requiring assistance, claim/accept field tasks, update rescue progress, mark resolved
* **🏠 Private Shelters:** Register community/NGO shelters, update capacity and availability
* **🏥 Private Hospitals:** Register private clinics/hospitals, update general and ICU bed availability
* **💰 Fundraising:** Create disaster-relief fundraising campaigns and track community contributions
* **👥 Operations:** Volunteer skills, availability, deployment location, active tasks

### 🧠 VajraAI (Human-Assistive Model)
* **Citizen:** *"What should I do during sudden flooding?"* → Safety protocols and verified shelter routing.
* **Government:** *"Which areas currently have the highest number of SOS alerts?"* → Synthesizes live database alerts and cluster hotspots.
* **Volunteer:** *"Show me nearby incidents requiring assistance."* → Interprets open field tasks and relief priorities.
* **Strict Guardrail:** VajraAI assists human decision-makers and **never makes independent critical medical or rescue dispatch determinations**.

---

## 5. Quick Start (Local Backend Setup)

### 1. Clone & Setup Python Environment
```bash
git clone https://github.com/your-org/vajranet-backend.git
cd vajranet-backend

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run Backend Locally
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Interactive Documentation
* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 6. Running Automated Tests

Run the full automated test suite with pytest:
```bash
python -m pytest -v
```

---

## 7. Deployment on Render

This repository includes `render.yaml` and `Dockerfile`.

1. Connect your repository to **Render**.
2. Select **Blueprint** using `render.yaml` or create a **New Web Service**.
3. Set environment variables (`DATABASE_URL`, `JWT_SECRET`, `SUPABASE_URL`, `CLOUDINARY_*`).
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Health Check Path: `/health`

---

## 8. Integration Contracts

Refer to [API.md](file:///c:/Users/vansh/Desktop/Projects/vajranet-backend/API.md) for the complete integration contract, payload schemas, and example requests/responses.
