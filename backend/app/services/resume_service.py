"""Service layer for resume management."""

import asyncio
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.resume import Resume, ResumeExtraction, ResumeVersion, ResumeReview
from app.schemas.resume import ResumeCreate
from app.services.storage_service import storage_service
from app.services.resume_parser import resume_parser
from app.core.exceptions import NotFoundError, ValidationError


class ResumeService:
    """Service for managing resumes."""

    async def create_resume(
        self,
        db: AsyncSession,
        profile_id: UUID,
        file_content: bytes,
        filename: str,
        content_type: str,
        title: str,
    ) -> Resume:
        """Create a resume from uploaded file."""
        # Validate file size
        file_size = len(file_content)
        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            raise ValidationError("File size exceeds 5MB limit")

        # Validate file type
        allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if content_type not in allowed_types:
            raise ValidationError("Only PDF and DOCX files are supported")

        # Upload to storage
        storage_path = await storage_service.upload_resume(
            file_content, filename, profile_id, content_type
        )

        # Create resume record
        resume = Resume(
            student_profile_id=profile_id,
            title=title,
            source_type="uploaded",
            original_filename=filename,
            content_type=content_type,
            file_size_bytes=file_size,
            storage_path=storage_path,
            status="processing",
            is_primary=False,
        )
        db.add(resume)
        await db.flush()

        # Create version record
        version = ResumeVersion(
            resume_id=resume.id,
            version_number=1,
            storage_path=storage_path,
            file_format="docx" if "wordprocessingml" in content_type else "pdf",
        )
        db.add(version)

        # Extract text and parse with AI
        try:
            resume_text = resume_parser.extract_text(file_content, content_type)
            extraction_method = "rules"
            
            # Parse with AI (with timeout)
            try:
                ai_data = await asyncio.wait_for(
                    resume_parser.parse_resume_with_ai(resume_text),
                    timeout=10.0
                )
                ai_skills = ai_data.get("skills") or {}
                has_ai_data = any((
                    ai_data.get("contact_info"),
                    ai_data.get("summary"),
                    ai_data.get("education"),
                    ai_data.get("experience"),
                    ai_data.get("projects"),
                    ai_data.get("certifications"),
                    any(value for value in ai_skills.values()) if isinstance(ai_skills, dict) else bool(ai_skills),
                ))
                extraction_method = "ai+rules" if has_ai_data else "rules"
            except (asyncio.TimeoutError, Exception) as e:
                print(f"AI parsing failed, using basic extraction: {str(e)}")
                ai_data = {}
                extraction_method = "rules"

            # Keep useful deterministic evidence even when the LLM returns
            # partial JSON or hallucinates dates/roles from unrelated sections.
            extracted_data = resume_parser.enrich_extraction(ai_data, resume_text)

            # Score the resume (statistical - always works)
            from app.services.resume_scorer import resume_scorer
            score_data = resume_scorer.score_resume(extracted_data, resume_text)
            
            # Add score to extracted data
            extracted_data['score'] = score_data

            # Create extraction record
            extraction = ResumeExtraction(
                resume_id=resume.id,
                raw_text=resume_text,
                contact_info=extracted_data.get("contact_info", {}),
                education=extracted_data.get("education", []),
                experience=extracted_data.get("experience", []),
                projects=extracted_data.get("projects", []),
                skills=extracted_data.get("skills", {}),
                certifications=extracted_data.get("certifications", []),
                achievements=extracted_data.get("achievements", []),
                extraction_method=extraction_method,
                is_confirmed=False,
            )
            db.add(extraction)

            resume.status = "ready"
        except Exception as e:
            resume.status = "failed"
            print(f"Resume parsing error: {str(e)}")
            # Even if parsing fails, try to save basic info
            try:
                extraction = ResumeExtraction(
                    resume_id=resume.id,
                    raw_text=locals().get("resume_text", ""),
                    contact_info={},
                    education=[],
                    experience=[],
                    projects=[],
                    skills={},
                    certifications=[],
                    achievements=[{"error": str(e), "status": "parsing_failed"}],
                    extraction_method="fallback",
                    is_confirmed=False,
                )
                db.add(extraction)
            except:
                pass

        await db.commit()
        await db.refresh(resume)
        return resume

    async def get_resumes(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[Resume]:
        """Get all resumes for a profile."""
        result = await db.execute(
            select(Resume)
            .where(Resume.student_profile_id == profile_id)
            .order_by(Resume.is_primary.desc(), Resume.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_resume(
        self, db: AsyncSession, resume_id: UUID, profile_id: UUID
    ) -> Optional[Resume]:
        """Get specific resume."""
        result = await db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.student_profile_id == profile_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_resume_extraction(
        self, db: AsyncSession, resume_id: UUID, profile_id: UUID
    ) -> Optional[ResumeExtraction]:
        """Get resume extraction data."""
        # Verify ownership
        resume = await self.get_resume(db, resume_id, profile_id)
        if not resume:
            raise NotFoundError("Resume not found")

        result = await db.execute(
            select(ResumeExtraction).where(ResumeExtraction.resume_id == resume_id)
        )
        return result.scalar_one_or_none()

    async def set_primary_resume(
        self, db: AsyncSession, resume_id: UUID, profile_id: UUID
    ) -> Resume:
        """Set a resume as primary."""
        # Get resume
        resume = await self.get_resume(db, resume_id, profile_id)
        if not resume:
            raise NotFoundError("Resume not found")

        # Unset other primary resumes
        result = await db.execute(
            select(Resume).where(
                Resume.student_profile_id == profile_id,
                Resume.is_primary == True,
            )
        )
        for other_resume in result.scalars().all():
            other_resume.is_primary = False

        # Set this as primary
        resume.is_primary = True
        await db.commit()
        await db.refresh(resume)
        return resume

    async def delete_resume(
        self, db: AsyncSession, resume_id: UUID, profile_id: UUID
    ) -> None:
        """Delete a resume."""
        resume = await self.get_resume(db, resume_id, profile_id)
        if not resume:
            raise NotFoundError("Resume not found")

        # Delete file from storage if exists
        if resume.storage_path:
            try:
                if not resume.storage_path.startswith("local://"):
                    await storage_service.delete_resume(resume.storage_path)
            except Exception:
                pass  # Continue even if file deletion fails

        await db.delete(resume)
        await db.commit()


# Singleton instance
resume_service = ResumeService()
