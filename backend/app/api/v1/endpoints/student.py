"""API endpoints for student profile management."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user_id
from app.services.student_service import student_service
from app.services.auth_service import auth_service
from app.schemas.student import (
    StudentProfileCreate,
    StudentProfileUpdate,
    StudentProfileResponse,
    CompleteProfileResponse,
    EducationRecordCreate,
    EducationRecordUpdate,
    EducationRecordResponse,
    StudentSkillCreate,
    StudentSkillUpdate,
    StudentSkillResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    CertificationCreate,
    CertificationUpdate,
    CertificationResponse,
)
from app.core.exceptions import NotFoundError

router = APIRouter()


# Profile Endpoints
@router.get("/profile", response_model=StudentProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Get current user's profile.
    Auto-creates user and profile if they don't exist.
    """
    from app.services.auth_service import AuthService
    
    # Ensure user exists first
    auth_svc = AuthService(db)
    user = await auth_svc.get_user_by_id(user_id)
    
    if not user:
        # Create user record from token
        user = await auth_svc.create_user(user_id, f"{user_id}@supabase.user")
        await db.flush()
    
    # Get or create profile
    profile = await student_service.get_profile(db, user_id)
    
    if not profile:
        # Create profile with basic info
        profile = await auth_svc.create_student_profile(
            user_id=user_id,
            email=user.email,
            full_name=user.email.split('@')[0]
        )
        await db.commit()
        await db.refresh(profile)
    
    return profile


@router.get("/profile/complete", response_model=CompleteProfileResponse)
async def get_complete_profile(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Get complete profile with all related data.
    Auto-creates profile if it doesn't exist.
    """
    profile = await student_service.get_complete_profile(db, user_id)
    
    # Auto-create profile if it doesn't exist
    if not profile:
        from app.services.auth_service import AuthService
        auth_svc = AuthService(db)
        user = await auth_svc.get_user_by_id(user_id)
        
        if user:
            profile = await auth_svc.create_student_profile(
                user_id=user_id,
                email=user.email,
                full_name=user.email.split('@')[0]
            )
            await db.commit()
            # Refresh to get relations
            profile = await student_service.get_complete_profile(db, user_id)
        else:
            raise NotFoundError("User not found")

    return CompleteProfileResponse(
        profile=profile,
        education=profile.education_records or [],
        skills=profile.student_skills or [],
        projects=profile.projects or [],
        certifications=profile.certifications or [],
    )


@router.post(
    "/profile", response_model=StudentProfileResponse, status_code=status.HTTP_201_CREATED
)
async def create_profile(
    profile_data: StudentProfileCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create student profile."""
    profile = await student_service.create_profile(db, user_id, profile_data)
    return profile


@router.patch("/profile", response_model=StudentProfileResponse)
async def update_profile(
    profile_data: StudentProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update student profile."""
    profile = await student_service.update_profile(db, user_id, profile_data)
    return profile


# Education Endpoints
@router.get("/education", response_model=List[EducationRecordResponse])
async def get_education_records(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all education records."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    records = await student_service.get_education_records(db, profile.id)
    return records


@router.get("/education/{record_id}", response_model=EducationRecordResponse)
async def get_education_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get specific education record."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    record = await student_service.get_education_record(db, record_id, profile.id)
    if not record:
        raise NotFoundError("Education record not found")
    return record


@router.post(
    "/education",
    response_model=EducationRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_education_record(
    record_data: EducationRecordCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create education record."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    record = await student_service.create_education_record(db, profile.id, record_data)
    return record


@router.patch("/education/{record_id}", response_model=EducationRecordResponse)
async def update_education_record(
    record_id: UUID,
    record_data: EducationRecordUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update education record."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    record = await student_service.update_education_record(
        db, record_id, profile.id, record_data
    )
    return record


@router.delete("/education/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete education record."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    await student_service.delete_education_record(db, record_id, profile.id)


# Skill Endpoints
@router.get("/skills", response_model=List[StudentSkillResponse])
async def get_student_skills(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all skills."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    skills = await student_service.get_student_skills(db, profile.id)
    return skills


@router.get("/skills/{skill_id}", response_model=StudentSkillResponse)
async def get_student_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get specific skill."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    skill = await student_service.get_student_skill(db, skill_id, profile.id)
    if not skill:
        raise NotFoundError("Skill not found")
    return skill


@router.post(
    "/skills",
    response_model=StudentSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_student_skill(
    skill_data: StudentSkillCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create student skill."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    skill = await student_service.create_student_skill(db, profile.id, skill_data)
    return skill


@router.patch("/skills/{skill_id}", response_model=StudentSkillResponse)
async def update_student_skill(
    skill_id: UUID,
    skill_data: StudentSkillUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update student skill."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    skill = await student_service.update_student_skill(
        db, skill_id, profile.id, skill_data
    )
    return skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete student skill."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    await student_service.delete_student_skill(db, skill_id, profile.id)


# Project Endpoints
@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all projects."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    projects = await student_service.get_projects(db, profile.id)
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get specific project."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    project = await student_service.get_project(db, project_id, profile.id)
    if not project:
        raise NotFoundError("Project not found")
    return project


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create project."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    project = await student_service.create_project(db, profile.id, project_data)
    return project


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update project."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    project = await student_service.update_project(
        db, project_id, profile.id, project_data
    )
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete project."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    await student_service.delete_project(db, project_id, profile.id)


# Certification Endpoints
@router.get("/certifications", response_model=List[CertificationResponse])
async def get_certifications(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all certifications."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    certifications = await student_service.get_certifications(db, profile.id)
    return certifications


@router.get("/certifications/{cert_id}", response_model=CertificationResponse)
async def get_certification(
    cert_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get specific certification."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    certification = await student_service.get_certification(db, cert_id, profile.id)
    if not certification:
        raise NotFoundError("Certification not found")
    return certification


@router.post(
    "/certifications",
    response_model=CertificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_certification(
    cert_data: CertificationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create certification."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    certification = await student_service.create_certification(
        db, profile.id, cert_data
    )
    return certification


@router.patch("/certifications/{cert_id}", response_model=CertificationResponse)
async def update_certification(
    cert_id: UUID,
    cert_data: CertificationUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update certification."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    certification = await student_service.update_certification(
        db, cert_id, profile.id, cert_data
    )
    return certification


@router.delete("/certifications/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certification(
    cert_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete certification."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    await student_service.delete_certification(db, cert_id, profile.id)
