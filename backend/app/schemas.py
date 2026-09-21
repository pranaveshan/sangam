from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ProvenanceMixin(BaseModel):
    is_demo: bool = False
    provenance: str = "user"


# ---- Auth / Demo roles ----
class DemoUser(BaseModel):
    id: int
    name: str
    email: str
    role: str
    organization: Optional[str] = None
    district: Optional[str] = None
    is_demo: bool = True


# ---- Challenges ----
class ChallengeCreate(BaseModel):
    title: str
    description: str
    category: str
    location: str
    district: str
    state: str = "Demo State"
    community_impact: str
    people_affected: int = Field(ge=0)
    urgency: str = "medium"
    severity: str = "medium"
    geographic_spread: str = "local"
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    video_url: Optional[str] = None
    reporter_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SimilarChallengeOut(BaseModel):
    id: int
    title: str
    location: str
    district: str
    similarity: float
    recommended_action: str
    status: str
    domain: Optional[str] = None


class PriorityFactorOut(BaseModel):
    factor: str
    value: str
    weight: float
    contribution: float


class AIAnalysisOut(BaseModel):
    domain: str
    subdomain: str
    priority: str
    priority_score: float
    estimated_impact: str
    required_expertise: list[str]
    similar_reports: int
    recommended_action: str
    priority_factors: list[PriorityFactorOut]
    similar_challenges: list[SimilarChallengeOut]
    classification_method: str
    duplicate_method: str
    matching_method: str
    disclaimer: str


class UniversityMatchOut(BaseModel):
    university_id: int
    university_name: str
    short_name: str
    score: float
    explanation: str
    departments: list[str]
    research_areas: list[str]
    is_demo: bool = True
    provenance: str = "demo"


class ChallengeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: str
    location: str
    district: str
    state: str
    community_impact: str
    people_affected: int
    urgency: str
    severity: str
    geographic_spread: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    photo_path: Optional[str] = None
    document_path: Optional[str] = None
    video_url: Optional[str] = None
    status: str
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    priority_score: Optional[float] = None
    priority_label: Optional[str] = None
    ai_analysis: Optional[dict[str, Any]] = None
    required_expertise: Optional[list[str]] = None
    similar_challenge_ids: Optional[list[int]] = None
    consolidated_into_id: Optional[int] = None
    matched_university_id: Optional[int] = None
    reporter_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_demo: bool
    provenance: str
    created_at: datetime
    updated_at: datetime


class ChallengeSubmitResponse(BaseModel):
    challenge: ChallengeOut
    ai_analysis: AIAnalysisOut
    university_matches: list[UniversityMatchOut]
    data_labels: dict[str, str]
    rag: Optional[dict[str, Any]] = None


class ValidateChallengeRequest(BaseModel):
    action: str = "validate"  # validate | reject | consolidate
    consolidate_into_id: Optional[int] = None
    notes: Optional[str] = None


# ---- University / Projects ----
class AcceptChallengeRequest(BaseModel):
    university_id: int
    project_name: str
    goal: str
    proposal: Optional[str] = None
    match_explanation: Optional[str] = None
    match_score: Optional[float] = None
    challenge_id: Optional[int] = None


class TeamUpdateRequest(BaseModel):
    team_name: str
    team_members: list[dict[str, Any]]
    faculty_mentors: list[dict[str, Any]]


class MilestoneCreate(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0


class MilestoneUpdate(BaseModel):
    status: str
    description: Optional[str] = None


class MilestoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    order_index: int
    status: str
    completed_at: Optional[datetime] = None


class CollaborationCreate(BaseModel):
    partner_id: int
    support_type: str
    details: Optional[str] = None


class CollaborationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    partner_id: int
    support_type: str
    details: Optional[str] = None
    status: str
    is_demo: bool
    provenance: str
    financial_note: str
    partner_name: Optional[str] = None


class FeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    feedback: str
    problem_improvement: Optional[str] = None
    deployment_confirmed: bool = False
    user_id: Optional[int] = None


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    rating: int
    feedback: str
    problem_improvement: Optional[str] = None
    photo_path: Optional[str] = None
    deployment_confirmed: bool
    is_demo: bool
    provenance: str
    created_at: datetime


class ProjectStatusUpdate(BaseModel):
    status: str
    people_impacted: Optional[int] = None
    communities_reached: Optional[int] = None
    pilot_location: Optional[str] = None
    pilot_notes: Optional[str] = None
    proposal: Optional[str] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    goal: str
    challenge_id: int
    university_id: Optional[int] = None
    status: str
    proposal: Optional[str] = None
    team_name: Optional[str] = None
    team_members: Optional[list] = None
    faculty_mentors: Optional[list] = None
    match_explanation: Optional[str] = None
    match_score: Optional[float] = None
    people_impacted: int
    communities_reached: int
    pilot_location: Optional[str] = None
    pilot_notes: Optional[str] = None
    is_demo: bool
    provenance: str
    created_at: datetime
    milestones: list[MilestoneOut] = []
    collaborations: list[CollaborationOut] = []
    feedback: list[FeedbackOut] = []
    challenge_title: Optional[str] = None
    university_name: Optional[str] = None
    domain: Optional[str] = None
    district: Optional[str] = None
    average_rating: Optional[float] = None


class UniversityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: str
    state: str
    district: str
    departments: list
    research_areas: list
    faculty_expertise: list
    laboratory_capabilities: list
    student_skills: list
    incubation_facilities: list
    domains: list
    is_demo: bool
    provenance: str
    notes: Optional[str] = None


class IndustryPartnerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sector: str
    support_types: list
    focus_domains: list
    description: Optional[str] = None
    is_demo: bool
    provenance: str
    notes: Optional[str] = None


class AdminStatsOut(BaseModel):
    total_challenges: int
    pending_validation: int
    validated_challenges: int
    active_projects: int
    completed_pilots: int
    university_participation: int
    industry_participation: int
    projects_by_domain: dict[str, int]
    district_distribution: dict[str, int]
    status_distribution: dict[str, int]
    domain_distribution: dict[str, int]
    lifecycle_counts: dict[str, int]
    people_affected_total: int
    communities_reached: int
    community_feedback_count: int
    average_community_rating: Optional[float]
    districts_covered: int
    domains_addressed: int
    solution_adoption: int
    university_teams: int
    data_label: str
    geo_points: list[dict[str, Any]]


class ImpactOut(BaseModel):
    people_affected: int
    communities_reached: int
    projects_completed: int
    pilots_deployed: int
    university_teams: int
    industry_partners: int
    domains_addressed: int
    districts_covered: int
    community_feedback: int
    average_rating: Optional[float]
    solution_adoption: int
    data_label: str
