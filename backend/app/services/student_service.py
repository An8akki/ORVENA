"""Service layer for student profile management."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.student import (
    StudentProfile,
    EducationRecord,
    Skill,
    StudentSkill,
    Project,
    Certification,
)
from app.schemas.student import (
    StudentProfileCreate,
    StudentProfileUpdate,
    EducationRecordCreate,
    EducationRecordUpdate,
    StudentSkillCreate,
    StudentSkillUpdate,
    ProjectCreate,
    ProjectUpdate,
    CertificationCreate,
    CertificationUpdate,
)
from app.core.exceptions import NotFoundError, ConflictError


class StudentService:
    """Service for managing student profiles and related data."""

    # Profile Management
    async def get_profile(
        self, db: AsyncSession, user_id: UUID
    ) -> Optional[StudentProfile]:
        """Get student profile by user ID."""
        result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_complete_profile(
        self, db: AsyncSession, user_id: UUID
    ) -> Optional[StudentProfile]:
        """Get student profile with all related data."""
        result = await db.execute(
            select(StudentProfile)
            .where(StudentProfile.user_id == user_id)
            .options(
                selectinload(StudentProfile.education_records),
                selectinload(StudentProfile.student_skills).selectinload(
                    StudentSkill.skill
                ),
                selectinload(StudentProfile.projects),
                selectinload(StudentProfile.certifications),
            )
        )
        return result.scalar_one_or_none()

    async def create_profile(
        self, db: AsyncSession, user_id: UUID, profile_data: StudentProfileCreate
    ) -> StudentProfile:
        """Create student profile."""
        # Check if profile already exists
        existing = await self.get_profile(db, user_id)
        if existing:
            raise ConflictError("Profile already exists for this user")

        profile = StudentProfile(user_id=user_id, **profile_data.model_dump())
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

    async def update_profile(
        self,
        db: AsyncSession,
        user_id: UUID,
        profile_data: StudentProfileUpdate,
    ) -> StudentProfile:
        """Update student profile."""
        profile = await self.get_profile(db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")

        # Update only provided fields
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        profile.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(profile)
        return profile

    # Education Management
    async def get_education_records(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[EducationRecord]:
        """Get all education records for a profile."""
        result = await db.execute(
            select(EducationRecord)
            .where(EducationRecord.student_profile_id == profile_id)
            .order_by(EducationRecord.start_date.desc())
        )
        return list(result.scalars().all())

    async def get_education_record(
        self, db: AsyncSession, record_id: UUID, profile_id: UUID
    ) -> Optional[EducationRecord]:
        """Get specific education record."""
        result = await db.execute(
            select(EducationRecord).where(
                EducationRecord.id == record_id,
                EducationRecord.student_profile_id == profile_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_education_record(
        self, db: AsyncSession, profile_id: UUID, record_data: EducationRecordCreate
    ) -> EducationRecord:
        """Create education record."""
        record = EducationRecord(
            student_profile_id=profile_id, **record_data.model_dump()
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    async def update_education_record(
        self,
        db: AsyncSession,
        record_id: UUID,
        profile_id: UUID,
        record_data: EducationRecordUpdate,
    ) -> EducationRecord:
        """Update education record."""
        record = await self.get_education_record(db, record_id, profile_id)
        if not record:
            raise NotFoundError("Education record not found")

        update_data = record_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

        record.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(record)
        return record

    async def delete_education_record(
        self, db: AsyncSession, record_id: UUID, profile_id: UUID
    ) -> None:
        """Delete education record."""
        record = await self.get_education_record(db, record_id, profile_id)
        if not record:
            raise NotFoundError("Education record not found")

        await db.delete(record)
        await db.commit()

    # Skill Management
    async def get_or_create_skill(
        self, db: AsyncSession, name: str, category: str
    ) -> Skill:
        """Get existing skill or create new one."""
        result = await db.execute(
            select(Skill).where(Skill.name == name, Skill.category == category)
        )
        skill = result.scalar_one_or_none()

        if not skill:
            skill = Skill(name=name, category=category)
            db.add(skill)
            await db.commit()
            await db.refresh(skill)

        return skill

    async def get_student_skills(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[StudentSkill]:
        """Get all skills for a student."""
        result = await db.execute(
            select(StudentSkill)
            .where(StudentSkill.student_profile_id == profile_id)
            .options(selectinload(StudentSkill.skill))
        )
        return list(result.scalars().all())

    async def get_student_skill(
        self, db: AsyncSession, skill_id: UUID, profile_id: UUID
    ) -> Optional[StudentSkill]:
        """Get specific student skill."""
        result = await db.execute(
            select(StudentSkill)
            .where(
                StudentSkill.id == skill_id,
                StudentSkill.student_profile_id == profile_id,
            )
            .options(selectinload(StudentSkill.skill))
        )
        return result.scalar_one_or_none()

    async def create_student_skill(
        self, db: AsyncSession, profile_id: UUID, skill_data: StudentSkillCreate
    ) -> StudentSkill:
        """Create student skill."""
        # Get or create the skill in master catalog
        skill = await self.get_or_create_skill(
            db, skill_data.skill_name, skill_data.skill_category
        )

        # Check if student already has this skill
        existing = await db.execute(
            select(StudentSkill).where(
                StudentSkill.student_profile_id == profile_id,
                StudentSkill.skill_id == skill.id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Skill already exists for this student")

        student_skill = StudentSkill(
            student_profile_id=profile_id,
            skill_id=skill.id,
            **skill_data.model_dump(exclude={"skill_name", "skill_category"}),
        )
        db.add(student_skill)
        await db.commit()
        await db.refresh(student_skill)
        await db.refresh(student_skill, ["skill"])
        return student_skill

    async def update_student_skill(
        self,
        db: AsyncSession,
        skill_id: UUID,
        profile_id: UUID,
        skill_data: StudentSkillUpdate,
    ) -> StudentSkill:
        """Update student skill."""
        student_skill = await self.get_student_skill(db, skill_id, profile_id)
        if not student_skill:
            raise NotFoundError("Student skill not found")

        update_data = skill_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student_skill, field, value)

        student_skill.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(student_skill)
        await db.refresh(student_skill, ["skill"])
        return student_skill

    async def delete_student_skill(
        self, db: AsyncSession, skill_id: UUID, profile_id: UUID
    ) -> None:
        """Delete student skill."""
        student_skill = await self.get_student_skill(db, skill_id, profile_id)
        if not student_skill:
            raise NotFoundError("Student skill not found")

        await db.delete(student_skill)
        await db.commit()

    # Project Management
    async def get_projects(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[Project]:
        """Get all projects for a profile."""
        result = await db.execute(
            select(Project)
            .where(Project.student_profile_id == profile_id)
            .order_by(Project.start_date.desc())
        )
        return list(result.scalars().all())

    async def get_project(
        self, db: AsyncSession, project_id: UUID, profile_id: UUID
    ) -> Optional[Project]:
        """Get specific project."""
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.student_profile_id == profile_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_project(
        self, db: AsyncSession, profile_id: UUID, project_data: ProjectCreate
    ) -> Project:
        """Create project."""
        project = Project(
            student_profile_id=profile_id, **project_data.model_dump()
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    async def update_project(
        self,
        db: AsyncSession,
        project_id: UUID,
        profile_id: UUID,
        project_data: ProjectUpdate,
    ) -> Project:
        """Update project."""
        project = await self.get_project(db, project_id, profile_id)
        if not project:
            raise NotFoundError("Project not found")

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        project.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(project)
        return project

    async def delete_project(
        self, db: AsyncSession, project_id: UUID, profile_id: UUID
    ) -> None:
        """Delete project."""
        project = await self.get_project(db, project_id, profile_id)
        if not project:
            raise NotFoundError("Project not found")

        await db.delete(project)
        await db.commit()

    # Certification Management
    async def get_certifications(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[Certification]:
        """Get all certifications for a profile."""
        result = await db.execute(
            select(Certification)
            .where(Certification.student_profile_id == profile_id)
            .order_by(Certification.issue_date.desc())
        )
        return list(result.scalars().all())

    async def get_certification(
        self, db: AsyncSession, cert_id: UUID, profile_id: UUID
    ) -> Optional[Certification]:
        """Get specific certification."""
        result = await db.execute(
            select(Certification).where(
                Certification.id == cert_id,
                Certification.student_profile_id == profile_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_certification(
        self, db: AsyncSession, profile_id: UUID, cert_data: CertificationCreate
    ) -> Certification:
        """Create certification."""
        certification = Certification(
            student_profile_id=profile_id, **cert_data.model_dump()
        )
        db.add(certification)
        await db.commit()
        await db.refresh(certification)
        return certification

    async def update_certification(
        self,
        db: AsyncSession,
        cert_id: UUID,
        profile_id: UUID,
        cert_data: CertificationUpdate,
    ) -> Certification:
        """Update certification."""
        certification = await self.get_certification(db, cert_id, profile_id)
        if not certification:
            raise NotFoundError("Certification not found")

        update_data = cert_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(certification, field, value)

        certification.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(certification)
        return certification

    async def delete_certification(
        self, db: AsyncSession, cert_id: UUID, profile_id: UUID
    ) -> None:
        """Delete certification."""
        certification = await self.get_certification(db, cert_id, profile_id)
        if not certification:
            raise NotFoundError("Certification not found")

        await db.delete(certification)
        await db.commit()


# Singleton instance
student_service = StudentService()
