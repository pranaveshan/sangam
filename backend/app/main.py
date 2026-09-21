"""
SANGAM FastAPI application entrypoint.
SIH26043 — Crowdsourced societal challenges + university/industry collaboration.
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import get_settings
from .database import Base, engine, SessionLocal
from .seed import seed_database
from .routers import challenges, projects, admin, rag, auth, problems
from .ai.rag import rag_engine
from .models import Challenge, Project, University

settings = get_settings()

# Built React app (production). Prefer backend/static, then ../frontend/dist
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if not STATIC_DIR.exists():
    alt = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if alt.exists():
        STATIC_DIR = alt


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.upload_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        challenge_rows = [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "domain": c.domain,
                "category": c.category,
                "district": c.district,
                "status": c.status,
                "community_impact": c.community_impact,
                "required_expertise": c.required_expertise,
                "is_demo": c.is_demo,
            }
            for c in db.query(Challenge).all()
        ]
        project_rows = [
            {
                "id": p.id,
                "name": p.name,
                "goal": p.goal,
                "proposal": p.proposal,
                "status": p.status,
                "team_name": p.team_name,
                "match_explanation": p.match_explanation,
                "is_demo": p.is_demo,
            }
            for p in db.query(Project).all()
        ]
        university_rows = [
            {
                "id": u.id,
                "name": u.name,
                "departments": u.departments,
                "research_areas": u.research_areas,
                "faculty_expertise": u.faculty_expertise,
                "laboratory_capabilities": u.laboratory_capabilities,
                "domains": u.domains,
                "provenance": u.provenance,
            }
            for u in db.query(University).all()
        ]
        rag_engine.upsert_live_corpus(challenge_rows, project_rows, university_rows)
    finally:
        db.close()
    yield


app = FastAPI(
    title="SANGAM",
    description=(
        "Smart India Hackathon 2026 — SIH26043 prototype.\n\n"
        "**Data labels:** DEMO DATA = seeded for demo; USER = real submissions; "
        "AI/RAG = local keyword/TF-IDF retrieval + grounded synthesis "
        "(optional OpenAI generation if OPENAI_API_KEY is set)."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

def _cors_middleware_kwargs() -> dict:
    """Never pair allow_origins=['*'] with allow_credentials=True."""
    origins = settings.origins
    if not origins:
        origins = ["http://localhost:5180", "http://127.0.0.1:5180"]
    if origins == ["*"]:
        return {
            "allow_origins": ["*"],
            "allow_credentials": False,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    return {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


app.add_middleware(CORSMiddleware, **_cors_middleware_kwargs())

app.include_router(challenges.router)
app.include_router(projects.router)
app.include_router(admin.router)
app.include_router(rag.router)
app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(problems.speech_router)

if os.path.isdir(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "data_mode": settings.data_mode,
        "ai": "local_heuristic LLMService + hashing embeddings + optional Web Speech client STT",
        "rag": {
            "documents_indexed": len(rag_engine.docs),
            "chunks_indexed": len(rag_engine.index.chunks),
            "retrieval": "local_tfidf_cosine",
            "generation": "local_grounded_synthesis (OpenAI optional)",
        },
        "database": "sqlite" if settings.database_url.startswith("sqlite") else "postgresql",
        "frontend": STATIC_DIR.exists(),
        "labels": {
            "REAL_FUNCTIONALITY": "CRUD, AI analysis, RAG retrieval, matching, lifecycle, feedback",
            "DEMO_DATA": "Seeded universities, partners, AquaGuard journey, knowledge playbooks",
            "FUTURE_INTEGRATION": "External embedding models, PostGIS live maps, payments",
        },
    }


# Serve SPA assets + client-side routes when frontend build is present
if STATIC_DIR.exists():
    assets = STATIC_DIR / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

    @app.get("/")
    def spa_index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        # Do not swallow API/docs/uploads
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json", "uploads/")):
            return {"detail": "Not found"}
        candidate = STATIC_DIR / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "message": "SANGAM API — build frontend to serve the full website",
            "docs": "/docs",
            "health": "/api/health",
        }
