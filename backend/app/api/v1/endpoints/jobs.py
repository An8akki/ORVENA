"""Deterministic job and career matching using profile, resume and discovery evidence."""

import re
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user_id, get_db
from app.core.exceptions import NotFoundError
from app.db.models.career import CareerDiscoverySession
from app.db.models.resume import Resume, ResumeExtraction
from app.db.models.student import EducationRecord, StudentProfile, StudentSkill
from app.services.job_matcher import job_matcher
from app.services.career_signals import extract_skill_evidence, infer_preferred_roles

router = APIRouter()


@router.get("/recommendations")
async def get_job_recommendations(
    db: AsyncSession = Depends(get_db),
    user_id=Depends(get_current_user_id),
) -> List[Dict[str, Any]]:
    """Return real profile-specific career matches without relying on an LLM."""
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Profile not found")

    skills_result = await db.execute(
        select(StudentSkill)
        .where(StudentSkill.student_profile_id == profile.id)
        .options(selectinload(StudentSkill.skill))
    )
    skills = [item.skill.name for item in skills_result.scalars().all() if item.skill]

    education_result = await db.execute(
        select(EducationRecord)
        .where(EducationRecord.student_profile_id == profile.id)
        .order_by(EducationRecord.start_date.desc())
    )
    education = [
        {
            "degree": item.degree,
            "field": item.field_of_study,
            "institution": item.institution_name,
            "start_date": str(item.start_date),
            "end_date": str(item.end_date or ""),
        }
        for item in education_result.scalars().all()
    ]

    resume_result = await db.execute(
        select(ResumeExtraction)
        .join(Resume, Resume.id == ResumeExtraction.resume_id)
        .where(Resume.student_profile_id == profile.id)
        .order_by(Resume.created_at.desc())
        .limit(1)
    )
    extraction = resume_result.scalar_one_or_none()
    resume_text = ""
    if extraction:
        resume_text = extraction.raw_text or ""
        resume_skills = extraction.skills or {}
        if isinstance(resume_skills, dict):
            for values in resume_skills.values():
                if isinstance(values, list):
                    skills.extend(str(value) for value in values if value)

        if not education and isinstance(extraction.education, list):
            education = [item for item in extraction.education if isinstance(item, dict)]

    preferences: Dict[str, Any] = {}
    session_result = await db.execute(
        select(CareerDiscoverySession)
        .where(CareerDiscoverySession.student_profile_id == profile.id)
        .options(selectinload(CareerDiscoverySession.responses))
        .order_by(CareerDiscoverySession.updated_at.desc())
    )
    session = next(
        (item for item in session_result.scalars().all() if item.responses), None
    )
    answer_text = ""
    if session:
        answer_text = " ".join(
            response.response_text
            for response in sorted(session.responses, key=lambda response: response.sequence_number)
        )
        preferences["preferred_roles"] = infer_preferred_roles(answer_text)
        normalized_answers = answer_text.lower()
        if any(term in normalized_answers for term in ("design", "creative", "visual", "figma", "user experience")):
            preferences["preferred_category"] = "Design"
        elif any(term in normalized_answers for term in ("business", "management", "strategy", "product")):
            preferences["preferred_category"] = "Business"

    skills = extract_skill_evidence(resume_text + " " + answer_text, skills)

    matches = job_matcher.match_jobs(
        profile={"id": str(profile.id)},
        skills=list(dict.fromkeys(skills)),
        education=education,
        experience=[],
        preferences=preferences,
    )
    return [
        {
            "id": item["role_name"].lower().replace(" ", "-"),
            "title": item["role_name"],
            "company": "Career path match",
            "location": "Based on your profile and preferences",
            "salaryMin": item["salary_range_min"],
            "salaryMax": item["salary_range_max"],
            "matchScore": item["match_percentage"],
            "growthRate": int(re.search(r"\d+", item["growth_rate"]).group(0)),
            "demandLevel": "High" if item["market_demand"] in ("very_high", "extremely_high", "high") else "Medium",
            "matchedSkills": item["matched_skills"],
            "missingSkills": item["missing_skills"],
            "description": item["reasoning"],
            "requirements": item["missing_skills"] or item["matched_skills"],
            "jobUrl": "https://www.linkedin.com/jobs/search/?keywords=" + item["role_name"].replace(" ", "%20"),
            "companyWebsite": None,
        }
        for item in matches
    ]
