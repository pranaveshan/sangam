# SANGAM — Developer Reference

Companion to the root [README](../README.md). README = quick start. This file = technical detail.

## Architecture

| Layer | Tech | Default URL |
|-------|------|-------------|
| Frontend | React 18, Vite, Tailwind, HashRouter | http://localhost:5180 |
| Backend | FastAPI, SQLAlchemy, Pydantic | http://localhost:8100 |
| Database | SQLite (`backend/sangam.db`) | file on disk |
| AI | Local `LLMService` / embeddings / speech abstractions | no API key required |

Optional PostgreSQL via `DATABASE_URL`. The live ORM does **not** require PostGIS. `database/schema.sql` is a legacy PostGIS sketch and is not applied by the app.

## Environment

| File | Purpose |
|------|---------|
| `backend/.env.example` | Template — copied to `backend/.env` by setup |
| `frontend/.env.example` | `VITE_API_URL` for Vite |

Variables actually read by the backend (`app/config.py`):

- `DATABASE_URL`
- `UPLOAD_DIR`
- `CORS_ORIGINS` (comma-separated; never use `*` with credentialed mode)
- `DATA_MODE`
- Optional: `OPENAI_API_KEY`, `OPENAI_MODEL` (RAG generation only)

## Backend

Package root: `backend/` with import path `app.*`.

```bash
cd backend
.venv/Scripts/activate   # Windows
# source .venv/bin/activate  # Unix
uvicorn app.main:app --reload --host 127.0.0.1 --port 8100
```

Key modules:

- `app/main.py` — FastAPI entry, lifespan seed, CORS, static SPA
- `app/models.py` — SQLAlchemy models
- `app/seed.py` — demo users, universities, AquaGuard journey
- `app/ai/` — engine, llm_service, embedding_service, speech_service, rag
- `app/routers/` — challenges, problems, projects, auth, admin, rag

### Database initialization

Canonical methods (same seed):

1. **API lifespan** — `create_all` + `seed_database` on startup  
2. **Script** — `backend/scripts/init_db.py`

```bash
# from repository root
backend/.venv/Scripts/python.exe backend/scripts/init_db.py
```

There is no Alembic migration pipeline in this prototype. Schema is created from models.

## Frontend

```bash
cd frontend
npm install
npm run dev      # port 5180, proxies /api → :8100
npm run build    # output: frontend/dist
```

Vite defaults (`vite.config.js`):

- `server.port = 5180`
- proxy `/api` and `/uploads` → `http://localhost:8100`
- `base: './'` for static hosting

## Ports (authoritative)

| Service | Port |
|---------|------|
| Frontend (Vite) | **5180** |
| Backend (uvicorn) | **8100** |

Do not use 5173 / 8000 unless you intentionally change config and CORS together.

## CORS

`CORS_ORIGINS` lists allowed browser origins. Credentials are enabled only when origins are explicit (not `*`).

## Scripts

| Script | Role |
|--------|------|
| `setup.bat` / `setup.sh` | Create `.venv`, pip install, npm install, `.env`, init_db |
| `start.bat` / `start.sh` | Start API + Vite (runs setup if missing) |
| `deploy-local.bat` | Build frontend → `backend/static` → serve on :8100 |

## AI services

Honest local defaults:

- Problem intelligence — keyword / heuristic structured output
- Similarity — hashing / bag-of-words embeddings
- Speech — client Web Speech transcript accepted server-side
- RAG — TF-IDF; optional OpenAI for answer wording

## Testing

```bash
# Health
curl http://localhost:8100/api/health

# Analyze
curl -X POST http://localhost:8100/api/problems/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Flooding damages farmland after rain\",\"location_text\":\"Village\",\"people_affected_text\":\"40\"}"
```

Manual UI checklist: `docs/TESTING.md`.

## Build & deployment

**Local production (API + SPA):**

```bat
deploy-local.bat
```

Open http://localhost:8100

**Docker:** multi-stage `Dockerfile` builds frontend into `static/` and runs uvicorn on 8100.

**Render:** `render.yaml` (SQLite on free tier — ephemeral disk).

`website/` is **generated** by deploy-local and gitignored. Root `index.html` is only a helper page for humans opening the repo folder — not the React app.

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| ImportError `app.database.connection` | Obsolete docs/scripts — use current `init_db.py` |
| PostGIS errors | You are following obsolete DEVELOPMENT instructions; use SQLite |
| Blank page on static host | Ensure `base: './'` build and HashRouter routes (`/#/...`) |
| CORS errors | Align `CORS_ORIGINS` with the exact frontend origin including port |
| Setup fails on Python | Use `python -m venv`; ensure Python 3.10+ |

## Project layout

```text
sangam/
  backend/app/
  backend/scripts/init_db.py
  frontend/src/
  docs/
  setup.bat  setup.sh
  start.bat  start.sh
  deploy-local.bat
```
