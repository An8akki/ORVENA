"""API endpoints for resume management."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user_id
from app.services.student_service import student_service
from app.services.resume_service import resume_service
from app.schemas.resume import (
    ResumeResponse,
    ResumeExtractionResponse,
)
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Upload and parse a resume."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

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
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    resumes = await resume_service.get_resumes(db, profile.id)
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get specific resume."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

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
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    extraction = await resume_service.get_resume_extraction(db, resume_id, profile.id)
    if not extraction:
        raise NotFoundError("Extraction data not found")

    return extraction


@router.post("/{resume_id}/set-primary", response_model=ResumeResponse)
async def set_primary_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Set a resume as primary."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    resume = await resume_service.set_primary_resume(db, resume_id, profile.id)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete a resume."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    await resume_service.delete_resume(db, resume_id, profile.id)
