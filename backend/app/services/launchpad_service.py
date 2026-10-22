"""
Orvena Project Launchpad Database Service

Manages database persistence for projects, milestones, 5-dimension assessments,
strategic outcome evaluations, project showcase portfolios, and opportunity applications.
Enforces strict server-side ownership and authorization checks on every operation.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
import re

from sqlalchemy import select, delete, and_, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.student import Project, StudentProfile
from app.db.models.launchpad import (
    ProjectMilestone,
    ProjectAssessment,
    ProjectOutcomeAssessment,
    ProjectShowcase,
    Opportunity,
    ProjectOpportunityApplication,
)
from app.schemas.launchpad import (
    LaunchpadProjectCreate,
    LaunchpadProjectUpdate,
    ProjectMilestoneCreate,
    ProjectMilestoneUpdate,
    ProjectEvaluationResponse,
    OutcomeIntelligenceResponse,
    ShowcaseUpdateRequest,
)
from app.core.exceptions import NotFoundError, UnauthorizedError, ValidationError
from app.services.launchpad_outcomes import project_outcome_intelligence_service
from app.services.launchpad_opportunities import project_opportunities_service, CURATED_OPPORTUNITIES


class LaunchpadService:
    """Handles all database operations for Project Launchpad."""

    # -------------------------------------------------------------
    # Project Core CRUD
    # -------------------------------------------------------------
    async def get_projects(self, db: AsyncSession, profile_id: UUID) -> List[Project]:
        """Fetch all projects owned by the student profile."""
        query = (
            select(Project)
            .where(Project.student_profile_id == profile_id)
            .order_by(Project.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_project(
        self, db: AsyncSession, project_id: UUID, profile_id: UUID
    ) -> Project:
        """Fetch a specific project ensuring student ownership."""
        query = (
            select(Project)
            .options(
                selectinload(Project.launchpad_milestones),
                selectinload(Project.launchpad_assessments),
                selectinload(Project.launchpad_outcomes),
                selectinload(Project.launchpad_showcase),
            )
            .where(and_(Project.id == project_id, Project.student_profile_id == profile_id))
        )
        result = await db.execute(query)
        project = result.scalar_one_or_none()
        if not project:
            raise NotFoundError("Project not found or you are not authorized to view it")
        return project

    async def create_project(
        self, db: AsyncSession, profile_id: UUID, data: LaunchpadProjectCreate
    ) -> Project:
        """Create a new project with optional initial milestones."""
        project = Project(
            id=uuid4(),
            student_profile_id=profile_id,
            title=data.title,
            description=data.description,
            role=data.role,
            technologies=data.technologies,
            problem_statement=data.problem_statement,
            target_users=data.target_users,
            proposed_solution=data.proposed_solution,
            domain=data.domain,
            difficulty_level=data.difficulty_level,
            primary_goal=data.primary_goal,
            stage=data.stage,
            status=data.status,
            weekly_hours=data.weekly_hours,
            estimated_duration_weeks=data.estimated_duration_weeks,
            github_url=data.github_url,
            demo_url=data.demo_url,
            visibility=data.visibility or "public",
            origin=data.origin or "scratch",
            catalogue_idea_id=data.catalogue_idea_id,
            plan_data=data.plan_data,
            completion_percentage=0,
            is_current=True,
        )
        db.add(project)
        await db.flush()

        # Create initial milestones if provided
        if data.initial_milestones:
            for idx, m_data in enumerate(data.initial_milestones, start=1):
                milestone = ProjectMilestone(
                    id=uuid4(),
                    project_id=project.id,
                    title=m_data.title,
                    description=m_data.description,
                    phase=m_data.phase,
                    sequence_order=m_data.sequence_order or idx,
                    status=m_data.status or "not_started",
                    target_date=m_data.target_date,
                    deliverables=m_data.deliverables,
                    resources=m_data.resources,
                )
                db.add(milestone)
            await db.flush()

        await self._recalculate_project_completion(db, project.id)
        await db.commit()

        # Re-fetch with relationships loaded
        return await self.get_project(db, project.id, profile_id)

    async def update_project(
        self,
        db: AsyncSession,
        project_id: UUID,
        profile_id: UUID,
        data: LaunchpadProjectUpdate,
    ) -> Project:
        """Update project details."""
        project = await self.get_project(db, project_id, profile_id)

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(project, key, value)

        await db.commit()
        return await self.get_project(db, project_id, profile_id)

    async def delete_project(
        self, db: AsyncSession, project_id: UUID, profile_id: UUID
    ) -> None:
        """Delete project and all child records."""
        project = await self.get_project(db, project_id, profile_id)
        await db.delete(project)
        await db.commit()

    # -------------------------------------------------------------
    # Milestones Management
    # -------------------------------------------------------------
    async def add_milestone(
        self,
        db: AsyncSession,
        project_id: UUID,
        profile_id: UUID,
        data: ProjectMilestoneCreate,
    ) -> ProjectMilestone:
        """Add a milestone to an owned project."""
        # Check ownership
        await self.get_project(db, project_id, profile_id)

        milestone = ProjectMilestone(
            id=uuid4(),
            project_id=project_id,
            title=data.title,
            description=data.description,
            phase=data.phase,
            sequence_order=data.sequence_order,
            status=data.status,
            target_date=data.target_date,
            deliverables=data.deliverables,
            resources=data.resources,
            blocker_notes=data.blocker_notes,
        )
        db.add(milestone)
        await db.flush()

        await self._recalculate_project_completion(db, project_id)
        await db.commit()
        await db.refresh(milestone)
        return milestone

    async def update_milestone(
        self,
        db: AsyncSession,
        project_id: UUID,
        milestone_id: UUID,
        profile_id: UUID,
        data: ProjectMilestoneUpdate,
    ) -> ProjectMilestone:
        """Update a specific milestone."""
        await self.get_project(db, project_id, profile_id)

        query = select(ProjectMilestone).where(
            and_(
                ProjectMilestone.id == milestone_id,
                ProjectMilestone.project_id == project_id,
            )
        )
        result = await db.execute(query)
        milestone = result.scalar_one_or_none()
        if not milestone:
            raise NotFoundError("Milestone not found")

        update_dict = data.model_dump(exclude_unset=True)
        if "status" in update_dict:
            if update_dict["status"] == "completed" and milestone.status != "completed":
                milestone.completed_at = datetime.now(timezone.utc)
            elif update_dict["status"] != "completed":
                milestone.completed_at = None

        for key, value in update_dict.items():
            setattr(milestone, key, value)

        await db.flush()
        await self._recalculate_project_completion(db, project_id)
        await db.commit()
        await db.refresh(milestone)
        return milestone

    async def delete_milestone(
        self,
        db: AsyncSession,
        project_id: UUID,
        milestone_id: UUID,
        profile_id: UUID,
    ) -> None:
        """Delete a milestone."""
        await self.get_project(db, project_id, profile_id)

        query = select(ProjectMilestone).where(
            and_(
                ProjectMilestone.id == milestone_id,
                ProjectMilestone.project_id == project_id,
            )
        )
        result = await db.execute(query)
        milestone = result.scalar_one_or_none()
        if not milestone:
            raise NotFoundError("Milestone not found")

        await db.delete(milestone)
        await db.flush()
        await self._recalculate_project_completion(db, project_id)
        await db.commit()

    async def _recalculate_project_completion(
        self, db: AsyncSession, project_id: UUID
    ) -> int:
        """Recalculates completion percentage based on milestone statuses."""
        query = select(ProjectMilestone).where(ProjectMilestone.project_id == project_id)
        result = await db.execute(query)
        milestones = list(result.scalars().all())

        if not milestones:
            pct = 0
        else:
            completed_count = sum(1 for m in milestones if m.status == "completed")
            pct = int((completed_count / len(milestones)) * 100)

        update_stmt = (
            update(Project)
            .where(Project.id == project_id)
            .values(completion_percentage=pct)
        )
        await db.execute(update_stmt)
        return pct

    # -------------------------------------------------------------
    # 5-Dimension Evaluation Persistence
    # -------------------------------------------------------------
    async def save_evaluation(
        self,
        db: AsyncSession,
        project_id: UUID,
        profile_id: UUID,
        evaluation: ProjectEvaluationResponse,
        raw_answers: Optional[Dict[str, Any]] = None,
    ) -> ProjectAssessment:
        """Persist a completed 5-dimension evaluation."""
        record = ProjectAssessment(
            id=evaluation.id,
            project_id=project_id,
            student_profile_id=profile_id,
            overall_score=evaluation.overall_score,
            overall_rating=evaluation.overall_rating,
            dimension_scores={k: v.model_dump() for k, v in evaluation.dimension_scores.items()},
            strengths=evaluation.strengths,
            missing_evidence=evaluation.missing_evidence,
            improvement_priorities=evaluation.improvement_priorities,
            recommended_milestone=evaluation.recommended_milestone,
            reassessment_conditions=evaluation.reassessment_conditions,
            summary=evaluation.summary,
            raw_answers=raw_answers,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    async def get_evaluations(
        self, db: AsyncSession, project_id: UUID, profile_id: UUID
    ) -> List[ProjectAssessment]:
        """Fetch past evaluations for a project."""
        await self.get_project(db, project_id, profile_id)
        query = (
            select(ProjectAssessment)
            .where(
                and_(
                    ProjectAssessment.project_id == project_id,
                    ProjectAssessment.student_profile_id == profile_id,
                )
            )
            .order_by(ProjectAssessment.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    # -------------------------------------------------------------
    # Outcome Intelligence Persistence & Milestone Conversion
    # -------------------------------------------------------------
    async def save_outcome_intelligence(
        self,
        db: AsyncSession,
        project_id: UUID,
        profile_id: UUID,
        outcome: OutcomeIntelligenceResponse,
    ) -> ProjectOutcomeAssessment:
        """Persist an outcome intelligence evaluation."""
        record = ProjectOutcomeAssessment(
            id=outcome.id,
            project_id=project_id,
            student_profile_id=profile_id,
            selected_goal=outcome.selected_goal,
            top_pathway=outcome.top_pathway,
            pathways=[p.model_dump() for p in outcome.pathways],
            readiness_summary=outcome.readiness_summary,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    async def get_latest_outcome(
        self, db: AsyncSession, project_id: UUID, profile_id: UUID
    ) -> Optional[ProjectOutcomeAssessment]:
        """Get the most recent outcome assessment for a project."""
        await self.get_project(db, project_id, profile_id)
        query = (
            select(ProjectOutcomeAssessment)
            .where(
                and_(
                    ProjectOutcomeAssessment.project_id == project_id,
                    ProjectOutcomeAssessment.student_profile_id == profile_id,
                )
            )
            .order_by(ProjectOutcomeAssessment.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def apply_pathway_milestones(
        self,
        db: AsyncSession,
        project_id: UUID,
        profile_id: UUID,
        pathway_key: str,
        replace_existing: bool = False,
    ) -> List[ProjectMilestone]:
        """Converts suggested milestones from an outcome pathway into active project milestones."""
        project = await self.get_project(db, project_id, profile_id)

        # Run outcome evaluation to retrieve pathway templates
        outcome_resp = project_outcome_intelligence_service.analyze_outcomes(
            project_id=project.id,
            project_title=project.title,
            project_stage=project.stage or "idea",
            domain=project.domain or "Full Stack Web",
            primary_goal=project.primary_goal or "portfolio",
            technologies=project.technologies,
            has_repo=bool(project.github_url),
            has_demo=bool(project.demo_url),
        )

        target_pathway = next(
            (p for p in outcome_resp.pathways if p.pathway_key == pathway_key), None
        )
        if not target_pathway:
            raise NotFoundError(f"Pathway {pathway_key} not found")

        if replace_existing:
            # Delete existing milestones
            del_stmt = delete(ProjectMilestone).where(
                ProjectMilestone.project_id == project_id
            )
            await db.execute(del_stmt)
            start_seq = 1
        else:
            # Query max sequence order
            max_seq_q = select(func.coalesce(func.max(ProjectMilestone.sequence_order), 0)).where(
                ProjectMilestone.project_id == project_id
            )
            max_res = await db.execute(max_seq_q)
            start_seq = (max_res.scalar() or 0) + 1

        new_milestones = []
        for idx, m_tmpl in enumerate(target_pathway.suggested_milestones, start=start_seq):
            m = ProjectMilestone(
                id=uuid4(),
                project_id=project_id,
                title=m_tmpl.title,
                description=m_tmpl.description,
                phase=m_tmpl.phase,
                sequence_order=idx,
                status="not_started",
                deliverables=m_tmpl.deliverables,
            )
            db.add(m)
            new_milestones.append(m)

        await db.flush()
        await self._recalculate_project_completion(db, project_id)
        await db.commit()
        return new_milestones

    # -------------------------------------------------------------
    # Project Showcase
    # -------------------------------------------------------------
    async def get_or_create_showcase(
        self, db: AsyncSession, project_id: UUID, profile_id: UUID
    ) -> ProjectShowcase:
        """Fetch showcase or initialize draft."""
        project = await self.get_project(db, project_id, profile_id)

        query = select(ProjectShowcase).where(ProjectShowcase.project_id == project_id)
        result = await db.execute(query)
        showcase = result.scalar_one_or_none()

        if not showcase:
            # Generate URL-safe slug
            clean_title = re.sub(r"[^a-zA-Z0-9]+", "-", project.title.lower()).strip("-")
            slug = f"{clean_title}-{str(project.id)[:8]}"

            showcase = ProjectShowcase(
                id=uuid4(),
                project_id=project.id,
                student_profile_id=profile_id,
                slug=slug,
                is_public=False,
                headline=f"{project.title} - {project.domain or 'Engineering Project'}",
                problem_solution_summary=project.problem_statement or project.description,
                key_contributions=[project.role or "Lead Contributor"],
                skills_highlighted=project.technologies,
                view_count=0,
            )
            db.add(showcase)
            await db.commit()
            await db.refresh(showcase)

        return showcase

    async def update_showcase(
        self,
        db: AsyncSession,
        project_id: UUID,
        profile_id: UUID,
        data: ShowcaseUpdateRequest,
    ) -> ProjectShowcase:
        """Update showcase configuration and public visibility."""
        showcase = await self.get_or_create_showcase(db, project_id, profile_id)

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(showcase, key, value)

        await db.commit()
        await db.refresh(showcase)
        return showcase

    async def get_public_showcase_by_slug(
        self, db: AsyncSession, slug: str, requesting_user_profile_id: Optional[UUID] = None
    ) -> ProjectShowcase:
        """Fetch showcase by unique slug. Enforces access control for private showcases."""
        query = (
            select(ProjectShowcase)
            .options(selectinload(ProjectShowcase.project))
            .where(ProjectShowcase.slug == slug)
        )
        result = await db.execute(query)
        showcase = result.scalar_one_or_none()

        if not showcase:
            raise NotFoundError("Showcase not found")

        # If private, only owner may view
        if not showcase.is_public:
            if not requesting_user_profile_id or showcase.student_profile_id != requesting_user_profile_id:
                raise UnauthorizedError("This project showcase is private.")

        # Increment view count
        showcase.view_count += 1
        await db.commit()
        return showcase

    # -------------------------------------------------------------
    # Opportunities & Applications Tracking
    # -------------------------------------------------------------
    async def list_opportunities(
        self,
        db: AsyncSession,
        opportunity_type: Optional[str] = None,
        domain: Optional[str] = None,
        stage: Optional[str] = None,
        beneficiary_type: Optional[str] = None,
    ) -> List[Opportunity]:
        """List opportunities from database, falling back to curated dataset if unseeded."""
        query = select(Opportunity).where(Opportunity.status == "active")
        result = await db.execute(query)
        opps = list(result.scalars().all())

        # If database has not been seeded with opportunities yet, seed them!
        if not opps:
            for raw in CURATED_OPPORTUNITIES:
                db_opp = Opportunity(
                    id=UUID(raw["id"]),
                    title=raw["title"],
                    provider=raw["provider"],
                    opportunity_type=raw["opportunity_type"],
                    description=raw["description"],
                    official_url=raw["official_url"],
                    eligibility_requirements=raw.get("eligibility_requirements"),
                    beneficiary_type=raw.get("beneficiary_type", "individual_student"),
                    geographic_scope=raw.get("geographic_scope", "Global"),
                    domains=raw.get("domains"),
                    required_project_stage=raw.get("required_project_stage", "any"),
                    funding_amount_or_benefits=raw.get("funding_amount_or_benefits"),
                    is_monetary=raw.get("is_monetary", False),
                    application_deadline=raw.get("application_deadline"),
                    is_rolling=raw.get("is_rolling", False),
                    application_instructions=raw.get("application_instructions"),
                    date_last_verified=raw.get("date_last_verified"),
                    status=raw.get("status", "active"),
                    is_verified=raw.get("is_verified", True),
                    source_notes=raw.get("source_notes"),
                )
                db.add(db_opp)
            try:
                await db.commit()
                opps_result = await db.execute(select(Opportunity))
                opps = list(opps_result.scalars().all())
            except Exception:
                await db.rollback()

        # Apply in-memory filtering if needed
        filtered = []
        for o in opps:
            if opportunity_type and opportunity_type.lower() != "all":
                if o.opportunity_type.lower() != opportunity_type.lower():
                    continue
            if domain and domain.lower() != "all":
                if not any(domain.lower() in (d or "").lower() for d in (o.domains or [])):
                    continue
            if stage and stage.lower() != "all":
                if o.required_project_stage != "any" and o.required_project_stage != stage:
                    continue
            if beneficiary_type and beneficiary_type.lower() != "all":
                if o.beneficiary_type != beneficiary_type:
                    continue
            filtered.append(o)
        return filtered

    async def list_saved_applications(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[ProjectOpportunityApplication]:
        """Fetch student's bookmarked and tracked opportunity applications."""
        query = (
            select(ProjectOpportunityApplication)
            .options(
                selectinload(ProjectOpportunityApplication.opportunity),
                selectinload(ProjectOpportunityApplication.project),
            )
            .where(ProjectOpportunityApplication.student_profile_id == profile_id)
            .order_by(ProjectOpportunityApplication.updated_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def bookmark_opportunity(
        self,
        db: AsyncSession,
        profile_id: UUID,
        opp_id: UUID,
        project_id: Optional[UUID] = None,
        status: str = "saved",
        notes: Optional[str] = None,
    ) -> ProjectOpportunityApplication:
        """Save or update tracking status for an opportunity."""
        # Check existing
        query = select(ProjectOpportunityApplication).where(
            and_(
                ProjectOpportunityApplication.student_profile_id == profile_id,
                ProjectOpportunityApplication.opportunity_id == opp_id,
            )
        )
        result = await db.execute(query)
        app = result.scalar_one_or_none()

        if app:
            app.status = status
            if project_id:
                app.project_id = project_id
            if notes is not None:
                app.notes = notes
        else:
            app = ProjectOpportunityApplication(
                id=uuid4(),
                student_profile_id=profile_id,
                opportunity_id=opp_id,
                project_id=project_id,
                status=status,
                notes=notes,
            )
            db.add(app)

        await db.commit()
        await db.refresh(app)
        return app

    async def remove_bookmarked_opportunity(
        self, db: AsyncSession, profile_id: UUID, opp_id: UUID
    ) -> None:
        """Remove a saved opportunity."""
        del_stmt = delete(ProjectOpportunityApplication).where(
            and_(
                ProjectOpportunityApplication.student_profile_id == profile_id,
                ProjectOpportunityApplication.opportunity_id == opp_id,
            )
        )
        await db.execute(del_stmt)
        await db.commit()


launchpad_service = LaunchpadService()
