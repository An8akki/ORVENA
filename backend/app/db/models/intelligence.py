"""
Intelligence System Models

Career classifications, skill evidence, roadmap templates,
and ML model metadata for the intelligence engine.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Text, Boolean, ARRAY, 
    ForeignKey, Numeric, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base, UUIDMixin, TimestampMixin


class CareerClassification(Base, UUIDMixin, TimestampMixin):
    """Career classification results for students"""
    
    __tablename__ = "career_classifications"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    session_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_discovery_sessions.id", ondelete="SET NULL"),
        index=True
    )
    
    # Classification metadata
    classifier_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # rule_based, ml_model, hybrid
    
    model_version: Mapped[Optional[str]] = mapped_column(String(50))
    confidence_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # high, medium, low, uncertain
    
    # Results (stored as JSONB for flexibility)
    candidate_roles: Mapped[dict] = mapped_column(JSONB, nullable=False)
    missing_information: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Feature snapshot for reproducibility
    input_features: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Student feedback
    student_feedback: Mapped[Optional[str]] = mapped_column(String(50))  # helpful, not_helpful
    selected_role_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True))


class SkillEvidenceRecord(Base, UUIDMixin, TimestampMixin):
    """Evidence records for student skills"""
    
    __tablename__ = "skill_evidence_records"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    skill_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Evidence details
    evidence_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # declared, project, work_experience, education, certification, assessment, resume
    
    evidence_state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # demonstrated, partially_demonstrated, declared_unverified, not_demonstrated, not_assessed
    
    proficiency_level: Mapped[Optional[str]] = mapped_column(
        String(20)
    )  # beginner, intermediate, advanced, expert
    
    source_description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Numeric] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        default=0.5
    )
    
    # Source references
    project_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    
    resume_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE")
    )
    
    certification_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("certifications.id", ondelete="CASCADE")
    )
    
    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column()
    verified_by: Mapped[Optional[str]] = mapped_column(String(50))  # system, manual, assessment
    
    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="check_confidence_score"
        ),
    )


class RoadmapTemplate(Base, UUIDMixin, TimestampMixin):
    """General roadmap templates for career roles"""
    
    __tablename__ = "roadmap_templates"
    
    career_role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    template_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    starting_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # beginner, intermediate, career_changer
    
    # Template content
    description: Mapped[str] = mapped_column(Text, nullable=False)
    prerequisites: Mapped[List[str]] = mapped_column(ARRAY(Text))
    estimated_duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    last_reviewed_date: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    phases: Mapped[List["RoadmapTemplatePhase"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="RoadmapTemplatePhase.phase_number"
    )
    
    __table_args__ = (
        UniqueConstraint("career_role_id", "version", name="unique_template_version"),
    )


class RoadmapTemplatePhase(Base, UUIDMixin, TimestampMixin):
    """Phases within roadmap templates"""
    
    __tablename__ = "roadmap_template_phases"
    
    template_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmap_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    phase_number: Mapped[int] = mapped_column(Integer, nullable=False)
    phase_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Phase details
    objectives: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    estimated_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    prerequisites: Mapped[List[str]] = mapped_column(ARRAY(Text))
    
    # Relationships
    template: Mapped["RoadmapTemplate"] = relationship(back_populates="phases")
    milestones: Mapped[List["RoadmapTemplateMilestone"]] = relationship(
        back_populates="phase",
        cascade="all, delete-orphan",
        order_by="RoadmapTemplateMilestone.sequence_number"
    )
    
    __table_args__ = (
        UniqueConstraint("template_id", "phase_number", name="unique_phase_number"),
        UniqueConstraint("template_id", "phase_id", name="unique_phase_id"),
    )


class RoadmapTemplateMilestone(Base, UUIDMixin, TimestampMixin):
    """Milestones within roadmap template phases"""
    
    __tablename__ = "roadmap_template_milestones"
    
    phase_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmap_template_phases.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    milestone_id: Mapped[str] = mapped_column(String(100), nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Content
    learning_objectives: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    topics: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    activities: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    deliverable: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Requirements
    prerequisites: Mapped[List[str]] = mapped_column(ARRAY(Text))
    estimated_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Completion
    completion_criteria: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    assessment_method: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Resources
    resources: Mapped[Optional[dict]] = mapped_column(JSONB)  # {type, title, url}
    
    # Relationships
    phase: Mapped["RoadmapTemplatePhase"] = relationship(back_populates="milestones")
    
    __table_args__ = (
        UniqueConstraint("phase_id", "sequence_number", name="unique_milestone_sequence"),
        UniqueConstraint("phase_id", "milestone_id", name="unique_milestone_id"),
    )


class ResumeSkillExtraction(Base, UUIDMixin, TimestampMixin):
    """Normalized skills extracted from resumes"""
    
    __tablename__ = "resume_skill_extractions"
    
    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Skill mapping
    raw_skill_text: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_skill_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="SET NULL"),
        index=True
    )
    canonical_skill_name: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Context
    skill_category: Mapped[Optional[str]] = mapped_column(String(50))
    context: Mapped[Optional[str]] = mapped_column(Text)  # Where it appeared in resume
    
    # Normalization metadata
    normalization_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # exact_match, synonym_match, fuzzy_match, manual
    
    confidence_score: Mapped[Numeric] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        default=1.0
    )
    
    # Verification
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column()
    
    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="check_skill_confidence"
        ),
    )


class ResumeRoleMatch(Base, UUIDMixin, TimestampMixin):
    """Career role matches from resume analysis"""
    
    __tablename__ = "resume_role_matches"
    
    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    career_role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Match score
    match_score: Mapped[Numeric] = mapped_column(
        Numeric(3, 2),
        nullable=False
    )
    
    confidence_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # high, medium, low
    
    match_rank: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Evidence
    matching_skills: Mapped[List[str]] = mapped_column(ARRAY(Text))
    missing_skills: Mapped[List[str]] = mapped_column(ARRAY(Text))
    partial_skills: Mapped[List[str]] = mapped_column(ARRAY(Text))
    
    # Explanation
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[List[str]] = mapped_column(ARRAY(Text))
    gaps: Mapped[List[str]] = mapped_column(ARRAY(Text))
    next_steps: Mapped[List[str]] = mapped_column(ARRAY(Text))
    
    # Metadata
    matcher_version: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Student feedback
    student_feedback: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # accurate, somewhat_accurate, not_accurate
    
    __table_args__ = (
        CheckConstraint(
            "match_score >= 0 AND match_score <= 1",
            name="check_match_score"
        ),
        UniqueConstraint("resume_id", "career_role_id", name="unique_resume_role_match"),
    )


class AIGenerationRecord(Base, UUIDMixin, TimestampMixin):
    """Track AI-generated content for audit and reproducibility"""
    
    __tablename__ = "ai_generation_records"
    
    # What was generated
    generation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # career_report, roadmap_personalization, resume_review, etc.
    
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Generation details
    llm_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Input/Output
    input_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    output_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Performance
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    generation_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # success, failed, partial
    
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Validation
    validation_passed: Mapped[Optional[bool]] = mapped_column(Boolean)
    validation_notes: Mapped[Optional[str]] = mapped_column(Text)


class MLModelMetadata(Base, UUIDMixin, TimestampMixin):
    """Metadata for ML models used in the system"""
    
    __tablename__ = "ml_model_metadata"
    
    model_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    
    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # classifier, regressor, clusterer
    
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Model details
    algorithm: Mapped[str] = mapped_column(String(100), nullable=False)
    framework: Mapped[Optional[str]] = mapped_column(String(50))  # scikit-learn, tensorflow, etc.
    
    # Storage
    artifact_path: Mapped[Optional[str]] = mapped_column(String(500))
    preprocessing_pipeline_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Training info
    trained_on_date: Mapped[Optional[datetime]] = mapped_column()
    training_dataset_size: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Performance metrics
    metrics: Mapped[Optional[dict]] = mapped_column(JSONB)  # accuracy, precision, recall, etc.
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_production: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Configuration
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSONB)
    feature_schema: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Validation
    validation_results: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Notes
    description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
