"""
Resume Intelligence Models
Resume documents, extractions, reviews, and versions
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Text, Boolean, 
    ForeignKey, Numeric, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


class Resume(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Resume documents and metadata"""
    
    __tablename__ = "resumes"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)  # uploaded, built
    original_filename: Mapped[Optional[str]] = mapped_column(String(255))
    storage_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    content_type: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(
        String(20),
        default="processing",
        nullable=False,
        index=True
    )  # processing, ready, failed
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    extraction: Mapped[Optional["ResumeExtraction"]] = relationship(
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan"
    )
    versions: Mapped[List["ResumeVersion"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan"
    )
    reviews: Mapped[List["ResumeReview"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan"
    )


class ResumeExtraction(Base, UUIDMixin, TimestampMixin):
    """Extracted structured data from resumes"""
    
    __tablename__ = "resume_extractions"
    
    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    contact_info: Mapped[Optional[dict]] = mapped_column(JSONB)
    education: Mapped[Optional[dict]] = mapped_column(JSONB)
    experience: Mapped[Optional[dict]] = mapped_column(JSONB)
    projects: Mapped[Optional[dict]] = mapped_column(JSONB)
    skills: Mapped[Optional[dict]] = mapped_column(JSONB)
    certifications: Mapped[Optional[dict]] = mapped_column(JSONB)
    achievements: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column()
    extraction_method: Mapped[Optional[str]] = mapped_column(String(50))  # ai, manual
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50))
    llm_model: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Relationships
    resume: Mapped["Resume"] = relationship(back_populates="extraction")


class ResumeVersion(Base, UUIDMixin, TimestampMixin):
    """Version history for resumes"""
    
    __tablename__ = "resume_versions"
    
    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_format: Mapped[str] = mapped_column(String(10), nullable=False)  # pdf, docx
    changes_summary: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    resume: Mapped["Resume"] = relationship(back_populates="versions")
    
    __table_args__ = (
        UniqueConstraint("resume_id", "version_number", name="unique_resume_version"),
    )


class ResumeReview(Base, UUIDMixin, TimestampMixin):
    """AI-generated resume reviews and feedback"""
    
    __tablename__ = "resume_reviews"
    
    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    review_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # general, job-tailored
    target_job_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_listings.id", ondelete="SET NULL")
    )
    overall_score: Mapped[Optional[Numeric]] = mapped_column(Numeric(3, 2))
    overall_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50))
    llm_model: Mapped[Optional[str]] = mapped_column(String(100))
    prompt_version: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relationships
    resume: Mapped["Resume"] = relationship(back_populates="reviews")
    findings: Mapped[List["ResumeReviewFinding"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        CheckConstraint(
            "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 1)",
            name="check_review_score"
        ),
    )


class ResumeReviewFinding(Base, UUIDMixin, TimestampMixin):
    """Specific findings and suggestions from reviews"""
    
    __tablename__ = "resume_review_findings"
    
    review_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )  # critical, major, minor, suggestion
    section: Mapped[Optional[str]] = mapped_column(String(100))
    current_text: Mapped[Optional[str]] = mapped_column(Text)
    suggested_improvement: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[Optional[str]] = mapped_column(Text)
    sequence_number: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relationships
    review: Mapped["ResumeReview"] = relationship(back_populates="findings")
