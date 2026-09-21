from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import (
    Challenge, Project, University, IndustryPartner, IndustryCollaboration,
    CommunityFeedback, ChallengeStatus,
)
from ..schemas import (
    AdminStatsOut, ImpactOut, UniversityOut, IndustryPartnerOut, DemoUser,
)
from ..models import User

router = APIRouter(prefix="/api", tags=["admin"])


@router.get("/demo/users", response_model=list[DemoUser])
def demo_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_demo == True).all()  # noqa: E712
    return [
        DemoUser(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            organization=u.organization,
            district=u.district,
            is_demo=u.is_demo,
        )
        for u in users
    ]


@router.get("/universities", response_model=list[UniversityOut])
def list_universities(db: Session = Depends(get_db)):
    return db.query(University).all()


@router.get("/industry/partners", response_model=list[IndustryPartnerOut])
def list_partners(db: Session = Depends(get_db)):
    return db.query(IndustryPartner).all()


@router.get("/admin/stats", response_model=AdminStatsOut)
def admin_stats(db: Session = Depends(get_db)):
    challenges = db.query(Challenge).all()
    projects = db.query(Project).all()
    feedback = db.query(CommunityFeedback).all()

    pending_statuses = {
        ChallengeStatus.SUBMITTED.value,
        ChallengeStatus.UNDER_REVIEW.value,
    }
    validated_statuses = {
        ChallengeStatus.VALIDATED.value,
        ChallengeStatus.MATCHED.value,
        ChallengeStatus.UNIVERSITY_ACCEPTED.value,
        ChallengeStatus.TEAM_FORMED.value,
        ChallengeStatus.INDUSTRY_COLLABORATION.value,
        ChallengeStatus.PROTOTYPE.value,
        ChallengeStatus.TESTING.value,
        ChallengeStatus.PILOT.value,
        ChallengeStatus.COMPLETED.value,
    }
    active_project_statuses = {
        ChallengeStatus.UNIVERSITY_ACCEPTED.value,
        ChallengeStatus.TEAM_FORMED.value,
        ChallengeStatus.INDUSTRY_COLLABORATION.value,
        ChallengeStatus.PROTOTYPE.value,
        ChallengeStatus.TESTING.value,
        ChallengeStatus.PILOT.value,
    }

    domain_distribution: dict[str, int] = {}
    district_distribution: dict[str, int] = {}
    status_distribution: dict[str, int] = {}
    for c in challenges:
        d = c.domain or c.category or "Unknown"
        domain_distribution[d] = domain_distribution.get(d, 0) + 1
        district_distribution[c.district] = district_distribution.get(c.district, 0) + 1
        status_distribution[c.status] = status_distribution.get(c.status, 0) + 1

    projects_by_domain: dict[str, int] = {}
    for p in projects:
        d = p.challenge.domain if p.challenge else "Unknown"
        projects_by_domain[d] = projects_by_domain.get(d, 0) + 1

    lifecycle_counts: dict[str, int] = {}
    for p in projects:
        lifecycle_counts[p.status] = lifecycle_counts.get(p.status, 0) + 1

    ratings = [f.rating for f in feedback]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    uni_with_projects = (
        db.query(func.count(func.distinct(Project.university_id))).scalar() or 0
    )
    industry_count = (
        db.query(func.count(func.distinct(IndustryCollaboration.partner_id))).scalar() or 0
    )

    geo_points = []
    for c in challenges:
        if c.latitude is not None and c.longitude is not None:
            geo_points.append({
                "id": c.id,
                "title": c.title,
                "district": c.district,
                "lat": c.latitude,
                "lng": c.longitude,
                "status": c.status,
                "domain": c.domain,
                "is_demo": c.is_demo,
            })

    # Label: mix of demo seed + user data — always disclose
    demo_count = sum(1 for c in challenges if c.is_demo)
    user_count = len(challenges) - demo_count
    data_label = (
        f"Demo Data ({demo_count} seeded) + User Data ({user_count}) — "
        "statistics reflect current prototype database, not official government figures."
    )

    return AdminStatsOut(
        total_challenges=len(challenges),
        pending_validation=sum(1 for c in challenges if c.status in pending_statuses),
        validated_challenges=sum(1 for c in challenges if c.status in validated_statuses),
        active_projects=sum(1 for p in projects if p.status in active_project_statuses),
        completed_pilots=sum(
            1 for p in projects
            if p.status in (ChallengeStatus.PILOT.value, ChallengeStatus.COMPLETED.value)
        ),
        university_participation=uni_with_projects,
        industry_participation=industry_count,
        projects_by_domain=projects_by_domain,
        district_distribution=district_distribution,
        status_distribution=status_distribution,
        domain_distribution=domain_distribution,
        lifecycle_counts=lifecycle_counts,
        people_affected_total=sum(c.people_affected or 0 for c in challenges),
        communities_reached=sum(p.communities_reached or 0 for p in projects),
        community_feedback_count=len(feedback),
        average_community_rating=avg_rating,
        districts_covered=len(district_distribution),
        domains_addressed=len(domain_distribution),
        solution_adoption=sum(1 for f in feedback if f.deployment_confirmed),
        university_teams=sum(1 for p in projects if p.team_name),
        data_label=data_label,
        geo_points=geo_points,
    )


@router.get("/impact", response_model=ImpactOut)
def impact_dashboard(db: Session = Depends(get_db)):
    stats = admin_stats(db)
    return ImpactOut(
        people_affected=stats.people_affected_total,
        communities_reached=stats.communities_reached,
        projects_completed=sum(
            1 for p in db.query(Project).all()
            if p.status == ChallengeStatus.COMPLETED.value
        ),
        pilots_deployed=stats.completed_pilots,
        university_teams=stats.university_teams,
        industry_partners=db.query(IndustryPartner).count(),
        domains_addressed=stats.domains_addressed,
        districts_covered=stats.districts_covered,
        community_feedback=stats.community_feedback_count,
        average_rating=stats.average_community_rating,
        solution_adoption=stats.solution_adoption,
        data_label=stats.data_label,
    )


@router.post("/demo/reset")
def reset_demo(db: Session = Depends(get_db)):
    """Re-seed demo journey. REAL FUNCTIONALITY — wipes and restores DEMO DATA."""
    from ..seed import seed_database

    seed_database(db, force=True)
    return {
        "ok": True,
        "message": "Demo database reset. AquaGuard journey restored.",
        "data_label": "DEMO DATA restored",
        "note": "Destructive action — use only for judge demo reset.",
    }


@router.get("/dashboard/ai-summary")
def dashboard_ai_summary(db: Session = Depends(get_db)):
    """Local dashboard summary grounded in real DB aggregates only."""
    from ..ai.llm_service import llm_service

    stats = admin_stats(db)
    demo_challenges = db.query(Challenge).filter(Challenge.is_demo == True).count()  # noqa: E712
    payload = {
        "total_challenges": stats.total_challenges,
        "total_projects": stats.active_projects + stats.completed_pilots,
        "demo_challenges": demo_challenges,
        "validated_or_beyond": stats.validated_challenges,
        "pilot_or_completed": stats.completed_pilots,
    }
    summary = llm_service.summarize_dashboard(payload)
    summary["raw_stats"] = {
        "total_challenges": stats.total_challenges,
        "pending_validation": stats.pending_validation,
        "active_projects": stats.active_projects,
        "completed_pilots": stats.completed_pilots,
        "people_affected_total": stats.people_affected_total,
        "community_feedback_count": stats.community_feedback_count,
        "data_label": stats.data_label,
    }
    return summary
