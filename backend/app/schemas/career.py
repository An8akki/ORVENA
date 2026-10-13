"""Career-related schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum


# Enums
class SessionType(str, Enum):
    """Discovery session types."""
    INITIAL = "initial"
    REFINEMENT = "refinement"
    FOCUSED = "focused"


class SessionStatus(str, Enum):
    """Session status."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


# Career Discovery Session Schemas
class CareerDiscoverySessionBase(BaseModel):
    """Base career discovery session schema."""
    session_type: SessionType = SessionType.INITIAL


class CareerDiscoverySessionCreate(CareerDiscoverySessionBase):
    """Schema for creating discovery session."""
    pass


class CareerDiscoverySessionUpdate(BaseModel):
    """Schema for updating discovery session."""
    status: Optional[SessionStatus] = None


class CareerDiscoveryResponseBase(BaseModel):
    """Base discovery response schema."""
    sequence_number: int = Field(..., ge=1)
    question_text: str
    response_text: str
    question_category: Optional[str] = None
    phase: Optional[str] = None


class CareerDiscoveryResponseCreate(CareerDiscoveryResponseBase):
    """Schema for creating discovery response."""
    pass


class CareerDiscoveryResponseResponse(CareerDiscoveryResponseBase):
    """Schema for discovery response."""
    id: UUID
    session_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerDiscoverySessionResponse(CareerDiscoverySessionBase):
    """Schema for discovery session response."""
    id: UUID
    student_profile_id: UUID
    status: SessionStatus
    current_phase: Optional[str] = None
    completed_phases: Optional[List[str]] = None
    completed_at: Optional[datetime] = None
    started_at: datetime
    created_at: datetime
    updated_at: datetime
    responses: List[CareerDiscoveryResponseResponse] = []

    model_config = ConfigDict(from_attributes=True)


class NextQuestionRequest(BaseModel):
    """Request for next question."""
    session_id: UUID


class NextQuestionResponse(BaseModel):
    """Response with next question."""
    question_number: int
    question_text: str
    question_type: str  # "mcq" or "descriptive"
    options: Optional[Dict[str, str]] = None  # For MCQ questions: {"A": "option1", "B": "option2", ...}
    session_id: UUID


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    session_id: UUID
    question_number: int
    question_text: str
    response_text: str = Field(..., min_length=1)


class SessionAnalysisResponse(BaseModel):
    """Response with session analysis."""
    session_id: UUID
    insights: Dict[str, Any]
    summary: str


# Career Goal Schemas
class CareerGoalBase(BaseModel):
    """Base career goal schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    career_role_id: Optional[UUID] = None
    target_timeline: Optional[str] = Field(None, max_length=50)
    priority: str = Field(default="medium", max_length=20)
    status: str = Field(default="active", max_length=20)
    is_primary: bool = False


class CareerGoalCreate(CareerGoalBase):
    """Schema for creating career goal."""
    pass


class CareerGoalUpdate(BaseModel):
    """Schema for updating career goal."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    career_role_id: Optional[UUID] = None
    target_timeline: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)
    is_primary: Optional[bool] = None


class CareerGoalResponse(CareerGoalBase):
    """Schema for career goal response."""
    id: UUID
    student_profile_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Career Role Schemas
class CareerRoleBase(BaseModel):
    """Base career role schema."""
    name: str
    category: str
    description: str
    typical_salary_min: Optional[int] = None
    typical_salary_max: Optional[int] = None


class CareerRoleResponse(CareerRoleBase):
    """Schema for career role response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Career Recommendation Schemas
class CareerRecommendationBase(BaseModel):
    """Base career recommendation schema."""
    fit_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    strengths: List[str] = []
    gaps: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []
    recommendation_rank: Optional[int] = None


class CareerRecommendationResponse(CareerRecommendationBase):
    """Schema for career recommendation response."""
    id: UUID
    student_profile_id: UUID
    career_role_id: UUID
    session_id: Optional[UUID] = None  # Changed from discovery_session_id to match model
    career_role: Optional[CareerRoleResponse] = None
    
    # Salary information
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    salary_currency: str = "USD"
    salary_period: str = "annual"
    
    # Industry trends
    industry_trend: Optional[str] = None
    market_growth: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Career Roadmap Schemas
class RoadmapMilestoneBase(BaseModel):
    """Base roadmap milestone schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., max_length=50)
    estimated_hours: Optional[int] = Field(None, ge=1, le=500)
    sequence_number: int = Field(..., ge=1)
    resources: List[str] = []


class RoadmapMilestoneResponse(RoadmapMilestoneBase):
    """Schema for roadmap milestone response."""
    id: UUID
    roadmap_id: UUID
    status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CareerRoadmapBase(BaseModel):
    """Base career roadmap schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_duration_weeks: Optional[int] = Field(None, ge=1, le=104)


class CareerRoadmapCreate(BaseModel):
    """Schema for creating career roadmap."""
    career_goal_id: Optional[UUID] = None
    career_role_id: Optional[UUID] = None
    recommendation_id: Optional[UUID] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_duration_weeks: int = Field(default=12, ge=1, le=104)


class CareerRoadmapResponse(CareerRoadmapBase):
    """Schema for career roadmap response."""
    id: UUID
    student_profile_id: UUID
    career_goal_id: UUID
    recommendation_id: Optional[UUID] = None
    status: str
    progress_percentage: int
    milestones: List[RoadmapMilestoneResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdateMilestoneStatusRequest(BaseModel):
    """Request to update milestone status."""
    status: str = Field(..., pattern="^(pending|in_progress|completed|skipped)$")
