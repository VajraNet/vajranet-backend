# VajraNet Backend

> **Disaster Communication and Emergency Response Platform** connecting **Citizens**, **Government Authorities**, and **Volunteers/Relief Bodies** during disaster scenarios through online REST APIs and offline mesh-relayed synchronization.

---

## 1. Product Story

```
CITIZEN (Online)
      ↓
  FastAPI Backend ──→ Government Dashboard + Volunteers
      ↑
CITIZEN (Offline - No Internet)
      ↓
  Nearby VajraNet Devices (Mesh Relay)
      ↓
  Gateway Device (Gains Internet)
      ↓
  POST /api/v1/gateway/sync (Idempotent Deduplication)
      ↓
  FastAPI Backend ──→ Government Dashboard + Volunteers
```

---

## 2. Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Validation**: Pydantic v2 & Pydantic-Settings
- **ORM & DB**: SQLAlchemy 2.x with PostgreSQL (Supabase) / SQLite (Local & Testing)
- **Security**: Supabase JWT validation & RBAC (Citizen, Volunteer, Government, Admin)
- **Testing**: Pytest & HTTPX test client

---

## 3. Quick Start (Local Setup)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-org/vajranet-backend.git
cd vajranet-backend

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run Locally
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Interactive Documentation
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 4. Running Automated Tests

Run the full automated test suite:
```bash
pytest -v
```

---

## 5. Deployment on Render

This repository includes `render.yaml` and `Dockerfile`.

1. Connect your repository to **Render**.
2. Select **New Web Service** or choose **Blueprint (render.yaml)**.
3. Set your environment variables (`DATABASE_URL`, `JWT_SECRET`, `SUPABASE_URL`, etc.).
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Health Check Path: `/health`

---

## 6. Frontend Integration

Refer to [API.md](file:///c:/Users/vansh/Desktop/Projects/VajraNet/API.md) for the complete integration contract, payload schemas, and example requests/responses.
