from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid

from ..database import get_db
from ..config import get_settings
from ..models import Challenge, University, ChallengeStatus, DataProvenance
from ..schemas import (
    ChallengeCreate, ChallengeOut, ChallengeSubmitResponse,
    ValidateChallengeRequest, AIAnalysisOut, UniversityMatchOut,
)
from ..ai import build_full_analysis
from ..ai.rag import rag_engine

router = APIRouter(prefix="/api/challenges", tags=["challenges"])
settings = get_settings()


def _challenge_dict(c: Challenge) -> dict:
    return {
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "district": c.district,
        "location": c.location,
        "status": c.status,
        "domain": c.domain,
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


@router.get("", response_model=list[ChallengeOut])
def list_challenges(
    status: Optional[str] = None,
    domain: Optional[str] = None,
    district: Optional[str] = None,
    provenance: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Challenge)
    if status:
        q = q.filter(Challenge.status == status)
    if domain:
        q = q.filter(Challenge.domain.ilike(f"%{domain}%"))
    if district:
        q = q.filter(Challenge.district.ilike(f"%{district}%"))
    if provenance:
        q = q.filter(Challenge.provenance == provenance)
    return q.order_by(Challenge.created_at.desc()).all()


@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    c = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(404, "Challenge not found")
    return c


@router.post("", response_model=ChallengeSubmitResponse)
async def create_challenge(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    district: str = Form(...),
    community_impact: str = Form(...),
    people_affected: int = Form(...),
    urgency: str = Form("medium"),
    severity: str = Form("medium"),
    geographic_spread: str = Form("local"),
    state: str = Form("Rajasthan"),
    contact_name: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    reporter_id: Optional[int] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo: Optional[UploadFile] = File(None),
    document: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    os.makedirs(settings.upload_dir, exist_ok=True)
    photo_path = None
    document_path = None

    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1] or ".jpg"
        fname = f"photo_{uuid.uuid4().hex}{ext}"
        photo_path = os.path.join(settings.upload_dir, fname)
        with open(photo_path, "wb") as f:
            f.write(await photo.read())

    if document and document.filename:
        ext = os.path.splitext(document.filename)[1] or ".pdf"
        fname = f"doc_{uuid.uuid4().hex}{ext}"
        document_path = os.path.join(settings.upload_dir, fname)
        with open(document_path, "wb") as f:
            f.write(await document.read())

    existing = [
        _challenge_dict(c)
        for c in db.query(Challenge).filter(
            Challenge.status != ChallengeStatus.REJECTED.value
        ).all()
    ]
    universities = [_uni_dict(u) for u in db.query(University).all()]

    analysis = build_full_analysis(
        title=title,
        description=description,
        category=category,
        district=district,
        people_affected=people_affected,
        urgency=urgency,
        severity=severity,
        geographic_spread=geographic_spread,
        existing_challenges=existing,
        universities=universities,
        has_photo=bool(photo_path),
        has_document=bool(document_path),
        has_video=bool(video_url),
    )

    challenge = Challenge(
        title=title,
        description=description,
        category=category,
        location=location,
        district=district,
        state=state,
        community_impact=community_impact,
        people_affected=people_affected,
        urgency=urgency,
        severity=severity,
        geographic_spread=geographic_spread,
        contact_name=contact_name,
        contact_email=contact_email,
        contact_phone=contact_phone,
        video_url=video_url,
        photo_path=photo_path,
        document_path=document_path,
        reporter_id=reporter_id,
        latitude=latitude,
        longitude=longitude,
        status=ChallengeStatus.UNDER_REVIEW.value,
        domain=analysis["domain"],
        subdomain=analysis["subdomain"],
        priority_score=analysis["priority_score"],
        priority_label=analysis["priority"],
        required_expertise=analysis["required_expertise"],
        similar_challenge_ids=[s["id"] for s in analysis["similar_challenges"]],
        ai_analysis={
            k: v for k, v in analysis.items() if k != "university_matches"
        },
        matched_university_id=(
            analysis["university_matches"][0]["university_id"]
            if analysis["university_matches"] else None
        ),
        is_demo=False,
        provenance=DataProvenance.USER.value,
        evidence_score=0.5 if photo_path or document_path else 0.3,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    ai_out = AIAnalysisOut(
        domain=analysis["domain"],
        subdomain=analysis["subdomain"],
        priority=analysis["priority"],
        priority_score=analysis["priority_score"],
        estimated_impact=analysis["estimated_impact"],
        required_expertise=analysis["required_expertise"],
        similar_reports=analysis["similar_reports"],
        recommended_action=analysis["recommended_action"],
        priority_factors=analysis["priority_factors"],
        similar_challenges=analysis["similar_challenges"],
        classification_method=analysis["classification_method"],
        duplicate_method=analysis["duplicate_method"],
        matching_method=analysis["matching_method"],
        disclaimer=analysis["disclaimer"],
    )

    return ChallengeSubmitResponse(
        challenge=challenge,
        ai_analysis=ai_out,
        university_matches=[
            UniversityMatchOut(**m) for m in analysis["university_matches"]
        ],
        data_labels={
            "challenge": "USER-GENERATED (REAL FUNCTIONALITY)",
            "ai": "LOCAL PROTOTYPE AI (not an external LLM)",
            "universities": "DEMO DATA — prototype institutions",
            "rag": "LOCAL RAG retrieval + grounded synthesis",
        },
        rag=rag_engine.suggest_for_challenge(
            challenge.title, challenge.description, challenge.domain or challenge.category
        ),
    )


@router.post("/json", response_model=ChallengeSubmitResponse)
def create_challenge_json(payload: ChallengeCreate, db: Session = Depends(get_db)):
    """JSON alternative for clients that do not upload files."""
    existing = [
        _challenge_dict(c)
        for c in db.query(Challenge).filter(
            Challenge.status != ChallengeStatus.REJECTED.value
        ).all()
    ]
    universities = [_uni_dict(u) for u in db.query(University).all()]
    analysis = build_full_analysis(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        district=payload.district,
        people_affected=payload.people_affected,
        urgency=payload.urgency,
        severity=payload.severity,
        geographic_spread=payload.geographic_spread,
        existing_challenges=existing,
        universities=universities,
        has_video=bool(payload.video_url),
    )
    challenge = Challenge(
        **payload.model_dump(),
        status=ChallengeStatus.UNDER_REVIEW.value,
        domain=analysis["domain"],
        subdomain=analysis["subdomain"],
        priority_score=analysis["priority_score"],
        priority_label=analysis["priority"],
        required_expertise=analysis["required_expertise"],
        similar_challenge_ids=[s["id"] for s in analysis["similar_challenges"]],
        ai_analysis={k: v for k, v in analysis.items() if k != "university_matches"},
        matched_university_id=(
            analysis["university_matches"][0]["university_id"]
            if analysis["university_matches"] else None
        ),
        is_demo=False,
        provenance=DataProvenance.USER.value,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return ChallengeSubmitResponse(
        challenge=challenge,
        ai_analysis=AIAnalysisOut(
            domain=analysis["domain"],
            subdomain=analysis["subdomain"],
            priority=analysis["priority"],
            priority_score=analysis["priority_score"],
            estimated_impact=analysis["estimated_impact"],
            required_expertise=analysis["required_expertise"],
            similar_reports=analysis["similar_reports"],
            recommended_action=analysis["recommended_action"],
            priority_factors=analysis["priority_factors"],
            similar_challenges=analysis["similar_challenges"],
            classification_method=analysis["classification_method"],
            duplicate_method=analysis["duplicate_method"],
            matching_method=analysis["matching_method"],
            disclaimer=analysis["disclaimer"],
        ),
        university_matches=[UniversityMatchOut(**m) for m in analysis["university_matches"]],
        data_labels={
            "challenge": "USER-GENERATED (REAL FUNCTIONALITY)",
            "ai": "LOCAL PROTOTYPE AI (not an external LLM)",
            "universities": "DEMO DATA — prototype institutions",
            "rag": "LOCAL RAG retrieval + grounded synthesis",
        },
        rag=rag_engine.suggest_for_challenge(
            challenge.title, challenge.description, challenge.domain or challenge.category
        ),
    )


@router.post("/{challenge_id}/validate", response_model=ChallengeOut)
def validate_challenge(
    challenge_id: int,
    body: ValidateChallengeRequest,
    db: Session = Depends(get_db),
):
    c = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(404, "Challenge not found")

    if body.action == "validate":
        c.status = ChallengeStatus.VALIDATED.value
        if c.matched_university_id:
            c.status = ChallengeStatus.MATCHED.value
    elif body.action == "reject":
        c.status = ChallengeStatus.REJECTED.value
    elif body.action == "consolidate":
        if not body.consolidate_into_id:
            raise HTTPException(400, "consolidate_into_id required")
        target = db.query(Challenge).filter(Challenge.id == body.consolidate_into_id).first()
        if not target:
            raise HTTPException(404, "Target challenge not found")
        c.status = ChallengeStatus.CONSOLIDATED.value
        c.consolidated_into_id = target.id
        # bump people affected on target as consolidation effect
        target.people_affected = (target.people_affected or 0) + (c.people_affected or 0)
    else:
        raise HTTPException(400, "Unknown action")

    db.commit()
    db.refresh(c)
    return c


@router.get("/{challenge_id}/reanalyze")
def reanalyze(challenge_id: int, db: Session = Depends(get_db)):
    c = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(404, "Challenge not found")
    existing = [
        _challenge_dict(x)
        for x in db.query(Challenge).filter(Challenge.id != c.id).all()
    ]
    universities = [_uni_dict(u) for u in db.query(University).all()]
    analysis = build_full_analysis(
        title=c.title,
        description=c.description,
        category=c.category,
        district=c.district,
        people_affected=c.people_affected,
        urgency=c.urgency,
        severity=c.severity,
        geographic_spread=c.geographic_spread,
        existing_challenges=existing,
        universities=universities,
        has_photo=bool(c.photo_path),
        has_document=bool(c.document_path),
        has_video=bool(c.video_url),
    )
    return {
        "ai_analysis": analysis,
        "university_matches": analysis["university_matches"],
        "rag": rag_engine.suggest_for_challenge(
            c.title, c.description, c.domain or c.category
        ),
        "data_labels": {
            "ai": "LOCAL PROTOTYPE AI (not an external LLM)",
            "universities": "DEMO DATA",
            "rag": "LOCAL RAG retrieval + grounded synthesis",
        },
    }
