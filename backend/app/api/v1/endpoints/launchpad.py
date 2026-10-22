"""
API Endpoints for Orvena Project Launchpad
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user_id, get_optional_user_id
from app.services.student_service import student_service
from app.services.auth_service import AuthService
from app.services.launchpad_ideas import project_ideas_service
from app.services.launchpad_planner import project_planner_service
from app.services.launchpad_evaluator import project_evaluator_service
from app.services.launchpad_outcomes import project_outcome_intelligence_service
from app.services.launchpad_opportunities import project_opportunities_service
from app.services.launchpad_service import launchpad_service
from app.services.career_recommendation_service import career_recommendation_service

from app.schemas.launchpad import (
    ProjectIdea,
    IdeaRecommendationRequest,
    IdeaRecommendationResponse,
    PlanGenerationRequest,
    GeneratedProjectPlan,
    LaunchpadProjectCreate,
    LaunchpadProjectUpdate,
    LaunchpadProjectResponse,
    LaunchpadProjectDetailResponse,
    ProjectMilestoneCreate,
    ProjectMilestoneUpdate,
    ProjectMilestoneResponse,
    ProjectEvaluationRequest,
    ProjectEvaluationResponse,
    OutcomeIntelligenceRequest,
    OutcomeIntelligenceResponse,
    ApplyPathwayRequest,
    ShowcaseUpdateRequest,
    ShowcaseResponse,
    OpportunityResponse,
    OpportunityApplicationCreate,
    OpportunityApplicationResponse,
)
from app.core.exceptions import NotFoundError, UnauthorizedError

router = APIRouter()


async def get_or_create_student_profile(db: AsyncSession, user_id: UUID):
    """Ensures profile exists for authenticated user."""
    profile = await student_service.get_profile(db, user_id)
    if profile:
        return profile

    auth_svc = AuthService(db)
    user = await auth_svc.get_user_by_id(user_id)
    if not user:
        user = await auth_svc.create_user(user_id, f"{user_id}@supabase.user")
        await db.flush()

    profile = await auth_svc.create_student_profile(
        user_id=user_id,
        email=user.email,
        full_name=user.email.split("@")[0] if user.email else "Student",
    )
    await db.flush()
    return profile


# -------------------------------------------------------------
# Idea Catalogue & Recommendations
# -------------------------------------------------------------
@router.get("/ideas", response_model=List[ProjectIdea])
async def list_project_ideas(
    domain: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    max_duration_weeks: Optional[int] = Query(None),
    goal: Optional[str] = Query(None),
    technology: Optional[str] = Query(None),
):
    """Browse the curated project ideas catalogue with deterministic filters."""
    return project_ideas_service.list_ideas(
        domain=domain,
        difficulty=difficulty,
        max_duration_weeks=max_duration_weeks,
        goal=goal,
        technology=technology,
    )


@router.get("/ideas/{idea_id}", response_model=ProjectIdea)
async def get_project_idea(idea_id: str):
    """Get full details of a specific project idea from the catalogue."""
    idea = project_ideas_service.get_idea_by_id(idea_id)
    if not idea:
        raise NotFoundError(f"Project idea '{idea_id}' not found in catalogue")
    return idea


@router.post("/ideas/recommend", response_model=IdeaRecommendationResponse)
async def recommend_project_ideas(
    request: IdeaRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[str] = Depends(get_optional_user_id),
):
    """
    Career-aware, deterministic project recommendations.
    If authenticated, automatically ingests student's Career Discovery recommendations
    and verified profile skills without forcing repetitive input.
    """
    career_interests = list(request.target_career_roles or [])
    student_skills = list(request.existing_skills or [])
    applied_signals = {
        "used_authenticated_profile": False,
        "career_roles_considered": career_interests,
        "skills_considered": student_skills,
    }

    if user_id:
        try:
            user_uuid = UUID(user_id)
            profile = await student_service.get_profile(db, user_uuid)
            if profile:
                applied_signals["used_authenticated_profile"] = True

                # Ingest profile skills
                profile_skills = await student_service.get_skills(db, profile.id)
                for s in profile_skills:
                    if hasattr(s, "skill") and s.skill and s.skill.name:
                        student_skills.append(s.skill.name)

                # Ingest career discovery recommendations if available
                career_recs = await career_recommendation_service.get_recommendations(db, profile.id)
                for rec in career_recs:
                    if hasattr(rec, "career_role") and rec.career_role and rec.career_role.name:
                        career_interests.append(rec.career_role.name)

                applied_signals["career_roles_considered"] = list(set(career_interests))
                applied_signals["skills_considered"] = list(set(student_skills))
        except Exception:
            # Fallback gracefully to request inputs if profile extraction encounters missing records
            pass

    recommended = project_ideas_service.recommend_ideas(
        request=request,
        career_interests=career_interests,
        student_skills=student_skills,
    )

    return IdeaRecommendationResponse(
        recommendations=recommended,
        total_matches=len(recommended),
        applied_profile_signals=applied_signals,
    )


@router.get("/resume-projects")
async def get_resume_projects(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Retrieves projects extracted from student's uploaded resumes
    so they can be imported into Project Launchpad for tracking,
    5-dimension evaluation, and Outcome Intelligence (Startup, Product, Thesis/Research).
    """
    try:
        user_uuid = UUID(user_id)
        profile = await student_service.get_profile(db, user_uuid)
        if not profile:
            return []

        from app.db.models.resume import Resume, ResumeExtraction
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        query = (
            select(Resume)
            .options(selectinload(Resume.extraction))
            .where(Resume.student_profile_id == profile.id)
            .order_by(Resume.created_at.desc())
        )
        result = await db.execute(query)
        resumes = result.scalars().all()

        extracted_projects = []
        seen_titles = set()

        for r in resumes:
            if r.extraction and r.extraction.projects:
                raw_projects = r.extraction.projects
                items = []
                if isinstance(raw_projects, list):
                    items = raw_projects
                elif isinstance(raw_projects, dict):
                    items = raw_projects.get("projects") or raw_projects.get("items") or [raw_projects]

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    name = item.get("name") or item.get("title") or "Unnamed Project"
                    name = str(name).strip()
                    if not name or name.lower() in seen_titles:
                        continue
                    seen_titles.add(name.lower())

                    desc = item.get("description") or item.get("raw_text") or ""
                    techs = item.get("technologies") or []
                    if isinstance(techs, str):
                        techs = [t.strip() for t in techs.split(",") if t.strip()]

                    extracted_projects.append({
                        "title": name,
                        "description": desc,
                        "technologies": techs,
                        "source_resume_title": r.title or r.original_filename or "Uploaded Resume",
                        "source_resume_id": str(r.id),
                    })

        return extracted_projects
    except Exception:
        return []


# -------------------------------------------------------------
# Structured Project Planning
# -------------------------------------------------------------
@router.post("/plan", response_model=GeneratedProjectPlan)
async def generate_project_plan(request: PlanGenerationRequest):
    """
    Generates a structured, deterministic engineering project plan with MVP boundaries,
    phases, testing protocols, risk mitigations, and suggested milestones.
    """
    return project_planner_service.generate_plan(request)


# -------------------------------------------------------------
# Project Core CRUD & Milestones
# -------------------------------------------------------------
@router.get("/projects", response_model=List[LaunchpadProjectResponse])
async def list_student_projects(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all projects created by the authenticated student."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    return await launchpad_service.get_projects(db, profile.id)


@router.post("/projects", response_model=LaunchpadProjectDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_student_project(
    data: LaunchpadProjectCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a project with optional initial milestones and plan data."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    project = await launchpad_service.create_project(db, profile.id, data)
    return await _format_project_detail(project)


@router.get("/projects/{project_id}", response_model=LaunchpadProjectDetailResponse)
async def get_student_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get project details with milestones, evaluation, and outcome state."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    project = await launchpad_service.get_project(db, project_id, profile.id)
    return await _format_project_detail(project)


@router.patch("/projects/{project_id}", response_model=LaunchpadProjectDetailResponse)
async def update_student_project(
    project_id: UUID,
    data: LaunchpadProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update project details, stage, status, or blockers."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    project = await launchpad_service.update_project(db, project_id, profile.id, data)
    return await _format_project_detail(project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a project and its milestones."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    await launchpad_service.delete_project(db, project_id, profile.id)


# -------------------------------------------------------------
# Milestones Endpoints
# -------------------------------------------------------------
@router.post("/projects/{project_id}/milestones", response_model=ProjectMilestoneResponse, status_code=status.HTTP_201_CREATED)
async def add_project_milestone(
    project_id: UUID,
    data: ProjectMilestoneCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Add a milestone to a student project."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    return await launchpad_service.add_milestone(db, project_id, profile.id, data)


@router.patch("/projects/{project_id}/milestones/{milestone_id}", response_model=ProjectMilestoneResponse)
async def update_project_milestone(
    project_id: UUID,
    milestone_id: UUID,
    data: ProjectMilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update milestone status, target date, or notes."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    return await launchpad_service.update_milestone(db, project_id, milestone_id, profile.id, data)


@router.delete("/projects/{project_id}/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_milestone(
    project_id: UUID,
    milestone_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a milestone from a student project."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    await launchpad_service.delete_milestone(db, project_id, milestone_id, profile.id)


# -------------------------------------------------------------
# 5-Dimension Evaluation
# -------------------------------------------------------------
@router.post("/projects/{project_id}/evaluate", response_model=ProjectEvaluationResponse)
async def evaluate_project(
    project_id: UUID,
    data: ProjectEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Run 5-dimension deterministic project evaluation."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    project = await launchpad_service.get_project(db, project_id, profile.id)

    evaluation = project_evaluator_service.evaluate(
        project_id=project.id,
        request=data,
        project_data={
            "title": project.title,
            "description": project.description,
            "technologies": project.technologies,
            "domain": project.domain,
        },
    )

    raw_answers_dict = {a.dimension_key: a.model_dump() for a in data.answers}
    await launchpad_service.save_evaluation(
        db, project_id=project.id, profile_id=profile.id, evaluation=evaluation, raw_answers=raw_answers_dict
    )
    return evaluation


@router.get("/projects/{project_id}/assessments")
async def list_project_assessments(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get history of evaluations for this project."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    return await launchpad_service.get_evaluations(db, project_id, profile.id)


# -------------------------------------------------------------
# Outcome Intelligence & Pathway Conversion
# -------------------------------------------------------------
@router.post("/projects/{project_id}/outcome-intelligence", response_model=OutcomeIntelligenceResponse)
async def run_outcome_intelligence(
    project_id: UUID,
    request: OutcomeIntelligenceRequest = None,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Evaluate project for 6 strategic next-stage pathways."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    project = await launchpad_service.get_project(db, project_id, profile.id)

    # Fetch latest evaluation if available
    evals = await launchpad_service.get_evaluations(db, project_id, profile.id)
    latest_eval = evals[0] if evals else None
    eval_dict = {"dimension_scores": latest_eval.dimension_scores} if latest_eval else {}

    outcome = project_outcome_intelligence_service.analyze_outcomes(
        project_id=project.id,
        project_title=project.title,
        project_stage=project.stage or "idea",
        domain=project.domain or "Full Stack Web",
        primary_goal=project.primary_goal or "portfolio",
        technologies=project.technologies,
        evaluation_scores=eval_dict,
        has_repo=bool(project.github_url),
        has_demo=bool(project.demo_url),
        student_intent=request.student_primary_intent if request else None,
    )

    await launchpad_service.save_outcome_intelligence(
        db, project_id=project.id, profile_id=profile.id, outcome=outcome
    )
    return outcome


@router.post("/projects/{project_id}/apply-pathway-milestones", response_model=List[ProjectMilestoneResponse])
async def apply_pathway_milestones(
    project_id: UUID,
    request: ApplyPathwayRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Converts a chosen outcome pathway into active project milestone tasks."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    return await launchpad_service.apply_pathway_milestones(
        db,
        project_id=project_id,
        profile_id=profile.id,
        pathway_key=request.pathway_key,
        replace_existing=request.replace_existing_milestones,
    )


# -------------------------------------------------------------
# Project Showcase
# -------------------------------------------------------------
@router.get("/projects/{project_id}/showcase", response_model=ShowcaseResponse)
async def get_project_showcase(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get project showcase portfolio configuration."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    showcase = await launchpad_service.get_or_create_showcase(db, project_id, profile.id)
    project = await launchpad_service.get_project(db, project_id, profile.id)
    return _format_showcase(showcase, project)


@router.put("/projects/{project_id}/showcase", response_model=ShowcaseResponse)
async def update_project_showcase(
    project_id: UUID,
    data: ShowcaseUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update showcase settings and toggle public visibility."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    showcase = await launchpad_service.update_showcase(db, project_id, profile.id, data)
    project = await launchpad_service.get_project(db, project_id, profile.id)
    return _format_showcase(showcase, project)


@router.get("/showcase/{slug}", response_model=ShowcaseResponse)
async def get_public_showcase(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[str] = Depends(get_optional_user_id),
):
    """Public showcase view. If private, only the authenticated owner may view it."""
    req_profile_id = None
    if user_id:
        try:
            profile = await student_service.get_profile(db, UUID(user_id))
            if profile:
                req_profile_id = profile.id
        except Exception:
            pass

    showcase = await launchpad_service.get_public_showcase_by_slug(db, slug, req_profile_id)
    return _format_showcase(showcase, showcase.project)


# -------------------------------------------------------------
# Opportunities Directory & Applications
# -------------------------------------------------------------
@router.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    type: Optional[str] = Query(None, alias="type"),
    domain: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    beneficiary_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Browse the curated, source-backed opportunity directory."""
    try:
        opps = await launchpad_service.list_opportunities(
            db,
            opportunity_type=type,
            domain=domain,
            stage=stage,
            beneficiary_type=beneficiary_type,
        )
        return opps
    except Exception:
        # Fallback to local curated service dataset
        return project_opportunities_service.list_opportunities(
            opportunity_type=type,
            domain=domain,
            stage=stage,
            beneficiary_type=beneficiary_type,
        )


@router.get("/opportunities/saved", response_model=List[OpportunityApplicationResponse])
async def list_saved_opportunities(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List opportunities bookmarked and tracked by the student."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    return await launchpad_service.list_saved_applications(db, profile.id)


@router.post("/opportunities/{opp_id}/bookmark", response_model=OpportunityApplicationResponse)
async def bookmark_opportunity(
    opp_id: UUID,
    data: OpportunityApplicationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Bookmark or update tracking status for an opportunity."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    return await launchpad_service.bookmark_opportunity(
        db,
        profile_id=profile.id,
        opp_id=opp_id,
        project_id=data.project_id,
        status=data.status,
        notes=data.notes,
    )


@router.delete("/opportunities/{opp_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmarked_opportunity(
    opp_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Remove a bookmarked opportunity."""
    profile = await get_or_create_student_profile(db, UUID(user_id))
    await launchpad_service.remove_bookmarked_opportunity(db, profile.id, opp_id)


# -------------------------------------------------------------
# Helpers
# -------------------------------------------------------------
async def _format_project_detail(project) -> LaunchpadProjectDetailResponse:
    latest_eval = None
    if project.launchpad_assessments:
        ae = project.launchpad_assessments[0]
        latest_eval = {
            "id": str(ae.id),
            "overall_score": float(ae.overall_score),
            "overall_rating": ae.overall_rating,
            "summary": ae.summary,
            "created_at": ae.created_at.isoformat() if ae.created_at else None,
        }

    latest_out = None
    if project.launchpad_outcomes:
        lo = project.launchpad_outcomes[0]
        latest_out = {
            "id": str(lo.id),
            "top_pathway": lo.top_pathway,
            "readiness_summary": lo.readiness_summary,
            "created_at": lo.created_at.isoformat() if lo.created_at else None,
        }

    showcase_slug = None
    showcase_public = False
    if project.launchpad_showcase:
        showcase_slug = project.launchpad_showcase.slug
        showcase_public = project.launchpad_showcase.is_public

    return LaunchpadProjectDetailResponse(
        id=project.id,
        student_profile_id=project.student_profile_id,
        title=project.title,
        description=project.description,
        role=project.role,
        technologies=project.technologies,
        start_date=project.start_date,
        end_date=project.end_date,
        is_current=project.is_current,
        github_url=project.github_url,
        demo_url=project.demo_url,
        achievements=project.achievements,
        team_size=project.team_size,
        impact_metrics=project.impact_metrics,
        visibility=project.visibility,
        problem_statement=project.problem_statement,
        target_users=project.target_users,
        proposed_solution=project.proposed_solution,
        domain=project.domain,
        difficulty_level=project.difficulty_level,
        primary_goal=project.primary_goal,
        stage=project.stage,
        status=project.status,
        blocker_description=project.blocker_description,
        weekly_hours=project.weekly_hours,
        estimated_duration_weeks=project.estimated_duration_weeks,
        completion_percentage=project.completion_percentage,
        origin=project.origin,
        catalogue_idea_id=project.catalogue_idea_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        milestones=project.launchpad_milestones or [],
        latest_assessment=latest_eval,
        latest_outcome=latest_out,
        showcase_slug=showcase_slug,
        showcase_public=showcase_public,
        plan_data=project.plan_data,
    )


def _format_showcase(showcase, project) -> ShowcaseResponse:
    return ShowcaseResponse(
        id=showcase.id,
        project_id=showcase.project_id,
        student_profile_id=showcase.student_profile_id,
        slug=showcase.slug,
        is_public=showcase.is_public,
        headline=showcase.headline,
        problem_solution_summary=showcase.problem_solution_summary,
        key_contributions=showcase.key_contributions,
        outcomes_metrics=showcase.outcomes_metrics,
        skills_highlighted=showcase.skills_highlighted,
        media_urls=showcase.media_urls,
        view_count=showcase.view_count,
        project_title=project.title,
        project_description=project.description,
        technologies=project.technologies,
        github_url=project.github_url,
        demo_url=project.demo_url,
        stage=project.stage,
        created_at=showcase.created_at,
    )
