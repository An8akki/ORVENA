"""
Project Launchpad Database Models

Supports project lifecycle management, milestones, 5-dimension evaluation,
outcome intelligence pathways, project showcase, and opportunity tracking.
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Integer, Text, Boolean, ARRAY, 
    ForeignKey, Numeric, CheckConstraint, UniqueConstraint, Date, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base, UUIDMixin, TimestampMixin


class ProjectMilestone(Base, UUIDMixin, TimestampMixin):
    """Milestones and tasks within a student project"""
    
    __tablename__ = "project_milestones"
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    phase: Mapped[str] = mapped_column(String(50), nullable=False, default="Implementation")
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="not_started",
        index=True
    )  # not_started, in_progress, blocked, completed
    target_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    deliverables: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    resources: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    blocker_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="launchpad_milestones")


class ProjectAssessment(Base, UUIDMixin, TimestampMixin):
    """5-Dimension Rule-Based Project Evaluation Record"""
    
    __tablename__ = "project_assessments"
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    overall_score: Mapped[Numeric] = mapped_column(Numeric(4, 1), nullable=False)  # 0 to 100
    overall_rating: Mapped[str] = mapped_column(String(50), nullable=False)  # Early Concept, Developing, Functional Prototype, Validated, Exemplary
    dimension_scores: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    strengths: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    missing_evidence: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    improvement_priorities: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    recommended_milestone: Mapped[Optional[str]] = mapped_column(Text)
    reassessment_conditions: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    raw_answers: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="launchpad_assessments")


class ProjectOutcomeAssessment(Base, UUIDMixin, TimestampMixin):
    """Strategic Outcome Intelligence Analysis across 6 Pathways"""
    
    __tablename__ = "project_outcome_assessments"
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    selected_goal: Mapped[Optional[str]] = mapped_column(String(100))
    top_pathway: Mapped[str] = mapped_column(String(50), nullable=False)
    pathways: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    readiness_summary: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="launchpad_outcomes")


class ProjectShowcase(Base, UUIDMixin, TimestampMixin):
    """Shareable Project Portfolio Showcase"""
    
    __tablename__ = "project_showcases"
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(255))
    problem_solution_summary: Mapped[Optional[str]] = mapped_column(Text)
    key_contributions: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    outcomes_metrics: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    media_urls: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    skills_highlighted: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="launchpad_showcase")


class Opportunity(Base, UUIDMixin, TimestampMixin):
    """Verified Directory of Competitions, Fellowships, Grants, and Accelerators"""
    
    __tablename__ = "opportunities"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    opportunity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    official_url: Mapped[str] = mapped_column(String(500), nullable=False)
    eligibility_requirements: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    beneficiary_type: Mapped[str] = mapped_column(String(100), default="individual_student")
    geographic_scope: Mapped[str] = mapped_column(String(100), default="Global")
    domains: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    required_project_stage: Mapped[str] = mapped_column(String(50), default="any")
    funding_amount_or_benefits: Mapped[Optional[str]] = mapped_column(String(255))
    is_monetary: Mapped[bool] = mapped_column(Boolean, default=False)
    application_deadline: Mapped[Optional[date]] = mapped_column(Date)
    is_rolling: Mapped[bool] = mapped_column(Boolean, default=False)
    application_instructions: Mapped[Optional[str]] = mapped_column(Text)
    date_last_verified: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    source_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    applications: Mapped[List["ProjectOpportunityApplication"]] = relationship(
        "ProjectOpportunityApplication",
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )


class ProjectOpportunityApplication(Base, UUIDMixin, TimestampMixin):
    """Student Saved and Tracked Applications for Opportunities"""
    
    __tablename__ = "project_opportunity_applications"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    project_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True
    )
    opportunity_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="saved",
        nullable=False,
        index=True
    )  # saved, researching, preparing, submitted, accepted, rejected, closed
    notes: Mapped[Optional[str]] = mapped_column(Text)
    submission_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="applications")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="launchpad_applications")
    
    __table_args__ = (
        UniqueConstraint(
            "student_profile_id", "opportunity_id", "project_id",
            name="unique_student_opportunity_project"
        ),
    )
