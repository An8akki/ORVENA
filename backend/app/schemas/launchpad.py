"""
Pydantic Schemas for Orvena Project Launchpad
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl


# -------------------------------------------------------------
# Project Idea Catalogue & Recommendations
# -------------------------------------------------------------
class MilestoneTemplate(BaseModel):
    title: str
    phase: str
    description: str
    deliverables: List[str] = []


class ProjectIdea(BaseModel):
    id: str
    title: str
    problem_statement: str
    intended_users: str
    domain: str
    difficulty: str  # beginner, intermediate, advanced
    prerequisites: List[str]
    recommended_technologies: List[str]
    estimated_duration_weeks: int
    weekly_hours: int
    expected_deliverables: List[str]
    learning_outcomes: List[str]
    suggested_milestones: List[MilestoneTemplate]
    validation_strategy: str
    possible_next_stage_pathways: List[str]
    relevant_career_skills: List[str]
    primary_goals: List[str]
    match_score: Optional[int] = None
    match_explanation: Optional[str] = None


class IdeaRecommendationRequest(BaseModel):
    target_domain: Optional[str] = None
    difficulty_preference: Optional[str] = None  # any, beginner, intermediate, advanced
    weekly_hours_available: Optional[int] = Field(default=10, ge=1, le=60)
    primary_objective: Optional[str] = None  # learning, portfolio, research, competition, product, entrepreneurship
    preferred_technologies: Optional[List[str]] = None
    target_career_roles: Optional[List[str]] = None
    existing_skills: Optional[List[str]] = None


class IdeaRecommendationResponse(BaseModel):
    recommendations: List[ProjectIdea]
    total_matches: int
    applied_profile_signals: Dict[str, Any]


# -------------------------------------------------------------
# Structured Project Planning
# -------------------------------------------------------------
class PlanGenerationRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    problem_statement: str = Field(..., min_length=10)
    intended_users: str = Field(..., min_length=3)
    proposed_solution: str = Field(..., min_length=10)
    domain: str
    technologies: List[str] = Field(..., min_items=1)
    current_stage: str = "idea"  # idea, planning, in_progress, validation, completed
    weekly_hours: int = Field(default=10, ge=1, le=60)
    target_duration_weeks: int = Field(default=8, ge=1, le=52)
    primary_goal: str = "portfolio"
    constraints_or_resources: Optional[str] = None
    repository_url: Optional[str] = None
    demo_url: Optional[str] = None


class PlannedPhase(BaseModel):
    phase_name: str
    target_week_start: int
    target_week_end: int
    objective: str
    tasks: List[str]
    deliverables: List[str]
    validation_criteria: str


class GeneratedProjectPlan(BaseModel):
    title: str
    problem_definition: str
    minimum_viable_scope: List[str]
    future_scope: List[str]
    required_prerequisites: List[str]
    phases: List[PlannedPhase]
    testing_and_validation_plan: List[str]
    risks_and_dependencies: List[Dict[str, str]]
    suggested_milestones: List[MilestoneTemplate]
    suggested_timeline_weeks: int


# -------------------------------------------------------------
# Project Milestones
# -------------------------------------------------------------
class ProjectMilestoneBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    phase: str = "Implementation"
    sequence_order: int = 1
    status: str = "not_started"  # not_started, in_progress, blocked, completed
    target_date: Optional[date] = None
    deliverables: Optional[List[str]] = None
    resources: Optional[List[str]] = None
    blocker_notes: Optional[str] = None


class ProjectMilestoneCreate(ProjectMilestoneBase):
    pass


class ProjectMilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    phase: Optional[str] = None
    sequence_order: Optional[int] = None
    status: Optional[str] = None
    target_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    deliverables: Optional[List[str]] = None
    resources: Optional[List[str]] = None
    blocker_notes: Optional[str] = None


class ProjectMilestoneResponse(ProjectMilestoneBase):
    id: UUID
    project_id: UUID
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Project Core CRUD
# -------------------------------------------------------------
class LaunchpadProjectCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    technologies: List[str] = Field(..., min_items=1)
    role: Optional[str] = "Lead Developer"
    problem_statement: Optional[str] = None
    target_users: Optional[str] = None
    proposed_solution: Optional[str] = None
    domain: Optional[str] = "Full Stack Web"
    difficulty_level: Optional[str] = "intermediate"
    primary_goal: Optional[str] = "portfolio"
    stage: Optional[str] = "idea"
    status: Optional[str] = "in_progress"
    weekly_hours: Optional[int] = 10
    estimated_duration_weeks: Optional[int] = 8
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    visibility: Optional[str] = "public"
    origin: Optional[str] = "scratch"
    catalogue_idea_id: Optional[str] = None
    initial_milestones: Optional[List[ProjectMilestoneCreate]] = None
    plan_data: Optional[Dict[str, Any]] = None


class LaunchpadProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    role: Optional[str] = None
    problem_statement: Optional[str] = None
    target_users: Optional[str] = None
    proposed_solution: Optional[str] = None
    domain: Optional[str] = None
    difficulty_level: Optional[str] = None
    primary_goal: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    blocker_description: Optional[str] = None
    weekly_hours: Optional[int] = None
    estimated_duration_weeks: Optional[int] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    visibility: Optional[str] = None
    achievements: Optional[List[str]] = None
    impact_metrics: Optional[List[str]] = None
    plan_data: Optional[Dict[str, Any]] = None


class LaunchpadProjectResponse(BaseModel):
    id: UUID
    student_profile_id: UUID
    title: str
    description: str
    role: Optional[str] = None
    technologies: List[str]
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    achievements: Optional[List[str]] = None
    team_size: Optional[int] = None
    impact_metrics: Optional[List[str]] = None
    visibility: str
    problem_statement: Optional[str] = None
    target_users: Optional[str] = None
    proposed_solution: Optional[str] = None
    domain: Optional[str] = None
    difficulty_level: Optional[str] = None
    primary_goal: Optional[str] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    blocker_description: Optional[str] = None
    weekly_hours: Optional[int] = None
    estimated_duration_weeks: Optional[int] = None
    completion_percentage: int
    origin: Optional[str] = None
    catalogue_idea_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LaunchpadProjectDetailResponse(LaunchpadProjectResponse):
    milestones: List[ProjectMilestoneResponse] = []
    latest_assessment: Optional[Dict[str, Any]] = None
    latest_outcome: Optional[Dict[str, Any]] = None
    showcase_slug: Optional[str] = None
    showcase_public: bool = False
    plan_data: Optional[Dict[str, Any]] = None


# -------------------------------------------------------------
# 5-Dimension Evaluation
# -------------------------------------------------------------
class DimensionAnswer(BaseModel):
    dimension_key: str  # problem_clarity, implementation_maturity, testing_validation, differentiation, documentation_readiness
    selected_option_level: int = Field(..., ge=0, le=4)  # 0 to 4
    notes: Optional[str] = None
    evidence_url: Optional[str] = None


class ProjectEvaluationRequest(BaseModel):
    answers: List[DimensionAnswer]
    repository_url: Optional[str] = None
    demo_url: Optional[str] = None
    sync_from_resume: bool = False


class DimensionScoreResult(BaseModel):
    dimension_name: str
    score: float  # 0 to 20
    max_score: float = 20.0
    status_label: str  # Strong, Adequate, Needs Attention, Unknown
    level: int
    feedback: str
    evidence_provided: bool


class ProjectEvaluationResponse(BaseModel):
    id: UUID
    project_id: UUID
    overall_score: float
    overall_rating: str
    dimension_scores: Dict[str, DimensionScoreResult]
    strengths: List[str]
    missing_evidence: List[str]
    improvement_priorities: List[str]
    recommended_milestone: str
    reassessment_conditions: str
    summary: str
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Project Outcome Intelligence (6 Pathways)
# -------------------------------------------------------------
class PathwayResult(BaseModel):
    pathway_key: str  # PRODUCT_DEVELOPMENT, RESEARCH_AND_PUBLICATION, INNOVATION_AND_FURTHER_DISCOVERY, STARTUP_AND_COMMERCIALISATION, COMPETITIONS_AND_HACKATHONS, CAREER_AND_PORTFOLIO
    title: str
    score: int  # 0 to 100
    tier: str  # Ready, Near-Ready, Needs Foundational Work
    summary_rationale: str
    readiness_factors: List[str]
    missing_evidence: List[str]
    action_checklist: List[str]
    suggested_milestones: List[MilestoneTemplate]


class OutcomeIntelligenceRequest(BaseModel):
    student_primary_intent: Optional[str] = None  # None or specific target pathway


class OutcomeIntelligenceResponse(BaseModel):
    id: UUID
    project_id: UUID
    selected_goal: Optional[str]
    top_pathway: str
    pathways: List[PathwayResult]
    readiness_summary: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplyPathwayRequest(BaseModel):
    pathway_key: str
    replace_existing_milestones: bool = False


# -------------------------------------------------------------
# Project Showcase
# -------------------------------------------------------------
class ShowcaseUpdateRequest(BaseModel):
    is_public: bool
    headline: Optional[str] = None
    problem_solution_summary: Optional[str] = None
    key_contributions: Optional[List[str]] = None
    outcomes_metrics: Optional[List[str]] = None
    skills_highlighted: Optional[List[str]] = None
    media_urls: Optional[Dict[str, Any]] = None


class ShowcaseResponse(BaseModel):
    id: UUID
    project_id: UUID
    student_profile_id: UUID
    slug: str
    is_public: bool
    headline: Optional[str]
    problem_solution_summary: Optional[str]
    key_contributions: Optional[List[str]]
    outcomes_metrics: Optional[List[str]]
    skills_highlighted: Optional[List[str]]
    media_urls: Optional[Dict[str, Any]]
    view_count: int
    project_title: str
    project_description: str
    technologies: List[str]
    github_url: Optional[str]
    demo_url: Optional[str]
    stage: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# -------------------------------------------------------------
# Opportunities Directory & Applications
# -------------------------------------------------------------
class OpportunityResponse(BaseModel):
    id: UUID
    title: str
    provider: str
    opportunity_type: str
    description: str
    official_url: str
    eligibility_requirements: Optional[List[str]]
    beneficiary_type: str
    geographic_scope: str
    domains: Optional[List[str]]
    required_project_stage: str
    funding_amount_or_benefits: Optional[str]
    is_monetary: bool
    application_deadline: Optional[date]
    is_rolling: bool
    application_instructions: Optional[str]
    date_last_verified: date
    status: str
    is_verified: bool
    source_notes: Optional[str]

    class Config:
        from_attributes = True


class OpportunityApplicationCreate(BaseModel):
    project_id: Optional[UUID] = None
    status: str = "saved"  # saved, researching, preparing, submitted, accepted, rejected, closed
    notes: Optional[str] = None
    submission_date: Optional[date] = None


class OpportunityApplicationUpdate(BaseModel):
    project_id: Optional[UUID] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    submission_date: Optional[date] = None


class OpportunityApplicationResponse(BaseModel):
    id: UUID
    student_profile_id: UUID
    project_id: Optional[UUID]
    opportunity_id: UUID
    status: str
    notes: Optional[str]
    submission_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    opportunity: OpportunityResponse

    class Config:
        from_attributes = True
