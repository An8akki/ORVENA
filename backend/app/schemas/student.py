"""Student profile schemas for API requests and responses."""

from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum


# Enums
class EducationLevel(str, Enum):
    """Education levels."""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    BOOTCAMP = "bootcamp"
    CERTIFICATION = "certification"


class SkillCategory(str, Enum):
    """Skill categories."""
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"
    TOOL = "tool"
    DOMAIN = "domain"


class ProficiencyLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# Student Profile Schemas
class StudentProfileBase(BaseModel):
    """Base student profile schema."""
    email: str = Field(..., max_length=255)
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=1950, le=2050)
    expected_salary_min: Optional[int] = Field(None, ge=0)
    expected_salary_max: Optional[int] = Field(None, ge=0)


class StudentProfileCreate(StudentProfileBase):
    """Schema for creating student profile."""
    pass


class StudentProfileUpdate(BaseModel):
    """Schema for updating student profile."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=200)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=1950, le=2050)
    expected_salary_min: Optional[int] = Field(None, ge=0)
    expected_salary_max: Optional[int] = Field(None, ge=0)


class StudentProfileResponse(StudentProfileBase):
    """Schema for student profile response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Education Schemas
class EducationRecordBase(BaseModel):
    """Base education record schema."""
    institution_name: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=200)
    field_of_study: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    gpa_scale: Optional[float] = Field(None, ge=1.0, le=10.0)


class EducationRecordCreate(EducationRecordBase):
    """Schema for creating education record."""
    pass


class EducationRecordUpdate(BaseModel):
    """Schema for updating education record."""
    institution_name: Optional[str] = Field(None, min_length=1, max_length=200)
    degree: Optional[str] = Field(None, min_length=1, max_length=200)
    field_of_study: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    gpa_scale: Optional[float] = Field(None, ge=1.0, le=10.0)


class EducationRecordResponse(EducationRecordBase):
    """Schema for education record response."""
    id: UUID
    student_profile_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Skill Schemas
class SkillBase(BaseModel):
    """Base skill schema."""
    name: str = Field(..., min_length=1, max_length=100)
    category: SkillCategory


class SkillCreate(SkillBase):
    """Schema for creating skill."""
    pass


class SkillResponse(SkillBase):
    """Schema for skill response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentSkillBase(BaseModel):
    """Base student skill schema."""
    proficiency_level: ProficiencyLevel
    years_of_experience: Optional[float] = Field(None, ge=0.0, le=50.0)
    last_used_date: Optional[date] = None
    is_verified: bool = False
    evidence_type: Optional[str] = None
    evidence_description: Optional[str] = None


class StudentSkillCreate(StudentSkillBase):
    """Schema for creating student skill."""
    pass


class StudentSkillUpdate(BaseModel):
    """Schema for updating student skill."""
    proficiency_level: Optional[ProficiencyLevel] = None
    years_of_experience: Optional[float] = Field(None, ge=0.0, le=50.0)
    last_used_date: Optional[date] = None
    is_verified: Optional[bool] = None
    evidence_type: Optional[str] = None
    evidence_description: Optional[str] = None


class StudentSkillResponse(StudentSkillBase):
    """Schema for student skill response."""
    id: UUID
    student_profile_id: UUID
    skill_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Project Schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    role: Optional[str] = Field(None, max_length=100)
    technologies: List[str] = Field(default_factory=list)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    github_url: Optional[str] = Field(None, max_length=500)
    demo_url: Optional[str] = Field(None, max_length=500)
    team_size: Optional[int] = Field(None, ge=1, le=1000)


class ProjectCreate(ProjectBase):
    """Schema for creating project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating project."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    role: Optional[str] = Field(None, max_length=100)
    technologies: Optional[List[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    github_url: Optional[str] = Field(None, max_length=500)
    demo_url: Optional[str] = Field(None, max_length=500)
    team_size: Optional[int] = Field(None, ge=1, le=1000)


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: UUID
    student_profile_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Certification Schemas
class CertificationBase(BaseModel):
    """Base certification schema."""
    name: str = Field(..., min_length=1, max_length=200)
    issuing_organization: str = Field(..., min_length=1, max_length=200)
    issue_date: date
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = Field(None, max_length=200)
    credential_url: Optional[str] = Field(None, max_length=500)
    skills_covered: List[str] = Field(default_factory=list)


class CertificationCreate(CertificationBase):
    """Schema for creating certification."""
    pass


class CertificationUpdate(BaseModel):
    """Schema for updating certification."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    issuing_organization: Optional[str] = Field(None, min_length=1, max_length=200)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = Field(None, max_length=200)
    credential_url: Optional[str] = Field(None, max_length=500)
    skills_covered: Optional[List[str]] = None


class CertificationResponse(CertificationBase):
    """Schema for certification response."""
    id: UUID
    student_profile_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Complete Profile Response
class CompleteProfileResponse(BaseModel):
    """Complete student profile with all related data."""
    profile: StudentProfileResponse
    education: List[EducationRecordResponse]
    skills: List[StudentSkillResponse]
    projects: List[ProjectResponse]
    certifications: List[CertificationResponse]

    model_config = ConfigDict(from_attributes=True)
