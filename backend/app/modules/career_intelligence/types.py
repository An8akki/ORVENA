"""
Type definitions for Career Intelligence module.

Shared types, enums, and base schemas used across classification,
evidence collection, and roadmap generation.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class EvidenceType(str, Enum):
    """Types of evidence for skills and experience."""
    DECLARED = "declared"  # Student claims the skill
    PROJECT = "project"  # Demonstrated in project
    WORK_EXPERIENCE = "work_experience"  # From internship/job
    EDUCATION = "education"  # From coursework
    CERTIFICATION = "certification"  # From certificate
    ASSESSMENT = "assessment"  # From test/evaluation
    RESUME = "resume"  # Found in resume


class EvidenceState(str, Enum):
    """State of skill evidence."""
    DEMONSTRATED = "demonstrated"  # Strong evidence exists
    PARTIALLY_DEMONSTRATED = "partially_demonstrated"  # Some evidence
    DECLARED_UNVERIFIED = "declared_unverified"  # Claimed but not proven
    NOT_DEMONSTRATED = "not_demonstrated"  # No evidence found
    NOT_ASSESSED = "not_assessed"  # Haven't checked yet


class SkillCategory(str, Enum):
    """Skill categories."""
    TECHNICAL = "technical"
    SOFT_SKILL = "soft_skill"
    DOMAIN = "domain"
    TOOL = "tool"
    LANGUAGE = "language"


class ProficiencyLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class RequirementImportance(str, Enum):
    """Importance level for role requirements."""
    REQUIRED = "required"
    PREFERRED = "preferred"
    OPTIONAL = "optional"


class ConfidenceLevel(str, Enum):
    """Confidence in classification results."""
    HIGH = "high"  # Strong evidence, clear match
    MEDIUM = "medium"  # Reasonable evidence
    LOW = "low"  # Weak evidence, needs clarification
    UNCERTAIN = "uncertain"  # Insufficient information


# Base Schemas

class SkillEvidence(BaseModel):
    """Evidence for a specific skill."""
    model_config = ConfigDict(from_attributes=True)
    
    skill_name: str
    skill_id: Optional[UUID] = None
    evidence_type: EvidenceType
    evidence_state: EvidenceState
    proficiency_level: Optional[ProficiencyLevel] = None
    source_description: str  # Where the evidence came from
    confidence: float = Field(ge=0.0, le=1.0)


class StudentFeatures(BaseModel):
    """Normalized features from student profile and discovery."""
    model_config = ConfigDict(from_attributes=True)
    
    # Interests (derived from discovery)
    interests: List[str] = Field(default_factory=list)
    
    # Work preferences
    work_preferences: Dict[str, Any] = Field(default_factory=dict)
    
    # Skills with evidence
    skills: List[SkillEvidence] = Field(default_factory=list)
    
    # Education
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    
    # Experience
    has_projects: bool = False
    project_count: int = 0
    has_internship: bool = False
    work_experience_months: int = 0
    
    # Constraints
    available_hours_per_week: Optional[int] = None
    target_timeline_weeks: Optional[int] = None
    willing_to_relocate: bool = False
    requires_sponsorship: bool = False
    
    # Goals
    salary_expectations: Optional[Dict[str, int]] = None
    preferred_industries: List[str] = Field(default_factory=list)


class RoleRequirement(BaseModel):
    """A requirement for a specific role."""
    model_config = ConfigDict(from_attributes=True)
    
    requirement_type: str  # skill, education, experience
    requirement_text: str
    importance: RequirementImportance
    min_proficiency: Optional[ProficiencyLevel] = None
    skill_name: Optional[str] = None


class RoleFitScore(BaseModel):
    """Score indicating how well a student fits a role."""
    model_config = ConfigDict(from_attributes=True)
    
    role_id: UUID
    role_name: str
    role_category: str
    
    # Overall score
    fit_score: float = Field(ge=0.0, le=1.0)
    confidence: ConfidenceLevel
    
    # Evidence breakdown
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    partially_matched_skills: List[str] = Field(default_factory=list)
    
    # Strengths and gaps
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    
    # Explanation
    reasoning: str
    
    # Recommended actions
    next_steps: List[str] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    """Result from career classification."""
    model_config = ConfigDict(from_attributes=True)
    
    student_profile_id: UUID
    classification_id: Optional[UUID] = None
    
    # Candidate roles (ranked)
    candidate_roles: List[RoleFitScore]
    
    # Classification metadata
    confidence: ConfidenceLevel
    model_version: Optional[str] = None
    classifier_type: str  # "rule_based", "ml_model", "hybrid"
    
    # Missing information
    missing_information: List[str] = Field(default_factory=list)
    suggested_followup_questions: List[str] = Field(default_factory=list)
    
    # Summary
    summary: str
    
    # Timestamp
    classified_at: datetime = Field(default_factory=datetime.utcnow)


class MilestoneStatus(str, Enum):
    """Status of a roadmap milestone."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class RoadmapPhase(BaseModel):
    """A phase in a career roadmap."""
    model_config = ConfigDict(from_attributes=True)
    
    phase_id: str
    phase_number: int
    title: str
    description: str
    objectives: List[str]
    estimated_hours: int
    prerequisites: List[str] = Field(default_factory=list)


class RoadmapMilestoneData(BaseModel):
    """Structured milestone data."""
    model_config = ConfigDict(from_attributes=True)
    
    milestone_id: str
    title: str
    description: str
    phase_id: str
    
    # Content
    learning_objectives: List[str]
    topics: List[str]
    activities: List[str]
    deliverable: str
    
    # Requirements
    prerequisites: List[str] = Field(default_factory=list)
    estimated_hours: int
    
    # Completion
    completion_criteria: List[str]
    assessment_method: Optional[str] = None
    
    # Resources
    resources: List[Dict[str, str]] = Field(default_factory=list)
    
    # Status
    status: MilestoneStatus = MilestoneStatus.PENDING
    sequence_number: int
