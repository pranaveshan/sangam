"""SQLAlchemy models for SANGAM."""
from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .database import Base


class DataProvenance(str, enum.Enum):
    DEMO = "demo"
    USER = "user"
    SYSTEM = "system"


class ChallengeStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VALIDATED = "validated"
    MATCHED = "matched"
    UNIVERSITY_ACCEPTED = "university_accepted"
    TEAM_FORMED = "team_formed"
    INDUSTRY_COLLABORATION = "industry_collaboration"
    PROTOTYPE = "prototype"
    TESTING = "testing"
    PILOT = "pilot"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CONSOLIDATED = "consolidated"


class UrgencyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    GOVERNMENT = "government"
    UNIVERSITY = "university"
    STUDENT = "student"
    INDUSTRY = "industry"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(50))
    organization: Mapped[str | None] = mapped_column(String(300), nullable=True)
    district: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance: Mapped[str] = mapped_column(String(20), default=DataProvenance.DEMO.value)

    challenges = relationship("Challenge", back_populates="reporter")
    feedback = relationship("CommunityFeedback", back_populates="user")


class University(Base, TimestampMixin):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    short_name: Mapped[str] = mapped_column(String(80))
    state: Mapped[str] = mapped_column(String(120))
    district: Mapped[str] = mapped_column(String(120))
    departments: Mapped[list] = mapped_column(JSON, default=list)
    research_areas: Mapped[list] = mapped_column(JSON, default=list)
    faculty_expertise: Mapped[list] = mapped_column(JSON, default=list)
    laboratory_capabilities: Mapped[list] = mapped_column(JSON, default=list)
    student_skills: Mapped[list] = mapped_column(JSON, default=list)
    incubation_facilities: Mapped[list] = mapped_column(JSON, default=list)
    domains: Mapped[list] = mapped_column(JSON, default=list)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    provenance: Mapped[str] = mapped_column(String(20), default=DataProvenance.DEMO.value)
    notes: Mapped[str | None] = mapped_column(
        Text, default="DEMO DATA — Prototype institution for SIH demonstration only."
    )

    projects = relationship("Project", back_populates="university")


class IndustryPartner(Base, TimestampMixin):
    __tablename__ = "industry_partners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    sector: Mapped[str] = mapped_column(String(120))
    support_types: Mapped[list] = mapped_column(JSON, default=list)
    focus_domains: Mapped[list] = mapped_column(JSON, default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    provenance: Mapped[str] = mapped_column(String(20), default=DataProvenance.DEMO.value)
    notes: Mapped[str | None] = mapped_column(
        Text, default="DEMO DATA — Prototype partner for SIH demonstration only."
    )

    collaborations = relationship("IndustryCollaboration", back_populates="partner")


class Challenge(Base, TimestampMixin):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(400))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(300))
    district: Mapped[str] = mapped_column(String(120), index=True)
    state: Mapped[str] = mapped_column(String(120), default="Demo State")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    community_impact: Mapped[str] = mapped_column(Text)
    people_affected: Mapped[int] = mapped_column(Integer, default=0)
    urgency: Mapped[str] = mapped_column(String(40), default=UrgencyLevel.MEDIUM.value)
    severity: Mapped[str] = mapped_column(String(40), default="medium")
    geographic_spread: Mapped[str] = mapped_column(String(40), default="local")
    contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(60), default=ChallengeStatus.SUBMITTED.value, index=True
    )
    domain: Mapped[str | None] = mapped_column(String(120), nullable=True)
    subdomain: Mapped[str | None] = mapped_column(String(120), nullable=True)
    priority_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    priority_label: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ai_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    required_expertise: Mapped[list | None] = mapped_column(JSON, nullable=True)
    similar_challenge_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    consolidated_into_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("challenges.id"), nullable=True
    )
    matched_university_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("universities.id"), nullable=True
    )
    reporter_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance: Mapped[str] = mapped_column(String(20), default=DataProvenance.USER.value)
    evidence_score: Mapped[float] = mapped_column(Float, default=0.3)

    reporter = relationship("User", back_populates="challenges")
    project = relationship("Project", back_populates="challenge", uselist=False)


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    goal: Mapped[str] = mapped_column(Text)
    challenge_id: Mapped[int] = mapped_column(Integer, ForeignKey("challenges.id"), unique=True)
    university_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("universities.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(60), default=ChallengeStatus.UNIVERSITY_ACCEPTED.value
    )
    proposal: Mapped[str | None] = mapped_column(Text, nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    team_members: Mapped[list | None] = mapped_column(JSON, nullable=True)
    faculty_mentors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    match_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    people_impacted: Mapped[int] = mapped_column(Integer, default=0)
    communities_reached: Mapped[int] = mapped_column(Integer, default=0)
    pilot_location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    pilot_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance: Mapped[str] = mapped_column(String(20), default=DataProvenance.USER.value)

    challenge = relationship("Challenge", back_populates="project")
    university = relationship("University", back_populates="projects")
    milestones = relationship(
        "Milestone", back_populates="project", cascade="all, delete-orphan",
        order_by="Milestone.order_index"
    )
    collaborations = relationship(
        "IndustryCollaboration", back_populates="project", cascade="all, delete-orphan"
    )
    feedback = relationship(
        "CommunityFeedback", back_populates="project", cascade="all, delete-orphan"
    )


class Milestone(Base, TimestampMixin):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(40), default="pending")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    project = relationship("Project", back_populates="milestones")


class IndustryCollaboration(Base, TimestampMixin):
    __tablename__ = "industry_collaborations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    partner_id: Mapped[int] = mapped_column(Integer, ForeignKey("industry_partners.id"))
    support_type: Mapped[str] = mapped_column(String(80))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="offered")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance: Mapped[str] = mapped_column(String(20), default=DataProvenance.USER.value)
    financial_note: Mapped[str] = mapped_column(
        String(300),
        default="DEMO / PROTOTYPE — No real financial transactions.",
    )

    project = relationship("Project", back_populates="collaborations")
    partner = relationship("IndustryPartner", back_populates="collaborations")


class CommunityFeedback(Base, TimestampMixin):
    __tablename__ = "community_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    rating: Mapped[int] = mapped_column(Integer)
    feedback: Mapped[str] = mapped_column(Text)
    problem_improvement: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deployment_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance: Mapped[str] = mapped_column(String(20), default=DataProvenance.USER.value)

    project = relationship("Project", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
