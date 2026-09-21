"""Shared serialization helpers."""
from __future__ import annotations

from .models import Project, IndustryCollaboration


def serialize_collaboration(c: IndustryCollaboration) -> dict:
    return {
        "id": c.id,
        "project_id": c.project_id,
        "partner_id": c.partner_id,
        "support_type": c.support_type,
        "details": c.details,
        "status": c.status,
        "is_demo": c.is_demo,
        "provenance": c.provenance,
        "financial_note": c.financial_note,
        "partner_name": c.partner.name if c.partner else None,
    }


def serialize_project(p: Project) -> dict:
    ratings = [f.rating for f in (p.feedback or [])]
    avg = round(sum(ratings) / len(ratings), 2) if ratings else None
    return {
        "id": p.id,
        "name": p.name,
        "goal": p.goal,
        "challenge_id": p.challenge_id,
        "university_id": p.university_id,
        "status": p.status,
        "proposal": p.proposal,
        "team_name": p.team_name,
        "team_members": p.team_members or [],
        "faculty_mentors": p.faculty_mentors or [],
        "match_explanation": p.match_explanation,
        "match_score": p.match_score,
        "people_impacted": p.people_impacted,
        "communities_reached": p.communities_reached,
        "pilot_location": p.pilot_location,
        "pilot_notes": p.pilot_notes,
        "is_demo": p.is_demo,
        "provenance": p.provenance,
        "created_at": p.created_at,
        "milestones": p.milestones or [],
        "collaborations": [serialize_collaboration(c) for c in (p.collaborations or [])],
        "feedback": p.feedback or [],
        "challenge_title": p.challenge.title if p.challenge else None,
        "university_name": p.university.name if p.university else None,
        "domain": p.challenge.domain if p.challenge else None,
        "district": p.challenge.district if p.challenge else None,
        "average_rating": avg,
    }
