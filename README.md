# SANGAM — Societal Innovation Platform
# Smart India Hackathon 2026 · Problem Statement SIH26043

Crowdsource societal challenges and facilitate collaborative problem-solving through universities and industry partnerships.

## What this prototype includes

| Layer | Status |
|--------|--------|
| Challenge submission + uploads | **Real functionality** |
| Local AI (classify, priority factors, duplicate similarity, university matching) | **Real functionality** (local algorithms — not an external LLM) |
| **RAG** (retrieve playbooks + live challenges/projects, grounded answers) | **Real functionality** (local TF-IDF; optional OpenAI if `OPENAI_API_KEY`) |
| Role workspaces (Citizen, Gov, University, Student, Industry) | **Real functionality** |
| Project lifecycle, milestones, collaborations, feedback | **Real functionality** |
| Charts, district map points, impact stats | **Real functionality** against DB |
| Universities, CSR partners, AquaGuard journey | **Demo Data** (clearly labeled) |
| Payments / production auth / live gov stats | **Future integration** |

## Stack

- **Frontend:** React, Vite, Tailwind CSS, Recharts, Leaflet
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** SQLite by default (zero-setup demo). Optional PostgreSQL via `DATABASE_URL`.

PostGIS is noted as a **future integration** for advanced geographic queries; the prototype stores lat/lng and renders OpenStreetMap markers.

## Quick start (Windows)

### 1. Backend

```bat
cd sangam\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8100
```

API docs: http://localhost:8100/docs  
Health: http://localhost:8100/api/health

### 2. Frontend

```bat
cd sangam\frontend
npm install
npm run dev
```

App: http://localhost:5180

### One-click helpers

- `start.bat` (Windows) / `start.sh` (Unix) — starts API + Vite if present.

## Separate portal logins

Each stakeholder has its own sign-in page:

| Portal | URL | Demo email | Password |
|--------|-----|------------|----------|
| Citizen | `/login/citizen` | citizen.demo@sangam.local | citizen123 |
| Admin / Government | `/login/admin` | gov.demo@sangam.local | admin123 |
| University | `/login/university` | uni.demo@sangam.local | uni123 |
| Student / SSC | `/login/ssc` | student.demo@sangam.local | student123 |
| Industry / CSR | `/login/csr` | industry.demo@sangam.local | csr123 |

Hub: `/login`. Workspaces are role-locked after login. **Demo auth only** — not production security.

## RAG (Retrieval-Augmented Generation)

Open **RAG** in the app header (`/rag`) or see suggestions after challenge submit.

- Retrieves from demo playbooks + live challenges/projects/universities
- Answers cite sources with relevance scores
- Default: local TF-IDF + grounded synthesis (works offline)
- Optional: set `OPENAI_API_KEY` for LLM generation over retrieved context
- Details: `docs/RAG.md`

## Demo mode (3–5 minutes)

1. Open **Demo Guide** in the app header.
2. Or switch roles in the header:
   - **Citizen** — submit flood challenge (prefilled) → see AI panel
   - **Government** — validate queue, charts, map, reset demo
   - **University** — accept challenge / open AquaGuard
   - **Student** — team AquaGuard, milestones, status
   - **Industry** — offer mentorship (no real money)
   - **Impact** — measurable outcomes
3. Seeded journey already includes AquaGuard at **Pilot** with community feedback.

Reset: Government dashboard → **Reset Demo Data**.

## Data provenance labels

- **Demo Data** — seeded prototype institutions, partners, sample challenges/projects
- **User-generated** — created through the UI in this session
- **Prototype AI** — keyword NLP + bag-of-words cosine similarity + transparent weighted scoring
- Never presented as official government statistics or real university partnerships

## Environment

### Backend `.env`

```
DATABASE_URL=sqlite:///./sangam.db
UPLOAD_DIR=./uploads
CORS_ORIGINS=http://localhost:5180,http://127.0.0.1:5180
DATA_MODE=prototype
```

Optional PostgreSQL:

```
DATABASE_URL=postgresql://sangam:sangam@localhost:5432/sangam
```

### Frontend `.env`

```
VITE_API_URL=http://localhost:8100
```

## Testing

```bat
cd sangam\backend
.venv\Scripts\activate
python -c "from app.ai.engine import build_full_analysis; print(build_full_analysis('Flood damaged drinking water','pipelines ruptured','Water','Barmer',5000,'high','high','district',[],[])['domain'])"
```

Manual API checks:

```bat
curl http://localhost:8100/api/health
curl http://localhost:8100/api/admin/stats
curl http://localhost:8100/api/projects
```

## Project layout

```
sangam/
  backend/app/          FastAPI app, models, AI engine, routers, seed
  frontend/src/         React role UIs, charts, map, demo guide
  README.md
```

## AI methods (honest disclosure)

1. **Classification** — keyword scores across civic domains  
2. **Priority** — weighted factors shown in UI (people, urgency, severity, spread, evidence)  
3. **Duplicates** — bag-of-words cosine similarity (local; not a neural embedding API)  
4. **University matching** — structured expertise overlap with explanations  

To plug a real embedding/LLM API later, replace functions in `backend/app/ai/engine.py` and update the method labels returned to the UI.

## License / SIH note

Built as a hackathon prototype. Demo organizations are fictional. Do not treat metrics as official statistics.
