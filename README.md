# SANGAM — Societal Innovation Platform
**Smart India Hackathon 2026 · SIH26043**

Crowdsource societal challenges and connect them with universities and industry partners who can collaborate on solutions.

## Features

| Capability | Status |
|------------|--------|
| Voice / photo / text citizen reporting | Real |
| Multilingual UI (en, te, hi, …) | Real |
| Local problem intelligence + semantic similarity | Real (local heuristics; optional OpenAI for RAG text) |
| University / industry matching (demo institutions labeled) | Real |
| Project lifecycle, plan suggestions, community feedback | Real |
| Role portals (citizen, admin, university, student, industry) | Real |
| Payments / production SSO | Future |

## Architecture

```text
frontend/   React + Vite + Tailwind   →  http://localhost:5180
backend/    FastAPI + SQLAlchemy      →  http://localhost:8100
database    SQLite by default (optional PostgreSQL via DATABASE_URL)
```

On startup the API creates tables and seeds demo data. PostGIS is **not** required.

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+ (includes npm)
- Git

## Quick start

```bash
git clone https://github.com/pranaveshan/sangam.git
cd sangam
```

### First time

**Windows**

```bat
setup.bat
start.bat
```

**Linux / macOS**

```bash
chmod +x setup.sh start.sh
./setup.sh
./start.sh
```

### Every later time

```bat
start.bat
```

```bash
./start.sh
```

Then open:

| Service | URL |
|---------|-----|
| App | http://localhost:5180 |
| Login hub | http://localhost:5180/#/login |
| API docs | http://localhost:8100/docs |
| Health | http://localhost:8100/api/health |

`start` will call `setup` automatically if `.venv` or `node_modules` are missing.

## Manual setup (optional)

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd ..
backend\.venv\Scripts\python.exe backend\scripts\init_db.py

cd frontend
npm install
copy .env.example .env
npm run dev
```

In another terminal:

```bat
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8100
```

## Environment configuration

Copy examples (done by `setup`):

- `backend/.env.example` → `backend/.env`
- `frontend/.env.example` → `frontend/.env`

Important variables:

```text
DATABASE_URL=sqlite:///./sangam.db
CORS_ORIGINS=http://localhost:5180,http://127.0.0.1:5180
UPLOAD_DIR=./uploads
VITE_API_URL=http://localhost:8100
```

Never commit real secrets. Optional `OPENAI_API_KEY` enables LLM text over RAG retrieval only.

## Database

- **Default:** SQLite file `backend/sangam.db` (created automatically).
- **Init / seed:** `backend/scripts/init_db.py` or API lifespan on first start.
- **Optional:** set `DATABASE_URL` to PostgreSQL. PostGIS is not used by the running app.
- **Reset demo data:** Admin portal → Reset Demo Data (or `POST /api/demo/reset`).

## Production build (local)

```bat
deploy-local.bat
```

This installs deps if needed, builds the frontend, copies assets into `backend/static/`, and serves API + UI at **http://localhost:8100**.

`website/` is a generated static package (gitignored) for optional Netlify-style hosts.

Docker: see `Dockerfile` and `render.yaml`.

## Demo portal logins

| Portal | Path | Email | Password |
|--------|------|-------|----------|
| Citizen | `/#/login/citizen` | citizen.demo@sangam.local | citizen123 |
| Admin | `/#/login/admin` | gov.demo@sangam.local | admin123 |
| University | `/#/login/university` | uni.demo@sangam.local | uni123 |
| Student | `/#/login/ssc` | student.demo@sangam.local | student123 |
| Industry | `/#/login/csr` | industry.demo@sangam.local | csr123 |

Demo auth only — not production security. Institutions and AquaGuard journey are labeled **DEMO DATA**.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Python was not found` | Install Python 3.10+ and ensure it is on PATH |
| `Node.js was not found` | Install Node.js 18+ |
| Port 5180 / 8100 in use | Stop the other process, or change ports in `start.bat` / `vite.config.js` and update `CORS_ORIGINS` |
| Frontend cannot reach API | Confirm backend is up; check `VITE_API_URL` and `CORS_ORIGINS` |
| Broken `init_db` imports | Use current `backend/scripts/init_db.py` (this repo no longer uses `app.database.connection`) |

## Project structure

```text
sangam/
  setup.bat / setup.sh      First-time install
  start.bat / start.sh      Dev servers (5180 + 8100)
  deploy-local.bat          Production-style local serve on :8100
  backend/                  FastAPI app, AI services, seed
  frontend/                 React UI
  docs/                     Detailed developer notes
  index.html                Helper page (not the Vite app)
```

## More detail

See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md), [`docs/TESTING.md`](docs/TESTING.md), [`docs/RAG.md`](docs/RAG.md).

## License / SIH note

Hackathon prototype. Demo organizations are fictional. Do not treat metrics as official statistics.
