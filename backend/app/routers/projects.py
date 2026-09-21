from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import (
    Challenge, Project, Milestone, IndustryCollaboration, IndustryPartner,
    CommunityFeedback, University, ChallengeStatus, DataProvenance,
)
from ..schemas import (
    AcceptChallengeRequest, TeamUpdateRequest, MilestoneCreate, MilestoneUpdate,
    CollaborationCreate, FeedbackCreate, ProjectStatusUpdate, ProjectOut,
)
from ..seed import ensure_default_milestones, DEFAULT_MILESTONES
from ..serializers import serialize_project

router = APIRouter(prefix="/api/projects", tags=["projects"])

LIFECYCLE = [
    "submitted", "under_review", "validated", "matched", "university_accepted",
    "team_formed", "industry_collaboration", "prototype", "testing", "pilot", "completed",
]


class PlanApproveBody(BaseModel):
    proposal: Optional[str] = None


class FeedbackAnalyzeBody(BaseModel):
    feedback: Optional[str] = None
    rating: Optional[int] = None
    problem_improvement: Optional[str] = None


@router.get("", response_model=list[ProjectOut])
def list_projects(
    university_id: Optional[int] = None,
    status: Optional[str] = None,
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Project).options(
        joinedload(Project.milestones),
        joinedload(Project.collaborations).joinedload(IndustryCollaboration.partner),
        joinedload(Project.feedback),
        joinedload(Project.challenge),
        joinedload(Project.university),
    )
    if university_id:
        q = q.filter(Project.university_id == university_id)
    if status:
        q = q.filter(Project.status == status)
    projects = q.order_by(Project.created_at.desc()).all()
    if domain:
        projects = [p for p in projects if p.challenge and domain.lower() in (p.challenge.domain or "").lower()]
    return [serialize_project(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = (
        db.query(Project)
        .options(
            joinedload(Project.milestones),
            joinedload(Project.collaborations).joinedload(IndustryCollaboration.partner),
            joinedload(Project.feedback),
            joinedload(Project.challenge),
            joinedload(Project.university),
        )
        .filter(Project.id == project_id)
        .first()
    )
    if not p:
        raise HTTPException(404, "Project not found")
    return serialize_project(p)


@router.post("/from-challenge/{challenge_id}", response_model=ProjectOut)
def accept_from_challenge(
    challenge_id: int,
    body: AcceptChallengeRequest,
    db: Session = Depends(get_db),
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(404, "Challenge not found")
    existing = db.query(Project).filter(Project.challenge_id == challenge_id).first()
    if existing:
        raise HTTPException(400, "Project already exists for this challenge")

    uni = db.query(University).filter(University.id == body.university_id).first()
    if not uni:
        raise HTTPException(404, "University not found")

    project = Project(
        name=body.project_name,
        goal=body.goal,
        challenge_id=challenge.id,
        university_id=body.university_id,
        status=ChallengeStatus.UNIVERSITY_ACCEPTED.value,
        proposal=body.proposal,
        match_explanation=body.match_explanation or (
            f"Matched because the institution has relevant expertise for {challenge.domain}."
        ),
        match_score=body.match_score,
        is_demo=False,
        provenance=DataProvenance.USER.value,
    )
    db.add(project)
    challenge.status = ChallengeStatus.UNIVERSITY_ACCEPTED.value
    challenge.matched_university_id = body.university_id
    db.commit()
    db.refresh(project)
    ensure_default_milestones(db, project.id)

    p = (
        db.query(Project)
        .options(
            joinedload(Project.milestones),
            joinedload(Project.collaborations).joinedload(IndustryCollaboration.partner),
            joinedload(Project.feedback),
            joinedload(Project.challenge),
            joinedload(Project.university),
        )
        .filter(Project.id == project.id)
        .first()
    )
    return serialize_project(p)


@router.put("/{project_id}/team", response_model=ProjectOut)
def update_team(project_id: int, body: TeamUpdateRequest, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    p.team_name = body.team_name
    p.team_members = body.team_members
    p.faculty_mentors = body.faculty_mentors
    p.status = ChallengeStatus.TEAM_FORMED.value
    if p.challenge:
        p.challenge.status = ChallengeStatus.TEAM_FORMED.value
    db.commit()
    return get_project(project_id, db)


@router.post("/{project_id}/milestones", response_model=ProjectOut)
def add_milestone(project_id: int, body: MilestoneCreate, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    db.add(Milestone(
        project_id=project_id,
        title=body.title,
        description=body.description,
        order_index=body.order_index,
        status="pending",
    ))
    db.commit()
    return get_project(project_id, db)


@router.patch("/{project_id}/milestones/{milestone_id}", response_model=ProjectOut)
def update_milestone(
    project_id: int,
    milestone_id: int,
    body: MilestoneUpdate,
    db: Session = Depends(get_db),
):
    m = (
        db.query(Milestone)
        .filter(Milestone.id == milestone_id, Milestone.project_id == project_id)
        .first()
    )
    if not m:
        raise HTTPException(404, "Milestone not found")
    m.status = body.status
    if body.description is not None:
        m.description = body.description
    if body.status == "completed":
        m.completed_at = datetime.utcnow()
        # Auto-advance project status based on milestone progress
        _maybe_advance_from_milestones(db, project_id)
    elif body.status != "completed":
        m.completed_at = None
    db.commit()
    return get_project(project_id, db)


def _maybe_advance_from_milestones(db: Session, project_id: int) -> None:
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        return
    milestones = (
        db.query(Milestone)
        .filter(Milestone.project_id == project_id)
        .order_by(Milestone.order_index)
        .all()
    )
    completed = {m.title for m in milestones if m.status == "completed"}
    mapping = [
        ("Prototype Development", ChallengeStatus.PROTOTYPE.value),
        ("Field Testing", ChallengeStatus.TESTING.value),
        ("Pilot Deployment", ChallengeStatus.PILOT.value),
    ]
    for title, status in mapping:
        if title in completed:
            p.status = status
            if p.challenge:
                p.challenge.status = status


@router.put("/{project_id}/status", response_model=ProjectOut)
def update_status(project_id: int, body: ProjectStatusUpdate, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    if body.status not in LIFECYCLE and body.status != "rejected":
        raise HTTPException(400, f"Invalid status. Allowed: {LIFECYCLE}")
    p.status = body.status
    if p.challenge:
        p.challenge.status = body.status
    if body.people_impacted is not None:
        p.people_impacted = body.people_impacted
    if body.communities_reached is not None:
        p.communities_reached = body.communities_reached
    if body.pilot_location is not None:
        p.pilot_location = body.pilot_location
    if body.pilot_notes is not None:
        p.pilot_notes = body.pilot_notes
    if body.proposal is not None:
        p.proposal = body.proposal
    db.commit()
    return get_project(project_id, db)


@router.post("/{project_id}/collaborations", response_model=ProjectOut)
def add_collaboration(
    project_id: int, body: CollaborationCreate, db: Session = Depends(get_db)
):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    partner = db.query(IndustryPartner).filter(IndustryPartner.id == body.partner_id).first()
    if not partner:
        raise HTTPException(404, "Partner not found")

    collab = IndustryCollaboration(
        project_id=project_id,
        partner_id=body.partner_id,
        support_type=body.support_type,
        details=body.details or f"{partner.name} offers {body.support_type}",
        status="offered",
        is_demo=False,
        provenance=DataProvenance.USER.value,
        financial_note="DEMO / PROTOTYPE — No real financial transactions.",
    )
    db.add(collab)
    p.status = ChallengeStatus.INDUSTRY_COLLABORATION.value
    if p.challenge:
        p.challenge.status = ChallengeStatus.INDUSTRY_COLLABORATION.value
    db.commit()
    return get_project(project_id, db)


@router.patch("/{project_id}/collaborations/{collab_id}/accept", response_model=ProjectOut)
def accept_collaboration(project_id: int, collab_id: int, db: Session = Depends(get_db)):
    c = (
        db.query(IndustryCollaboration)
        .filter(
            IndustryCollaboration.id == collab_id,
            IndustryCollaboration.project_id == project_id,
        )
        .first()
    )
    if not c:
        raise HTTPException(404, "Collaboration not found")
    c.status = "active"
    db.commit()
    return get_project(project_id, db)


@router.post("/{project_id}/feedback", response_model=ProjectOut)
def add_feedback(project_id: int, body: FeedbackCreate, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    if p.status not in (
        ChallengeStatus.PILOT.value,
        ChallengeStatus.TESTING.value,
        ChallengeStatus.COMPLETED.value,
    ):
        # Allow feedback once pilot-ish, but mark capability
        pass

    fb = CommunityFeedback(
        project_id=project_id,
        user_id=body.user_id,
        rating=body.rating,
        feedback=body.feedback,
        problem_improvement=body.problem_improvement,
        deployment_confirmed=body.deployment_confirmed,
        is_demo=False,
        provenance=DataProvenance.USER.value,
    )
    db.add(fb)
    db.commit()
    return get_project(project_id, db)


@router.get("/meta/lifecycle")
def lifecycle_meta():
    return {
        "stages": LIFECYCLE,
        "public_labels": [
            "REPORTED", "UNDERSTOOD", "VALIDATED", "MATCHED", "TEAM FORMED",
            "RESEARCH", "PROTOTYPE", "TESTING", "PILOT", "COMMUNITY FEEDBACK",
            "IMPROVEMENT", "IMPACT",
        ],
        "default_milestones": DEFAULT_MILESTONES,
        "note": "REAL FUNCTIONALITY — status transitions persist in the database",
    }


@router.post("/{project_id}/plan")
def generate_plan(project_id: int, db: Session = Depends(get_db)):
    """AI SUGGESTION project plan — human must approve before it becomes official."""
    from ..ai.llm_service import llm_service

    p = (
        db.query(Project)
        .options(joinedload(Project.challenge))
        .filter(Project.id == project_id)
        .first()
    )
    if not p:
        raise HTTPException(404, "Project not found")
    challenge = {
        "domain": p.challenge.domain if p.challenge else None,
        "required_expertise": (p.challenge.required_expertise if p.challenge else None) or [],
        "title": p.challenge.title if p.challenge else p.name,
        "description": p.challenge.description if p.challenge else p.goal,
    }
    plan = llm_service.generate_project_plan(challenge, {"name": p.name, "goal": p.goal})
    # Store as suggestion only — not official until approved
    if p.challenge:
        from sqlalchemy.orm.attributes import flag_modified

        analysis = dict(p.challenge.ai_analysis or {})
        analysis["project_plan_suggestion"] = plan
        p.challenge.ai_analysis = analysis
        flag_modified(p.challenge, "ai_analysis")
    db.commit()
    return plan


@router.post("/{project_id}/plan/approve")
def approve_plan(
    project_id: int,
    body: Optional[PlanApproveBody] = Body(default=None),
    db: Session = Depends(get_db),
):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    suggestion = None
    if p.challenge and p.challenge.ai_analysis:
        suggestion = p.challenge.ai_analysis.get("project_plan_suggestion")
    if not suggestion:
        raise HTTPException(400, "No AI suggestion to approve. Generate a plan first.")
    # Human approval makes it the official proposal text
    lines = ["[OFFICIAL PLAN — human approved]"]
    for q in suggestion.get("research_questions", []):
        lines.append(f"Research: {q}")
    for m in suggestion.get("milestones", []):
        lines.append(f"Milestone: {m.get('title')} ({m.get('stage')})")
    for step in suggestion.get("pilot_plan", []):
        lines.append(f"Pilot: {step}")
    p.proposal = "\n".join(lines)
    if body and body.proposal:
        p.proposal = body.proposal
    db.commit()
    return get_project(project_id, db)


@router.post("/{project_id}/feedback/analyze")
def analyze_feedback(
    project_id: int,
    body: Optional[FeedbackAnalyzeBody] = Body(default=None),
    db: Session = Depends(get_db),
):
    from ..ai.llm_service import llm_service

    p = (
        db.query(Project)
        .options(joinedload(Project.feedback))
        .filter(Project.id == project_id)
        .first()
    )
    if not p:
        raise HTTPException(404, "Project not found")
    items = [
        {"rating": f.rating, "feedback": f.feedback, "problem_improvement": f.problem_improvement}
        for f in (p.feedback or [])
    ]
    if body and body.feedback:
        items.append({
            "rating": body.rating or 0,
            "feedback": body.feedback,
            "problem_improvement": body.problem_improvement,
        })
    return llm_service.analyze_feedback(items)
