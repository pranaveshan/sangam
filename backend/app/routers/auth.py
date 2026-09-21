"""
SANGAM demo authentication — separate portals per role.

NOT production auth. Passwords are demo credentials for SIH judging.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Demo passwords (prototype only). Emails match seeded users.
DEMO_CREDENTIALS = {
    "citizen.demo@sangam.local": "citizen123",
    "gov.demo@sangam.local": "admin123",
    "uni.demo@sangam.local": "uni123",
    "student.demo@sangam.local": "student123",
    "industry.demo@sangam.local": "csr123",
}

PORTALS = [
    {
        "id": "citizen",
        "slug": "citizen",
        "title": "Citizen Portal",
        "subtitle": "Report societal challenges & give community feedback",
        "role": "citizen",
        "color": "#1d4ed8",
        "demo_email": "citizen.demo@sangam.local",
        "demo_password": "citizen123",
        "home_path": "/dashboard",
    },
    {
        "id": "government",
        "slug": "admin",
        "title": "Admin / Government Portal",
        "subtitle": "Validate challenges, monitor districts & impact",
        "role": "government",
        "color": "#a16207",
        "demo_email": "gov.demo@sangam.local",
        "demo_password": "admin123",
        "home_path": "/dashboard",
    },
    {
        "id": "university",
        "slug": "university",
        "title": "University Portal",
        "subtitle": "Accept matched challenges & mentor innovation projects",
        "role": "university",
        "color": "#0f766e",
        "demo_email": "uni.demo@sangam.local",
        "demo_password": "uni123",
        "home_path": "/dashboard",
    },
    {
        "id": "student",
        "slug": "ssc",
        "title": "Student / SSC Portal",
        "subtitle": "Student & Scholar Cell — teams, milestones, prototypes",
        "role": "student",
        "color": "#047857",
        "demo_email": "student.demo@sangam.local",
        "demo_password": "student123",
        "home_path": "/dashboard",
    },
    {
        "id": "industry",
        "slug": "csr",
        "title": "Industry / CSR Portal",
        "subtitle": "Offer mentorship, technology & non-financial sponsorship",
        "role": "industry",
        "color": "#334155",
        "demo_email": "industry.demo@sangam.local",
        "demo_password": "csr123",
        "home_path": "/dashboard",
    },
]


class LoginRequest(BaseModel):
    email: str
    password: str
    portal: str | None = Field(
        default=None,
        description="Optional portal slug/role to enforce (citizen|admin|university|ssc|csr)",
    )


class LoginResponse(BaseModel):
    ok: bool
    token: str
    user: dict
    portal: dict
    data_label: str = "DEMO AUTH — prototype credentials, not production security"


def _portal_for_role(role: str) -> dict:
    for p in PORTALS:
        if p["role"] == role or p["slug"] == role or p["id"] == role:
            return p
    raise HTTPException(400, f"Unknown portal/role: {role}")


def _portal_from_request(portal: str | None, role: str) -> dict:
    if not portal:
        return _portal_for_role(role)
    key = portal.lower().strip()
    for p in PORTALS:
        if key in (p["slug"], p["id"], p["role"]):
            return p
    raise HTTPException(400, f"Unknown portal: {portal}")


@router.get("/portals")
def list_portals():
    return {
        "portals": [
            {k: v for k, v in p.items()}
            for p in PORTALS
        ],
        "note": "DEMO AUTH — separate login portals for SIH demonstration",
    }


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    password = body.password

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "Invalid email or password")

    expected = DEMO_CREDENTIALS.get(user.email)
    if expected is None or password != expected:
        raise HTTPException(401, "Invalid email or password")

    portal = _portal_from_request(body.portal, user.role)
    if portal["role"] != user.role:
        raise HTTPException(
            403,
            f"This account belongs to the {user.role} portal. Use /login/{portal_slug_for_role(user.role)} instead.",
        )

    # Prototype token (not JWT crypto) — sufficient for demo session labeling
    token = f"sangam-demo-{user.role}-{user.id}"

    return LoginResponse(
        ok=True,
        token=token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "organization": user.organization,
            "district": user.district,
            "is_demo": user.is_demo,
        },
        portal={
            "id": portal["id"],
            "slug": portal["slug"],
            "title": portal["title"],
            "color": portal["color"],
            "home_path": portal["home_path"],
        },
    )


def portal_slug_for_role(role: str) -> str:
    return _portal_for_role(role)["slug"]


@router.get("/me")
def me(token: str, db: Session = Depends(get_db)):
    """Resolve demo token → user. Format: sangam-demo-{role}-{id}"""
    try:
        parts = token.split("-")
        user_id = int(parts[-1])
    except Exception as exc:
        raise HTTPException(401, "Invalid token") from exc
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "User not found")
    portal = _portal_for_role(user.role)
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "organization": user.organization,
            "district": user.district,
            "is_demo": user.is_demo,
        },
        "portal": {
            "id": portal["id"],
            "slug": portal["slug"],
            "title": portal["title"],
            "color": portal["color"],
            "home_path": portal["home_path"],
        },
    }
