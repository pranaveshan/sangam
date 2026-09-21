"""Light auth helpers and rate limiting for demo endpoints."""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Optional

from fastapi import Header, HTTPException, Request
from sqlalchemy.orm import Session

from .models import User

_RATE: dict[str, list[float]] = defaultdict(list)


def enforce_rate_limit(request: Request, limit: int = 20, window_seconds: int = 60) -> None:
    client = request.client.host if request.client else "unknown"
    key = f"{client}:{request.url.path}"
    now = time.time()
    hits = [t for t in _RATE[key] if now - t < window_seconds]
    if len(hits) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")
    hits.append(now)
    _RATE[key] = hits


def parse_demo_token(
    authorization: Optional[str] = None,
    token: Optional[str] = None,
) -> Optional[str]:
    raw = token
    if authorization and authorization.lower().startswith("bearer "):
        raw = authorization.split(" ", 1)[1].strip()
    return raw


def require_demo_token(
    authorization: Optional[str] = Header(None),
    x_sangam_token: Optional[str] = Header(None, alias="X-Sangam-Token"),
) -> str:
    raw = parse_demo_token(authorization, x_sangam_token)
    if not raw or not raw.startswith("sangam-demo-"):
        raise HTTPException(401, "Demo authentication required for this action.")
    return raw


def user_from_token(db: Session, token: str) -> Optional[User]:
    parts = token.split("-")
    if len(parts) < 4:
        return None
    try:
        uid = int(parts[-1])
    except ValueError:
        return None
    return db.query(User).filter(User.id == uid).first()
