"""
Job and Opportunity Intelligence Models
Companies, job listings, applications, and tracking
"""
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Text, Boolean, Date,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, UUIDMixin, TimestampMixin


class Company(Base, UUIDMixin, TimestampMixin):
    """Company information database"""
    
    __tablename__ = "companies"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    industry: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50))
    headquarters: Mapped[Optional[str]] = mapped_column(String(255))
    founded_year: Mapped[Optional[int]] = mapped_column(Integer)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    culture_tags: Mapped[Optional[List[str]]] = mapped_column(Text().with_variant(Text, "postgresql"))
    tech_stack: Mapped[Optional[List[str]]] = mapped_column(Text().with_variant(Text, "postgresql"))
    
    # Relationships
    job_listings: Mapped[List["JobListing"]] = relationship(back_populates="company")


class JobListing(Base, UUIDMixin, TimestampMixin):
    """Job postings and opportunities"""
    
    __tablename__ = "job_listings"
    
    company_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="SET NULL"),
        index=True
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    role_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(50))
    experience_level: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")
    application_url: Mapped[Optional[str]] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(255))
    posted_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    expires_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True
    )  # active, expired, filled, removed
    last_verified_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    company: Mapped[Optional["Company"]] = relationship(back_populates="job_listings")
    requirements: Mapped[List["JobRequirement"]] = relationship(
        back_populates="job_listing",
        cascade="all, delete-orphan"
    )
    saved_by: Mapped[List["SavedJob"]] = relationship(
        back_populates="job_listing",
        cascade="all, delete-orphan"
    )


class JobRequirement(Base, UUIDMixin, TimestampMixin):
    """Extracted requirements from job listings"""
    
    __tablename__ = "job_requirements"
    
    job_listing_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    skill_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="SET NULL"),
        index=True
    )
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    requirement_type: Mapped[Optional[str]] = mapped_column(String(50))
    importance: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relationships
    job_listing: Mapped["JobListing"] = relationship(back_populates="requirements")


class SavedJob(Base, UUIDMixin, TimestampMixin):
    """Jobs bookmarked by students"""
    
    __tablename__ = "saved_jobs"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_listing_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    match_score: Mapped[Optional[str]] = mapped_column(String(10))
    match_explanation: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    job_listing: Mapped["JobListing"] = relationship(back_populates="saved_by")
    
    __table_args__ = (
        UniqueConstraint("student_profile_id", "job_listing_id", name="unique_saved_job"),
    )


class Application(Base, UUIDMixin, TimestampMixin):
    """Job application tracking"""
    
    __tablename__ = "applications"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_listing_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_listings.id", ondelete="SET NULL")
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="applied",
        nullable=False,
        index=True
    )  # applied, screening, interview, offer, rejected, withdrawn
    applied_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    application_url: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    follow_up_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Relationships
    events: Mapped[List["ApplicationEvent"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan"
    )


class ApplicationEvent(Base, UUIDMixin, TimestampMixin):
    """Timeline of application progress"""
    
    __tablename__ = "application_events"
    
    application_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    application: Mapped["Application"] = relationship(back_populates="events")
