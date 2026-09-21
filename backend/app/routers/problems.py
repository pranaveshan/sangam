"""Problem intelligence + citizen submission API (voice-first pipeline)."""
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import get_settings
from ..models import Challenge, University, ChallengeStatus, DataProvenance
from ..ai.llm_service import llm_service
from ..ai.embedding_service import embedding_service
from ..ai.speech_service import speech_service
from ..security import enforce_rate_limit

router = APIRouter(prefix="/api/problems", tags=["problems"])
settings = get_settings()


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    language: str = "en"
    location_text: Optional[str] = None
    people_affected_text: Optional[str] = None
    has_photo: bool = False
    has_video: bool = False
    has_document: bool = False


class ProblemIntelligence(BaseModel):
    problem_title: str = ""
    summary: str = ""
    category: str = ""
    subcategory: str = ""
    severity: str = ""
    urgency: str = ""
    affected_population: str = ""
    location: dict[str, Any] = Field(default_factory=dict)
    required_expertise: list[str] = Field(default_factory=list)
    required_technologies: list[str] = Field(default_factory=list)
    possible_root_causes: list[str] = Field(default_factory=list)
    environmental_impact: str = ""
    social_impact: str = ""
    sdg_alignment: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    evidence_required: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    confidence: float = 0.0


def _validate_intelligence(data: dict[str, Any]) -> dict[str, Any]:
    """Validate / coerce LLM output via Pydantic — never trust raw dicts."""
    allowed = set(ProblemIntelligence.model_fields.keys())
    # keep explainability extras
    extras = {
        k: data.get(k)
        for k in (
            "what_we_understood", "why_we_think_this", "what_you_can_correct",
            "provider", "disclaimer", "language", "original_text_preserved",
            "priority_score", "priority_label", "affected_population_estimate",
        )
        if k in data
    }
    core = {k: data.get(k) for k in allowed}
    validated = ProblemIntelligence.model_validate(core).model_dump()
    return {**validated, **extras}


def _challenge_public(c: Challenge) -> dict:
    return {
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "category": c.category,
        "domain": c.domain,
        "location": c.location,
        "district": c.district,
        "status": c.status,
        "required_expertise": c.required_expertise or [],
        "is_demo": c.is_demo,
        "provenance": c.provenance,
        "people_affected": c.people_affected,
        "ai_analysis": c.ai_analysis,
        "photo_path": c.photo_path,
        "submitted_with_assistance": bool((c.ai_analysis or {}).get("submitted_with_assistance")),
        "language": (c.ai_analysis or {}).get("language"),
        "cluster_id": (c.ai_analysis or {}).get("cluster_id"),
    }


def _uni_dict(u: University) -> dict:
    return {
        "id": u.id,
        "name": u.name,
        "short_name": u.short_name,
        "state": u.state,
        "district": u.district,
        "departments": u.departments or [],
        "research_areas": u.research_areas or [],
        "faculty_expertise": u.faculty_expertise or [],
        "laboratory_capabilities": u.laboratory_capabilities or [],
        "student_skills": u.student_skills or [],
        "incubation_facilities": u.incubation_facilities or [],
        "domains": u.domains or [],
        "is_demo": u.is_demo,
        "provenance": u.provenance,
    }


@router.post("/analyze")
def analyze_problem(body: AnalyzeRequest, request: Request):
    enforce_rate_limit(request, limit=40, window_seconds=60)
    try:
        raw = llm_service.analyze_problem(
            body.text,
            language=body.language,
            location_text=body.location_text,
            people_affected_text=body.people_affected_text,
            has_photo=body.has_photo,
            has_video=body.has_video,
            has_document=body.has_document,
        )
        return _validate_intelligence(raw)
    except Exception as exc:  # noqa: BLE001
        # Honest failure — do not fake analysis
        raise HTTPException(
            status_code=503,
            detail=(
                "AI analysis is temporarily unavailable. "
                "Your report can still be saved and processed later."
            ),
        ) from exc


@router.post("")
async def create_problem(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form("Community"),
    location: str = Form("Not specified"),
    district: str = Form("Unknown"),
    community_impact: str = Form("To be assessed"),
    people_affected: int = Form(0),
    urgency: str = Form("medium"),
    severity: str = Form("medium"),
    language: str = Form("en"),
    original_transcript: str = Form(""),
    submitted_with_assistance: str = Form("false"),
    citizen_consent: str = Form("true"),
    intelligence_json: Optional[str] = Form(None),
    reporter_id: Optional[int] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    enforce_rate_limit(request, limit=30, window_seconds=60)

    assisted = submitted_with_assistance.lower() in ("1", "true", "yes")
    consent = citizen_consent.lower() in ("1", "true", "yes")
    if assisted and not consent:
        raise HTTPException(400, "Citizen consent is required for assisted reporting.")

    # Validate uploads
    photo_path = None
    if photo and photo.filename:
        allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".webm", ".mov"}
        ext = os.path.splitext(photo.filename)[1].lower() or ".jpg"
        if ext not in allowed:
            raise HTTPException(400, "Unsupported file type.")
        content = await photo.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(400, "File too large (max 15MB).")
        os.makedirs(settings.upload_dir, exist_ok=True)
        fname = f"evidence_{uuid.uuid4().hex}{ext}"
        photo_path = os.path.join(settings.upload_dir, fname)
        with open(photo_path, "wb") as f:
            f.write(content)

    intelligence: dict[str, Any] = {}
    if intelligence_json:
        try:
            intelligence = _validate_intelligence(json.loads(intelligence_json))
        except Exception:  # noqa: BLE001
            intelligence = {}

    if not intelligence:
        try:
            intelligence = _validate_intelligence(
                llm_service.analyze_problem(
                    original_transcript or description,
                    language=language,
                    location_text=location,
                    has_photo=bool(photo_path),
                )
            )
        except Exception:  # noqa: BLE001
            intelligence = {
                "problem_title": title,
                "summary": description,
                "missing_information": ["AI analysis unavailable at submit time"],
                "confidence": 0,
                "ai_unavailable": True,
            }

    emb = embedding_service.embed(f"{title} {description} {location}")

    existing = db.query(Challenge).all()
    candidates = [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "location": c.location,
            "district": c.district,
            "status": c.status,
            "domain": c.domain,
            "embedding": (c.ai_analysis or {}).get("embedding"),
        }
        for c in existing
        if c.status != ChallengeStatus.REJECTED.value
    ]
    similar_raw = embedding_service.find_similar(
        f"{title} {description} {location}", candidates, threshold=0.32
    )
    similar = []
    for s in similar_raw:
        other = next((c for c in existing if c.id == s["id"]), None)
        if not other:
            continue
        cmp = llm_service.compare_problems(
            {"title": title, "description": description, "district": district},
            {"title": other.title, "description": other.description, "district": other.district},
        )
        similar.append({**s, **cmp})

    # Cluster: attach to highest "same/related" if confident
    cluster_id = None
    for s in similar:
        if s.get("relation") in ("same", "related") and s.get("similarity", 0) >= 50:
            cluster_id = s["id"]
            break

    universities = [_uni_dict(u) for u in db.query(University).all()]
    matches = match_from_db(
        intelligence.get("category") or category,
        intelligence.get("subcategory") or "",
        intelligence.get("required_expertise") or [],
        district,
        universities,
        intelligence,
    )

    analysis_blob = {
        **intelligence,
        "embedding": emb,
        "similar": similar,
        "matches": matches,
        "submitted_with_assistance": assisted,
        "citizen_consent": consent,
        "language": language,
        "original_transcript": original_transcript or description,
        "cluster_id": cluster_id,
        "reporting_mode": "assisted" if assisted else "citizen",
    }

    challenge = Challenge(
        title=title[:400],
        description=description,
        category=category[:120],
        location=location[:300],
        district=district[:120],
        state="India",
        latitude=latitude,
        longitude=longitude,
        community_impact=community_impact,
        people_affected=people_affected or intelligence.get("affected_population_estimate") or 0,
        urgency=urgency,
        severity=severity,
        photo_path=photo_path,
        status=ChallengeStatus.UNDER_REVIEW.value if intelligence.get("confidence", 0) >= 0.4 else ChallengeStatus.SUBMITTED.value,
        domain=intelligence.get("category") or category,
        subdomain=intelligence.get("subcategory"),
        priority_score=intelligence.get("priority_score"),
        priority_label=intelligence.get("priority_label"),
        ai_analysis=analysis_blob,
        required_expertise=intelligence.get("required_expertise") or [],
        similar_challenge_ids=[s["id"] for s in similar],
        consolidated_into_id=cluster_id if similar and similar[0].get("relation") == "same" else None,
        matched_university_id=matches[0]["university_id"] if matches else None,
        reporter_id=reporter_id,
        is_demo=False,
        provenance=DataProvenance.USER.value,
        evidence_score=0.5 if photo_path else 0.3,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return {
        "id": challenge.id,
        "challenge": _challenge_public(challenge),
        "intelligence": intelligence,
        "similar": similar,
        "matches": matches,
        "cluster_id": cluster_id,
        "submitted_with_assistance": assisted,
        "data_labels": {
            "challenge": "USER",
            "matches": "DEMO DATA" if matches and matches[0].get("is_demo") else "VERIFIED",
        },
    }


def match_from_db(domain, subdomain, expertise, district, universities, intelligence):
    from ..ai.engine import match_universities

    matches = match_universities(domain, subdomain, expertise, district, universities)
    for m in matches:
        m["explanation"] = llm_service.explain_match(m, intelligence or {"required_expertise": expertise})
    return matches


@router.post("/{problem_id}/similar")
def similar_problems(problem_id: int, db: Session = Depends(get_db)):
    c = db.query(Challenge).filter(Challenge.id == problem_id).first()
    if not c:
        raise HTTPException(404, "Problem not found")
    existing = [
        {
            "id": x.id,
            "title": x.title,
            "description": x.description,
            "location": x.location,
            "district": x.district,
            "status": x.status,
            "domain": x.domain,
            "embedding": (x.ai_analysis or {}).get("embedding"),
        }
        for x in db.query(Challenge).filter(Challenge.id != problem_id).all()
    ]
    similar_raw = embedding_service.find_similar(
        f"{c.title} {c.description} {c.location}", existing
    )
    out = []
    for s in similar_raw:
        other = next((x for x in existing if x["id"] == s["id"]), None)
        cmp = llm_service.compare_problems(
            {"title": c.title, "description": c.description, "district": c.district},
            other or {},
        )
        out.append({**s, **cmp})
    return {"problem_id": problem_id, "similar": out}


@router.post("/{problem_id}/match")
def match_problem(problem_id: int, db: Session = Depends(get_db)):
    c = db.query(Challenge).filter(Challenge.id == problem_id).first()
    if not c:
        raise HTTPException(404, "Problem not found")
    intelligence = c.ai_analysis or {}
    universities = [_uni_dict(u) for u in db.query(University).all()]
    matches = match_from_db(
        c.domain or c.category,
        c.subdomain or "",
        c.required_expertise or intelligence.get("required_expertise") or [],
        c.district,
        universities,
        intelligence,
    )
    return {"problem_id": problem_id, "matches": matches}


@router.get("/{problem_id}/intelligence")
def get_intelligence(problem_id: int, db: Session = Depends(get_db)):
    c = db.query(Challenge).filter(Challenge.id == problem_id).first()
    if not c:
        raise HTTPException(404, "Problem not found")
    return {
        "problem_id": problem_id,
        "intelligence": c.ai_analysis or {},
        "required_expertise": c.required_expertise or [],
        "similar_challenge_ids": c.similar_challenge_ids or [],
        "matched_university_id": c.matched_university_id,
        "status": c.status,
    }


# Speech endpoint under /api/speech for clarity
speech_router = APIRouter(prefix="/api/speech", tags=["speech"])


@speech_router.post("/transcribe")
async def transcribe(
    request: Request,
    client_transcript: Optional[str] = Form(None),
    language_hint: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
):
    enforce_rate_limit(request, limit=40, window_seconds=60)
    audio_bytes = await audio.read() if audio and audio.filename else None
    return speech_service.transcribe(
        client_transcript=client_transcript,
        language_hint=language_hint,
        audio_bytes=audio_bytes,
        filename=audio.filename if audio else None,
    )
