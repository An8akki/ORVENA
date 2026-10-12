"""
Student Profile Models
Student information, education, skills, projects, and certifications
"""
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Text, Date, Boolean, ARRAY, 
    ForeignKey, Numeric, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base, UUIDMixin, TimestampMixin


class StudentProfile(Base, UUIDMixin, TimestampMixin):
    """Student profile information"""
    
    __tablename__ = "student_profiles"
    
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    
    # URLs
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Career details
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer)
    current_status: Mapped[Optional[str]] = mapped_column(String(50))  # student, graduate, employed
    availability_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Preferences
    preferred_locations: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    remote_preference: Mapped[Optional[str]] = mapped_column(String(20))  # remote, hybrid, onsite, flexible
    work_authorization: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Salary expectations
    expected_salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    expected_salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    education_records: Mapped[List["EducationRecord"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan"
    )
    preferences: Mapped[Optional["StudentPreferences"]] = relationship(
        back_populates="student_profile",
        uselist=False,
        cascade="all, delete-orphan"
    )
    skills: Mapped[List["StudentSkill"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan"
    )
    certifications: Mapped[List["Certification"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        CheckConstraint(
            "expected_salary_min IS NULL OR expected_salary_max IS NULL OR expected_salary_min <= expected_salary_max",
            name="check_salary_range"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<StudentProfile(id={self.id}, name={self.full_name})>"


class EducationRecord(Base, UUIDMixin, TimestampMixin):
    """Educational background"""
    
    __tablename__ = "education_records"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(100), nullable=False)  # Bachelor, Master, PhD
    field_of_study: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    gpa: Mapped[Optional[Numeric]] = mapped_column(Numeric(3, 2))
    gpa_scale: Mapped[Optional[Numeric]] = mapped_column(Numeric(3, 2))
    achievements: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    relevant_coursework: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    
    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship(back_populates="education_records")
    
    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="check_education_dates"
        ),
    )


class StudentPreferences(Base, UUIDMixin, TimestampMixin):
    """Career and job search preferences"""
    
    __tablename__ = "student_preferences"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    preferred_industries: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    preferred_company_sizes: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    work_environment_preferences: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    values: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    avoid_industries: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    willing_to_relocate: Mapped[bool] = mapped_column(Boolean, default=False)
    maximum_commute_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    requires_sponsorship: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship(back_populates="preferences")


class Skill(Base, UUIDMixin, TimestampMixin):
    """Master skill catalog"""
    
    __tablename__ = "skills"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # technical, soft, domain
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    aliases: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    
    # Relationships
    student_skills: Mapped[List["StudentSkill"]] = relationship(back_populates="skill")


class StudentSkill(Base, UUIDMixin, TimestampMixin):
    """Student skill proficiency with evidence"""
    
    __tablename__ = "student_skills"
    
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
    proficiency_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )  # beginner, intermediate, advanced, expert
    years_of_experience: Mapped[Optional[Numeric]] = mapped_column(Numeric(3, 1))
    evidence_type: Mapped[Optional[str]] = mapped_column(String(50))
    evidence_description: Mapped[Optional[str]] = mapped_column(Text)
    last_used_date: Mapped[Optional[date]] = mapped_column(Date)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(back_populates="student_skills")
    
    __table_args__ = (
        UniqueConstraint("student_profile_id", "skill_id", name="unique_student_skill"),
    )


class Project(Base, UUIDMixin, TimestampMixin):
    """Student projects with detailed information"""
    
    __tablename__ = "projects"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(100))
    technologies: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    demo_url: Mapped[Optional[str]] = mapped_column(String(500))
    achievements: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    team_size: Mapped[Optional[int]] = mapped_column(Integer)
    impact_metrics: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    visibility: Mapped[str] = mapped_column(String(20), default="public")  # public, private
    
    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship(back_populates="projects")
    
    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="check_project_dates"
        ),
    )


class Certification(Base, UUIDMixin, TimestampMixin):
    """Professional certifications and courses"""
    
    __tablename__ = "certifications"
    
    student_profile_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_organization: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    credential_id: Mapped[Optional[str]] = mapped_column(String(255))
    credential_url: Mapped[Optional[str]] = mapped_column(String(500))
    skills_covered: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    
    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship(back_populates="certifications")
