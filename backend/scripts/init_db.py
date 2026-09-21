"""
Initialize SANGAM database tables and demo seed data.

Uses the current application architecture:
  - app.database (engine, SessionLocal, Base)
  - app.models (SQLAlchemy models)
  - app.seed.seed_database

Default database is SQLite (see backend/.env.example).
PostgreSQL is optional via DATABASE_URL — PostGIS is NOT required.

Run from repository root:
  backend\\.venv\\Scripts\\python.exe backend\\scripts\\init_db.py

Or from backend/ with venv active:
  python scripts/init_db.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure backend/ is on sys.path whether launched from repo root or backend/
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app import models  # noqa: E402, F401  — register models on Base.metadata
from app.seed import seed_database  # noqa: E402


def main() -> int:
    print("Initializing SANGAM database...")
    print(f"  Backend dir: {BACKEND_DIR}")
    print(f"  Engine: {engine.url}")

    Base.metadata.create_all(bind=engine)
    print("Tables created (SQLAlchemy metadata).")

    db = SessionLocal()
    try:
        seed_database(db, force=False)
        print("Demo seed applied (skipped if already present).")
        print("Database ready.")
        print()
        print("Start the API with:")
        print("  uvicorn app.main:app --reload --host 127.0.0.1 --port 8100")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Database initialization failed: {exc}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
