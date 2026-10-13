"""API endpoints for resume management."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user_id
from app.services.student_service import student_service
from app.services.resume_service import resume_service
from app.services.auth_service import AuthService
from app.schemas.resume import (
    ResumeResponse,
    ResumeExtractionResponse,
    ResumeAnalysisResponse,
)
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


async def get_or_create_profile(db: AsyncSession, user_id: UUID):
    """Create the application profile for authenticated users who lack one."""
    profile = await student_service.get_profile(db, user_id)
    if profile:
        return profile

    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        user = await auth_service.create_user(user_id, f"{user_id}@supabase.user")
        await db.flush()
    profile = await auth_service.create_student_profile(
        user_id=user_id,
        email=user.email,
        full_name=user.email.split("@")[0],
    )
    await db.flush()
    return profile


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Upload and parse a resume."""
    profile = await get_or_create_profile(db, user_id)

    # Read file content
    file_content = await file.read()

    # Create resume
    resume = await resume_service.create_resume(
        db,
        profile.id,
        file_content,
        file.filename or "resume.pdf",
        file.content_type or "application/pdf",
        title,
    )

    return resume


@router.get("", response_model=List[ResumeResponse])
async def get_resumes(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all resumes."""
    profile = await get_or_create_profile(db, user_id)

    resumes = await resume_service.get_resumes(db, profile.id)
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get specific resume."""
    profile = await get_or_create_profile(db, user_id)

    resume = await resume_service.get_resume(db, resume_id, profile.id)
    if not resume:
        raise NotFoundError("Resume not found")

    return resume


@router.get("/{resume_id}/extraction", response_model=ResumeExtractionResponse)
async def get_resume_extraction(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get extracted resume data."""
    profile = await get_or_create_profile(db, user_id)

    extraction = await resume_service.get_resume_extraction(db, resume_id, profile.id)
    if not extraction:
        raise NotFoundError("Extraction data not found")

    return extraction


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Score the saved resume with the local statistical analyzer."""
    profile = await get_or_create_profile(db, user_id)
    extraction = await resume_service.get_resume_extraction(db, resume_id, profile.id)
    if not extraction:
        raise NotFoundError("Resume analysis is not available yet")

    from app.services.resume_parser import resume_parser
    from app.services.resume_scorer import resume_scorer

    raw_text = extraction.raw_text or ""
    stored_data = {
        "contact_info": extraction.contact_info or {},
        "education": extraction.education or [],
        "experience": extraction.experience or [],
        "projects": extraction.projects or [],
        "skills": extraction.skills or {},
        "certifications": extraction.certifications or [],
        "achievements": extraction.achievements or [],
    }
    enriched = resume_parser.enrich_extraction(stored_data, raw_text)
    score = resume_scorer.score_resume(enriched, raw_text)
    # Repair incomplete or hallucinated legacy extraction records as they are
    # analyzed, so later reads show the same evidence used for the score.
    for field in ("contact_info", "education", "experience", "projects", "skills", "certifications", "achievements"):
        setattr(extraction, field, enriched.get(field))
    await db.commit()
    return ResumeAnalysisResponse(
        resume_id=resume_id,
        **score,
        extraction_method=extraction.extraction_method,
        normalized_extraction={
            **enriched,
            "raw_text": raw_text,
            "is_confirmed": extraction.is_confirmed,
            "extraction_method": extraction.extraction_method,
        },
    )


@router.post("/{resume_id}/set-primary", response_model=ResumeResponse)
async def set_primary_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Set a resume as primary."""
    profile = await get_or_create_profile(db, user_id)

    resume = await resume_service.set_primary_resume(db, resume_id, profile.id)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete a resume."""
    profile = await get_or_create_profile(db, user_id)

    await resume_service.delete_resume(db, resume_id, profile.id)
