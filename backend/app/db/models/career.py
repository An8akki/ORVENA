"""
Career Intelligence Models
Career roles, discovery sessions, recommendations, and roadmaps
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Text, Boolean, ARRAY, 
    ForeignKey, Numeric, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base, UUIDMixin, TimestampMixin


class CareerRole(Base, UUIDMixin, TimestampMixin):
    """Master career role definitions"""
    
    __tablename__ = "career_roles"
    
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    typical_responsibilities: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    entry_requirements: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    typical_salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    typical_salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")
    growth_outlook: Mapped[Optional[str]] = mapped_column(Text)
    work_environment: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    requirements: Mapped[List["RoleRequirement"]] = relationship(
        back_populates="career_role",
        cascade="all, delete-orphan"
    )


class RoleRequirement(Base, UUIDMixin, TimestampMixin):
    """Skills and qualifications required for roles"""
    
    __tablename__ = "role_requirements"
    
    career_role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    skill_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        index=True
    )
    requirement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[str] = mapped_column(String(20), nullable=False)  # required, preferred, optional
    min_proficiency: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relationships
    career_role: Mapped["CareerRole"] = relationship(back_populates="requirements")


class CareerDiscoverySession(Base, UUIDMixin, TimestampMixin):
    """Career discovery conversation sessions"""
    
    __tablename__ = "career_discovery_sessions"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_type: Mapped[str] = mapped_column(String(50), nullable=False)  # discovery, targeted
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="in_progress",
        index=True
    )  # in_progress, completed, abandoned
    current_phase: Mapped[Optional[str]] = mapped_column(String(50))
    completed_phases: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    responses: Mapped[List["CareerDiscoveryResponse"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan"
    )


class CareerDiscoveryResponse(Base, UUIDMixin, TimestampMixin):
    """Student responses during discovery"""
    
    __tablename__ = "career_discovery_responses"
    
    session_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_discovery_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_category: Mapped[Optional[str]] = mapped_column(String(100))
    phase: Mapped[Optional[str]] = mapped_column(String(50))
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    session: Mapped["CareerDiscoverySession"] = relationship(back_populates="responses")


class CareerGoal(Base, UUIDMixin, TimestampMixin):
    """Student career goals and targets"""
    
    __tablename__ = "career_goals"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    career_role_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    target_timeline: Mapped[Optional[str]] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        index=True
    )  # active, achieved, modified, abandoned
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)


class CareerRecommendation(Base, UUIDMixin, TimestampMixin):
    """AI-generated career recommendations"""
    
    __tablename__ = "career_recommendations"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_discovery_sessions.id", ondelete="SET NULL")
    )
    career_role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    fit_score: Mapped[Optional[Numeric]] = mapped_column(Numeric(3, 2))
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Salary information
    salary_range_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_range_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")
    salary_period: Mapped[str] = mapped_column(String(20), default="annual")  # annual, monthly
    
    # Industry trends and market data
    industry_trend: Mapped[Optional[str]] = mapped_column(Text)
    market_growth: Mapped[Optional[str]] = mapped_column(Text)
    
    strengths: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    gaps: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    opportunities: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    threats: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    recommendation_rank: Mapped[Optional[int]] = mapped_column(Integer)
    student_feedback: Mapped[Optional[str]] = mapped_column(String(20))  # interested, maybe, not-interested
    student_notes: Mapped[Optional[str]] = mapped_column(Text)
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50))
    llm_model: Mapped[Optional[str]] = mapped_column(String(100))
    prompt_version: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relationships
    career_role: Mapped["CareerRole"] = relationship("CareerRole")
    
    __table_args__ = (
        CheckConstraint(
            "fit_score IS NULL OR (fit_score >= 0 AND fit_score <= 1)",
            name="check_fit_score"
        ),
    )


class CareerRoadmap(Base, UUIDMixin, TimestampMixin):
    """Development roadmaps for career goals"""
    
    __tablename__ = "career_roadmaps"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    career_goal_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_goals.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    recommendation_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_recommendations.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    target_duration_weeks: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        index=True
    )  # active, completed, paused, archived
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    milestones: Mapped[List["RoadmapMilestone"]] = relationship(
        back_populates="roadmap",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="check_progress"
        ),
    )


class RoadmapMilestone(Base, UUIDMixin, TimestampMixin):
    """Specific milestones and tasks in roadmaps"""
    
    __tablename__ = "roadmap_milestones"
    
    roadmap_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("career_roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    estimated_hours: Mapped[Optional[int]] = mapped_column(Integer)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        index=True
    )  # pending, in_progress, completed, skipped
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    resources: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    
    # Relationships
    roadmap: Mapped["CareerRoadmap"] = relationship(back_populates="milestones")
