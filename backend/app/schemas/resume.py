"""Resume-related schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# Resume Schemas
class ResumeBase(BaseModel):
    """Base resume schema."""
    title: str = Field(..., min_length=1, max_length=200)


class ResumeCreate(ResumeBase):
    """Schema for creating resume."""
    pass


class ResumeResponse(ResumeBase):
    """Schema for resume response."""
    id: UUID
    student_profile_id: UUID
    source_type: str
    original_filename: Optional[str] = None
    storage_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    content_type: Optional[str] = None
    status: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Resume Extraction Schemas
class ResumeExtractionResponse(BaseModel):
    """Schema for resume extraction response."""
    id: UUID
    resume_id: UUID
    raw_text: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    experience: Optional[Dict[str, Any]] = None
    projects: Optional[Dict[str, Any]] = None
    skills: Optional[Dict[str, Any]] = None
    certifications: Optional[Dict[str, Any]] = None
    achievements: Optional[Dict[str, Any]] = None
    is_confirmed: bool
    confirmed_at: Optional[datetime] = None
    extraction_method: Optional[str] = None
    llm_provider: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Resume Review Schemas
class ResumeReviewResponse(BaseModel):
    """Schema for resume review response."""
    id: UUID
    resume_id: UUID
    review_type: str
    overall_score: float
    overall_feedback: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeReviewFindingResponse(BaseModel):
    """Schema for resume review finding response."""
    id: UUID
    review_id: UUID
    category: str
    severity: str
    section: Optional[str] = None
    current_text: Optional[str] = None
    suggested_improvement: str
    reasoning: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
