"""
Interview Preparation Models
Interview plans, tasks, practice sessions, and evaluations
"""
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Text, Date,
    ForeignKey, Numeric, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.db.base import Base, UUIDMixin, TimestampMixin


class InterviewPlan(Base, UUIDMixin, TimestampMixin):
    """Structured interview preparation plans"""
    
    __tablename__ = "interview_plans"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_role: Mapped[str] = mapped_column(String(255), nullable=False)
    company_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL")
    )
    application_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL")
    )
    interview_date: Mapped[Optional[date]] = mapped_column(Date)
    plan_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True
    )  # active, completed, archived
    
    # Relationships
    tasks: Mapped[List["PreparationTask"]] = relationship(
        back_populates="interview_plan",
        cascade="all, delete-orphan"
    )
    sessions: Mapped[List["PracticeSession"]] = relationship(
        back_populates="interview_plan",
        cascade="all, delete-orphan"
    )


class PreparationTask(Base, UUIDMixin, TimestampMixin):
    """Tasks in interview preparation plans"""
    
    __tablename__ = "preparation_tasks"
    
    interview_plan_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    task_title: Mapped[str] = mapped_column(String(255), nullable=False)
    task_description: Mapped[Optional[str]] = mapped_column(Text)
    estimated_time_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True
    )  # pending, in_progress, completed, skipped
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    interview_plan: Mapped["InterviewPlan"] = relationship(back_populates="tasks")


class PracticeSession(Base, UUIDMixin, TimestampMixin):
    """Interview practice sessions"""
    
    __tablename__ = "practice_sessions"
    
    interview_plan_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_type: Mapped[str] = mapped_column(String(50), nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    completed_questions: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    interview_plan: Mapped["InterviewPlan"] = relationship(back_populates="sessions")
    attempts: Mapped[List["QuestionAttempt"]] = relationship(
        back_populates="practice_session",
        cascade="all, delete-orphan"
    )


class QuestionAttempt(Base, UUIDMixin, TimestampMixin):
    """Individual question responses and evaluations"""
    
    __tablename__ = "question_attempts"
    
    practice_session_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("practice_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20))
    student_answer: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_score: Mapped[Optional[Numeric]] = mapped_column(Numeric(3, 2))
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    improvements: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    sample_answer: Mapped[Optional[str]] = mapped_column(Text)
    time_taken_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50))
    llm_model: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Relationships
    practice_session: Mapped["PracticeSession"] = relationship(back_populates="attempts")
    
    __table_args__ = (
        CheckConstraint(
            "evaluation_score IS NULL OR (evaluation_score >= 0 AND evaluation_score <= 1)",
            name="check_evaluation_score"
        ),
    )
