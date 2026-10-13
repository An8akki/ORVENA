"""Service layer for career recommendations and roadmaps."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json
import re

from app.db.models.student import StudentProfile, StudentSkill, EducationRecord
from app.db.models.resume import Resume, ResumeExtraction
from app.db.models.career import (
    CareerRole,
    RoleRequirement,
    CareerDiscoverySession,
    CareerRecommendation,
    CareerRoadmap,
    RoadmapMilestone,
    CareerGoal,
)
from app.schemas.career import (
    CareerGoalCreate,
    CareerGoalUpdate,
)
from app.services.llm import get_llm_provider, LLMMessage
from app.core.exceptions import NotFoundError, ValidationError


class CareerRecommendationService:
    """Service for generating career recommendations and roadmaps."""

    RECOMMENDATION_SYSTEM_PROMPT = """You are an expert career advisor analyzing student profiles to provide personalized career recommendations.

Your task is to:
1. Analyze the student's background (education, skills, projects, interests)
2. Match them with suitable career roles in CURRENTLY BOOMING INDUSTRIES (AI/ML, Cloud Computing, Cybersecurity, Data Science, DevOps, Full-Stack Development, etc.)
3. Provide detailed reasoning for each recommendation
4. Perform SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
5. Include realistic salary information for each role
6. Add industry trends and market outlook
7. Rank recommendations by fit score

Consider:
- Technical skills and proficiency levels
- Educational background and field of study
- Project experience and portfolio
- Career goals and preferences from discovery session
- Market demand and growth potential (prioritize HIGH-GROWTH industries)
- Skill gaps and development needs
- Salary expectations ($75,000+ annually for entry to mid-level roles)

Return recommendations as a JSON array with this structure:
[
  {
    "role_name": "Software Engineer",
    "category": "Technology",
    "fit_score": 0.85,
    "reasoning": "Brief explanation of why this is a good fit",
    "salary_range_min": 75000,
    "salary_range_max": 150000,
    "salary_currency": "USD",
    "salary_period": "annual",
    "industry_trend": "Growing rapidly with AI/ML integration, high demand for cloud-native applications",
    "market_growth": "15% annual growth expected through 2027",
    "strengths": ["strength1", "strength2"],
    "gaps": ["gap1", "gap2"],
    "opportunities": ["opportunity1", "opportunity2"],
    "threats": ["threat1", "threat2"]
  }
]

IMPORTANT: 
- Focus on HIGH-PAYING roles ($75,000+ annual salary)
- Emphasize CURRENTLY BOOMING sectors (AI, Cloud, Data, Cybersecurity)
- Provide REALISTIC salary ranges based on current market data (October 2026)
- Include industry growth trends and market outlook
- Provide 3-5 recommendations ranked by fit score (0.0-1.0)."""

    ROADMAP_SYSTEM_PROMPT = """You are a career development coach creating personalized learning roadmaps.

Your task is to create a detailed, actionable development plan that helps the student:
1. Bridge skill gaps for their target career
2. Build relevant experience and portfolio
3. Prepare for job applications and interviews
4. Achieve their career goals within the target timeline

The roadmap should include:
- Specific, measurable milestones
- Estimated time commitment for each task
- Resources and learning materials
- Project ideas to build experience
- Networking and community engagement
- Application and interview preparation

Return a roadmap as JSON with this structure:
{
  "title": "Career Development Roadmap for [Role]",
  "description": "Brief overview of the plan",
  "target_duration_weeks": 12,
  "milestones": [
    {
      "title": "Milestone title",
      "description": "What to accomplish",
      "category": "learning|project|networking|application",
      "estimated_hours": 20,
      "sequence_number": 1,
      "resources": ["resource1", "resource2"]
    }
  ]
}

Create 6-10 milestones spanning the target timeline."""

    async def get_or_create_career_roles(
        self, db: AsyncSession
    ) -> List[CareerRole]:
        """Get or seed initial career roles."""
        result = await db.execute(select(CareerRole))
        roles = list(result.scalars().all())
        
        if not roles:
            # Seed with common tech roles (in production, load from a comprehensive database)
            default_roles = [
                {
                    "name": "Software Engineer",
                    "category": "Technology",
                    "description": "Design, develop, and maintain software applications",
                    "typical_salary_min": 70000,
                    "typical_salary_max": 150000,
                },
                {
                    "name": "Data Scientist",
                    "category": "Technology",
                    "description": "Analyze data and build predictive models",
                    "typical_salary_min": 80000,
                    "typical_salary_max": 160000,
                },
                {
                    "name": "Product Manager",
                    "category": "Business",
                    "description": "Lead product strategy and development",
                    "typical_salary_min": 90000,
                    "typical_salary_max": 170000,
                },
                {
                    "name": "UX Designer",
                    "category": "Design",
                    "description": "Design user experiences for digital products",
                    "typical_salary_min": 65000,
                    "typical_salary_max": 130000,
                },
                {
                    "name": "DevOps Engineer",
                    "category": "Technology",
                    "description": "Manage infrastructure and deployment pipelines",
                    "typical_salary_min": 75000,
                    "typical_salary_max": 150000,
                },
            ]
            
            for role_data in default_roles:
                role = CareerRole(**role_data)
                db.add(role)
            
            await db.commit()
            
            # Fetch again
            result = await db.execute(select(CareerRole))
            roles = list(result.scalars().all())
        
        return roles

    async def generate_recommendations(
        self,
        db: AsyncSession,
        profile_id: UUID,
        session_id: Optional[UUID] = None,
    ) -> List[CareerRecommendation]:
        """Generate career recommendations using AI with statistical fallback."""
        import asyncio
        from app.services.job_matcher import job_matcher
        
        # Get student profile and related data
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.id == profile_id)
        )
        profile = profile_result.scalar_one_or_none()
        if not profile:
            raise NotFoundError("Profile not found")

        # Recommendations must be based on the student's saved discovery
        # answers even when the UI calls this endpoint without a session id.
        # Select the most recently updated session that actually has answers;
        # this also recovers partial sessions without asking the questions again.
        if session_id is None:
            saved_session_result = await db.execute(
                select(CareerDiscoverySession)
                .where(CareerDiscoverySession.student_profile_id == profile_id)
                .options(selectinload(CareerDiscoverySession.responses))
                .order_by(CareerDiscoverySession.updated_at.desc(), CareerDiscoverySession.created_at.desc())
            )
            saved_sessions = list(saved_session_result.scalars().all())
            saved_session = next(
                (item for item in saved_sessions if item.responses), None
            )
            if saved_session:
                session_id = saved_session.id

        # Get education
        education_result = await db.execute(
            select(EducationRecord)
            .where(EducationRecord.student_profile_id == profile_id)
            .order_by(EducationRecord.start_date.desc())
        )
        education = list(education_result.scalars().all())

        # Get skills
        skills_result = await db.execute(
            select(StudentSkill)
            .where(StudentSkill.student_profile_id == profile_id)
            .options(selectinload(StudentSkill.skill))
        )
        skills = list(skills_result.scalars().all())

        # Prepare data for matching
        skill_names = [s.skill.name if s.skill else str(s.skill_id) for s in skills]
        resume_result = await db.execute(
            select(ResumeExtraction)
            .join(Resume, Resume.id == ResumeExtraction.resume_id)
            .where(Resume.student_profile_id == profile_id)
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        resume_extraction = resume_result.scalar_one_or_none()
        resume_text = ""
        if resume_extraction:
            resume_text = resume_extraction.raw_text or ""
            resume_skills = resume_extraction.skills or {}
            if isinstance(resume_skills, dict):
                skill_names.extend(
                    str(value)
                    for values in resume_skills.values()
                    if isinstance(values, list)
                    for value in values
                    if value
                )
            if not education_data and isinstance(resume_extraction.education, list):
                education_data = [item for item in resume_extraction.education if isinstance(item, dict)]
        from app.services.career_signals import extract_skill_evidence
        skill_names = extract_skill_evidence(resume_text, skill_names)
        education_data = [
            {
                "institution": e.institution_name,
                "degree": e.degree,
                "field": e.field_of_study,
                "start_date": str(e.start_date) if e.start_date else "",
                "end_date": str(e.end_date) if e.end_date else ""
            }
            for e in education
        ]
        
        # Get discovery session preferences
        preferences = {}
        if session_id:
            session_result = await db.execute(
                select(CareerDiscoverySession)
                .where(CareerDiscoverySession.id == session_id)
                .options(selectinload(CareerDiscoverySession.responses))
            )
            session = session_result.scalar_one_or_none()
            if session and session.analysis_data:
                preferences = session.analysis_data.get("preferences", {})
            if session and session.responses:
                answers = " ".join(response.response_text for response in session.responses)
                from app.services.career_signals import infer_preferred_roles
                preferences["preferred_roles"] = infer_preferred_roles(answers)
                skill_names = extract_skill_evidence(answers + " " + resume_text, skill_names)

        # Try AI-enhanced recommendations first (with timeout)
        recommendations_data = None
        try:
            recommendations_data = await asyncio.wait_for(
                self._generate_with_ai(profile, education, skills, session_id, db),
                timeout=8.0
            )
        except (asyncio.TimeoutError, Exception) as e:
            print(f"AI recommendation failed, using statistical matcher: {str(e)}")
        
        # Fallback to statistical matching if AI fails
        if not recommendations_data:
            recommendations_data = job_matcher.match_jobs(
                profile={"id": str(profile_id)},
                skills=skill_names,
                education=education_data,
                experience=[],  # TODO: Add experience data if available
                preferences=preferences
            )

        # Ensure career roles exist
        await self.get_or_create_career_roles(db)

        # Create recommendation records
        recommendations = []
        batch_timestamp = datetime.utcnow()
        for idx, rec_data in enumerate(recommendations_data[:5]):  # Top 5
            # Get or create career role
            role = await self._get_or_create_role(
                db, rec_data["role_name"], rec_data.get("category", "Technology")
            )

            recommendation = CareerRecommendation(
                student_profile_id=profile_id,
                career_role_id=role.id,
                session_id=session_id,
                fit_score=rec_data.get("fit_score", 0.7),
                reasoning=rec_data.get("reasoning", ""),
                salary_range_min=rec_data.get("salary_range_min"),
                salary_range_max=rec_data.get("salary_range_max"),
                salary_currency=rec_data.get("salary_currency", "USD"),
                salary_period=rec_data.get("salary_period", "annual"),
                industry_trend=rec_data.get("industry_trend"),
                market_growth=rec_data.get("market_growth", rec_data.get("growth_rate")),
                strengths=rec_data.get("strengths", []),
                gaps=rec_data.get("gaps", []),
                opportunities=rec_data.get("opportunities", []),
                threats=rec_data.get("threats", []),
                recommendation_rank=idx + 1,
                created_at=batch_timestamp,
                updated_at=batch_timestamp,
            )
            db.add(recommendation)
            recommendations.append(recommendation)

        await db.commit()
        
        # Refresh to get relationships
        for rec in recommendations:
            await db.refresh(rec)
            await db.refresh(rec, ["career_role"])

        return recommendations

    async def get_recommendations(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[CareerRecommendation]:
        """Return the latest generated recommendation batch for a profile."""
        latest_result = await db.execute(
            select(CareerRecommendation.created_at)
            .where(CareerRecommendation.student_profile_id == profile_id)
            .order_by(CareerRecommendation.created_at.desc())
            .limit(1)
        )
        latest_created_at = latest_result.scalar_one_or_none()
        if latest_created_at is None:
            return []

        # Recommendations in a batch are written together. Filtering to the
        # latest batch prevents old SWOTs from appearing alongside new answers.
        result = await db.execute(
            select(CareerRecommendation)
            .where(
                CareerRecommendation.student_profile_id == profile_id,
                CareerRecommendation.created_at == latest_created_at,
            )
            .options(selectinload(CareerRecommendation.career_role))
            .order_by(CareerRecommendation.recommendation_rank, CareerRecommendation.created_at.desc())
        )
        latest_batch = list(result.scalars().all())
        return latest_batch[:5]

    async def generate_roadmap(
        self,
        db: AsyncSession,
        profile_id: UUID,
        career_goal_id: Optional[UUID],
        recommendation_id: Optional[UUID] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        target_timeline_weeks: int = 12,
        career_role_id: Optional[UUID] = None,
    ) -> CareerRoadmap:
        """Generate a personalized career development roadmap."""
        llm = get_llm_provider()
        
        # A roadmap can be created directly from a recommendation. Older clients
        # may still provide a goal ID; when absent, create a goal for the role.
        career_goal = None
        if career_goal_id:
            goal_result = await db.execute(
                select(CareerGoal).where(
                    CareerGoal.id == career_goal_id,
                    CareerGoal.student_profile_id == profile_id,
                )
            )
            career_goal = goal_result.scalar_one_or_none()
            if not career_goal:
                raise NotFoundError("Career goal not found")

        # Get target role from goal or recommendation
        target_role = None
        if career_role_id:
            role_result = await db.execute(
                select(CareerRole).where(CareerRole.id == career_role_id)
            )
            target_role = role_result.scalar_one_or_none()
        if not target_role and career_goal and career_goal.career_role_id:
            role_result = await db.execute(
                select(CareerRole).where(CareerRole.id == career_goal.career_role_id)
            )
            target_role = role_result.scalar_one_or_none()
        
        # If no role from goal, try to get from recommendation
        recommendation = None
        if recommendation_id:
            rec_result = await db.execute(
                select(CareerRecommendation)
                .where(
                    CareerRecommendation.id == recommendation_id,
                    CareerRecommendation.student_profile_id == profile_id,
                )
                .options(selectinload(CareerRecommendation.career_role))
            )
            recommendation = rec_result.scalar_one_or_none()
            if recommendation and not target_role:
                target_role = recommendation.career_role

        # Older goals may not have a role linked. Recover the target from this
        # account's newest recommendation instead of failing roadmap creation.
        if not target_role:
            rec_result = await db.execute(
                select(CareerRecommendation)
                .where(CareerRecommendation.student_profile_id == profile_id)
                .options(selectinload(CareerRecommendation.career_role))
                .order_by(CareerRecommendation.created_at.desc())
                .limit(1)
            )
            recommendation = rec_result.scalar_one_or_none()
            if recommendation:
                recommendation_id = recommendation.id
                target_role = recommendation.career_role
        
        if not target_role:
            raise ValidationError("Could not determine target career role")

        if career_goal and not career_goal.career_role_id:
            career_goal.career_role_id = target_role.id

        if not career_goal:
            career_goal = CareerGoal(
                student_profile_id=profile_id,
                career_role_id=target_role.id,
                title=f"Become a {target_role.name}",
                target_timeline=f"{target_timeline_weeks} weeks",
                priority="high",
                status="active",
                is_primary=True,
            )
            db.add(career_goal)
            await db.flush()

        # Get student context
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.id == profile_id)
        )
        profile = profile_result.scalar_one_or_none()

        # Get skills
        skills_result = await db.execute(
            select(StudentSkill)
            .where(StudentSkill.student_profile_id == profile_id)
            .options(selectinload(StudentSkill.skill))
        )
        skills = list(skills_result.scalars().all())

        # Build context
        student_skill_names = [s.skill.name for s in skills if s.skill]
        resume_result = await db.execute(
            select(ResumeExtraction)
            .join(Resume, Resume.id == ResumeExtraction.resume_id)
            .where(Resume.student_profile_id == profile_id)
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        resume_extraction = resume_result.scalar_one_or_none()
        resume_text = ""
        if resume_extraction:
            resume_text = resume_extraction.raw_text or ""
            resume_skill_data = resume_extraction.skills or {}
            if isinstance(resume_skill_data, dict):
                student_skill_names.extend(
                    str(value)
                    for values in resume_skill_data.values()
                    if isinstance(values, list)
                    for value in values
                    if value
                )
        from app.services.career_signals import extract_skill_evidence
        student_skill_names = extract_skill_evidence(resume_text, student_skill_names)
        context = f"""Target Role: {target_role.name}
Goal: {career_goal.title}
Timeline: {target_timeline_weeks} weeks
Current Level: Entry/Junior

Student Profile:
- Name: {profile.full_name if profile else "Student"}
- Current Skills: {', '.join(student_skill_names[:20]) or 'Not listed yet'}

Create a detailed development roadmap to prepare for this role and achieve the career goal."""

        # Carry the same account's saved discovery answers into roadmap
        # generation, even when the user starts from a recommendation link.
        saved_session_result = await db.execute(
            select(CareerDiscoverySession)
            .where(CareerDiscoverySession.student_profile_id == profile_id)
            .options(selectinload(CareerDiscoverySession.responses))
            .order_by(CareerDiscoverySession.updated_at.desc(), CareerDiscoverySession.created_at.desc())
        )
        saved_session = next(
            (item for item in saved_session_result.scalars().all() if item.responses), None
        )
        saved_answers = ""
        if saved_session:
            saved_answers = "\n".join(
                f"Q: {answer.question_text}\nA: {answer.response_text}"
                for answer in sorted(saved_session.responses, key=lambda answer: answer.sequence_number)
            )
            context += f"\n\nStudent's saved career discovery answers:\n{saved_answers}"

        # Generate roadmap with AI
        try:
            import asyncio
            response = await asyncio.wait_for(
                llm.generate_with_system(
                    system_prompt=self.ROADMAP_SYSTEM_PROMPT,
                    user_message=context,
                    temperature=0.7,
                    max_tokens=2000,
                ),
                timeout=12.0,
            )
            roadmap_data = self._parse_roadmap(
                response.content,
                target_role.name,
                target_timeline_weeks,
                student_skill_names,
                saved_answers,
            )
        except Exception as e:
            print(f"AI roadmap generation failed, using built-in template: {e}")
            roadmap_data = self._parse_roadmap(
                "", target_role.name, target_timeline_weeks, student_skill_names, saved_answers
            )

        # Create roadmap
        roadmap_description = description or roadmap_data.get("description", "")
        if "[plan-v2]" not in roadmap_description:
            roadmap_description = f"[plan-v2] {roadmap_description}".strip()
        roadmap = CareerRoadmap(
            student_profile_id=profile_id,
            career_goal_id=career_goal.id,
            recommendation_id=recommendation_id,
            title=title or roadmap_data.get("title", f"Roadmap to {target_role.name}"),
            description=roadmap_description,
            target_duration_weeks=target_timeline_weeks,
            status="active",
            progress_percentage=0,
        )
        db.add(roadmap)
        await db.flush()

        # Create milestones
        for milestone_data in roadmap_data.get("milestones", []):
            milestone = RoadmapMilestone(
                roadmap_id=roadmap.id,
                title=milestone_data.get("title", ""),
                description=milestone_data.get("description", ""),
                category=milestone_data.get("category", "learning"),
                estimated_hours=milestone_data.get("estimated_hours", 10),
                sequence_number=milestone_data.get("sequence_number", 1),
                resources=milestone_data.get("resources", []),
                status="pending",
            )
            db.add(milestone)

        await db.commit()
        await db.refresh(roadmap)
        await db.refresh(roadmap, ["milestones"])

        return roadmap

    async def get_roadmaps(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[CareerRoadmap]:
        """Get all roadmaps for a profile."""
        result = await db.execute(
            select(CareerRoadmap)
            .where(CareerRoadmap.student_profile_id == profile_id)
            .options(selectinload(CareerRoadmap.milestones))
            .order_by(CareerRoadmap.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_milestone_status(
        self,
        db: AsyncSession,
        milestone_id: UUID,
        profile_id: UUID,
        status: str,
    ) -> RoadmapMilestone:
        """Update milestone status and recalculate roadmap progress."""
        # Get milestone with roadmap
        result = await db.execute(
            select(RoadmapMilestone)
            .where(RoadmapMilestone.id == milestone_id)
            .options(
                selectinload(RoadmapMilestone.roadmap)
                .selectinload(CareerRoadmap.milestones)
            )
        )
        milestone = result.scalar_one_or_none()
        
        if not milestone:
            raise NotFoundError("Milestone not found")
        
        # Verify ownership
        if milestone.roadmap.student_profile_id != profile_id:
            raise ValidationError("Not authorized")

        # Update status
        milestone.status = status
        if status == "completed":
            milestone.completed_at = datetime.utcnow()
        else:
            milestone.completed_at = None

        # Recalculate progress
        roadmap = milestone.roadmap
        if status == "completed":
            # Keep the roadmap actionable: completing the current phase unlocks
            # the next pending phase so the UI can offer its completion action.
            next_milestone = next(
                (
                    item for item in sorted(roadmap.milestones, key=lambda item: item.sequence_number)
                    if item.status == "pending"
                ),
                None,
            )
            if next_milestone:
                next_milestone.status = "in_progress"

        total_milestones = len(roadmap.milestones)
        completed = sum(1 for m in roadmap.milestones if m.status == "completed")
        roadmap.progress_percentage = int((completed / total_milestones) * 100) if total_milestones > 0 else 0

        await db.commit()
        await db.refresh(milestone)
        return milestone

    # Career Goals
    async def create_goal(
        self, db: AsyncSession, profile_id: UUID, goal_data: CareerGoalCreate
    ) -> CareerGoal:
        """Create a career goal."""
        goal = CareerGoal(
            student_profile_id=profile_id,
            **goal_data.model_dump()
        )
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
        return goal

    async def get_goals(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[CareerGoal]:
        """Get all career goals."""
        result = await db.execute(
            select(CareerGoal)
            .where(CareerGoal.student_profile_id == profile_id)
            .order_by(CareerGoal.is_primary.desc(), CareerGoal.created_at.desc())
        )
        return list(result.scalars().all())

    
    async def _generate_with_ai(
        self,
        profile: StudentProfile,
        education: List,
        skills: List,
        session_id: Optional[UUID],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Generate recommendations using AI (can throw exceptions)."""
        llm = get_llm_provider()
        
        # Get discovery session if provided
        discovery_insights = ""
        if session_id:
            session_result = await db.execute(
                select(CareerDiscoverySession)
                .where(CareerDiscoverySession.id == session_id)
                .options(selectinload(CareerDiscoverySession.responses))
            )
            session = session_result.scalar_one_or_none()
            if session and session.responses:
                discovery_insights = "\n".join([
                    f"Q: {r.question_text}\nA: {r.response_text}"
                    for r in sorted(session.responses, key=lambda response: response.sequence_number)
                ])

        # Build context for AI
        context = self._build_student_context(profile, education, skills, discovery_insights)

        # Generate recommendations
        response = await llm.generate_with_system(
            system_prompt=self.RECOMMENDATION_SYSTEM_PROMPT,
            user_message=context,
            temperature=0.7,
            max_tokens=1500,
        )

        # Parse AI response
        return self._parse_recommendations(response.content)
    
    # Helper methods
    def _build_student_context(
        self,
        profile: StudentProfile,
        education: List[EducationRecord],
        skills: List[StudentSkill],
        discovery_insights: str,
    ) -> str:
        """Build student context for AI."""
        parts = [f"Student Profile Analysis:\n"]
        
        if profile:
            parts.append(f"Name: {profile.full_name}")
            if profile.bio:
                parts.append(f"Bio: {profile.bio}")
        
        if education:
            parts.append("\nEducation:")
            for edu in education[:2]:
                parts.append(f"- {edu.degree} in {edu.field_of_study} from {edu.institution_name}")
        
        if skills:
            parts.append("\nSkills:")
            for skill in skills[:15]:
                parts.append(f"- {skill.skill.name} ({skill.proficiency_level})")
        
        if discovery_insights:
            parts.append(f"\nCareer Discovery Insights:\n{discovery_insights}")
        
        parts.append("\nProvide career recommendations for this student.")
        
        return "\n".join(parts)

    def _parse_recommendations(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI recommendations response."""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback: create a default recommendation with salary
                return [{
                    "role_name": "Software Engineer",
                    "category": "Technology",
                    "fit_score": 0.75,
                    "reasoning": "Based on your technical background and skills, software engineering is a strong match with excellent growth prospects.",
                    "salary_range_min": 75000,
                    "salary_range_max": 150000,
                    "salary_currency": "USD",
                    "salary_period": "annual",
                    "industry_trend": "Growing rapidly with AI/ML integration and cloud-native development. High demand for full-stack engineers.",
                    "market_growth": "15% annual growth expected through 2027, driven by digital transformation and AI adoption.",
                    "strengths": ["Technical skills", "Problem solving", "Adaptability to new technologies"],
                    "gaps": ["Industry experience", "Advanced cloud platforms", "System design at scale"],
                    "opportunities": ["Booming AI/ML sector", "Remote work flexibility", "High-paying roles"],
                    "threats": ["Competitive job market", "Rapid technology changes require continuous learning"],
                }]
        except Exception:
            # Return default if parsing fails
            return [{
                "role_name": "Software Engineer",
                "category": "Technology",
                "fit_score": 0.75,
                "reasoning": "Technical background suggests strong fit for software engineering with current market demand.",
                "salary_range_min": 75000,
                "salary_range_max": 150000,
                "salary_currency": "USD",
                "salary_period": "annual",
                "industry_trend": "High growth sector with increasing demand",
                "market_growth": "15% annual growth through 2027",
                "strengths": ["Technical foundation"],
                "gaps": ["Professional experience"],
                "opportunities": ["Growing field", "High salaries"],
                "threats": ["Competition"],
            }]

    def _parse_roadmap(
        self,
        ai_response: str,
        role_name: str,
        duration_weeks: int = 16,
        current_skills: Optional[List[str]] = None,
        discovery_answers: str = "",
    ) -> Dict[str, Any]:
        """Parse AI output or build a role-specific roadmap without AI."""
        try:
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, dict) and len(parsed.get("milestones", [])) >= 6:
                    return parsed
        except Exception:
            pass

        role = role_name.lower()
        if any(term in role for term in ("cyber", "security")):
            roadmap = {
                "focus": ["TCP/IP, DNS, HTTP/TLS", "Linux and Windows internals", "threat modeling and risk", "OWASP Top 10", "Nmap, Wireshark, Zeek", "SIEM triage and incident response"],
                "project": "Build a legal home lab: document a small network, capture and explain benign traffic, run a deliberately vulnerable app locally, map findings to OWASP, then write a remediation and incident report. Never test systems without permission.",
                "docs": ["https://owasp.org/www-project-top-ten/", "https://www.wireshark.org/docs/", "https://nmap.org/book/"],
            }
        elif "frontend" in role or "front-end" in role or "ui" in role:
            roadmap = {
                "focus": ["semantic HTML and responsive CSS", "JavaScript/TypeScript and browser APIs", "React composition, state, forms and routing", "accessibility and design systems", "performance, testing and error handling", "deployment, analytics and product iteration"],
                "project": "Build an accessible, responsive application dashboard with real loading/error/empty states. Explore keyboard navigation, screen-reader labels, responsive layouts, form validation, component tests, Lighthouse performance and user feedback.",
                "docs": ["https://developer.mozilla.org/", "https://react.dev/learn", "https://www.typescriptlang.org/docs/"],
            }
        elif "full" in role:
            roadmap = {
                "focus": ["HTML, CSS, JavaScript and TypeScript foundations", "React architecture, state, forms and accessibility", "REST APIs with Django REST or FastAPI", "SQL data modeling, migrations and transactions", "authentication, authorization, testing and security", "Docker, CI, cloud deployment, observability and performance"],
                "project": "Build and deploy a full-stack learning or career platform. Explore role-based access, validated APIs, relational schema design, pagination, file handling, automated tests, security boundaries, logs, deployment and a clear architecture README.",
                "docs": ["https://react.dev/learn", "https://www.django-rest-framework.org/", "https://www.postgresql.org/docs/"],
            }
        elif "machine learning" in role or " ai" in f" {role}" or "artificial intelligence" in role:
            roadmap = {
                "focus": ["Python, NumPy, pandas and data cleaning", "probability, statistics and model objectives", "scikit-learn pipelines and feature engineering", "train/validation/test splits and leakage prevention", "model evaluation, error analysis and responsible AI", "API serving, monitoring, reproducibility and cloud deployment"],
                "project": "Build an end-to-end model on a documented public dataset. Compare a simple baseline with at least two models, use leakage-safe splits, report precision/recall and failure slices, package inference behind an API, and document limitations and monitoring.",
                "docs": ["https://scikit-learn.org/stable/user_guide.html", "https://pandas.pydata.org/docs/", "https://pytorch.org/tutorials/"],
            }
        elif "data engineer" in role:
            roadmap = {
                "focus": ["advanced SQL, joins, windows and query plans", "Python ingestion, APIs and data formats", "dimensional modeling and warehouse design", "batch ETL, orchestration and idempotency", "data quality, lineage, testing and observability", "cloud storage, Spark basics and cost-aware operations"],
                "project": "Build a reliable pipeline from a public API into a modeled warehouse and dashboard. Explore incremental loads, retries, schema changes, deduplication, data-quality checks, orchestration, lineage, alerting and recovery from a failed run.",
                "docs": ["https://www.postgresql.org/docs/", "https://airflow.apache.org/docs/", "https://docs.getdbt.com/"],
            }
        elif "data scientist" in role or "data analyst" in role:
            roadmap = {
                "focus": ["SQL and exploratory data analysis", "statistics, sampling and experiment design", "Python with pandas and visualization", "feature engineering and model baselines", "validation, uncertainty and communicating results", "reproducible notebooks and stakeholder recommendations"],
                "project": "Investigate a real public dataset and answer a specific decision question. Explore data quality, define metrics before modeling, compare a baseline, quantify uncertainty, inspect subgroup errors and deliver a concise report with reproducible code.",
                "docs": ["https://pandas.pydata.org/docs/", "https://scikit-learn.org/stable/user_guide.html", "https://www.statsmodels.org/stable/index.html"],
            }
        elif "devops" in role or "cloud" in role:
            roadmap = {
                "focus": ["Linux, networking, DNS and TLS fundamentals", "cloud IAM, compute, storage and networking", "Docker images and container operation", "CI/CD, infrastructure as code and deployment strategies", "metrics, logs, tracing, alerting and incident response", "security, backups, scaling and cloud cost controls"],
                "project": "Deploy a containerized API with a managed database and automated pipeline. Explore least-privilege IAM, secrets, health checks, rollback, dashboards, alerts, backups, load testing and a short incident runbook.",
                "docs": ["https://docs.docker.com/", "https://developer.hashicorp.com/terraform/docs", "https://docs.aws.amazon.com/"],
            }
        else:
            roadmap = {
                "focus": ["programming fundamentals, Git and command line", "data structures, algorithms and complexity", "object-oriented design and clean code", "HTTP, APIs, SQL and application architecture", "automated testing, debugging and secure coding", "deployment, system design and technical communication"],
                "project": "Build and deploy a complete application that solves a problem you named in career discovery. Explore requirements, architecture, edge cases, test coverage, security, performance, deployment and feedback from at least two users.",
                "docs": ["https://docs.python.org/3/tutorial/", "https://git-scm.com/doc", "https://developer.mozilla.org/"],
            }

        from app.services.career_signals import extract_interest_summary, extract_skill_evidence
        answer_skills = extract_skill_evidence(discovery_answers)
        resume_evidence = set(extract_skill_evidence("", current_skills or []))
        interests = extract_interest_summary(discovery_answers, limit=4)
        interest_note = (
            "Personalized from your saved interests: " + ", ".join(interests) + "."
            if interests else "Personalized from your saved profile and current skill evidence."
        )
        baseline_note = (
            "Resume evidence to build on: " + ", ".join((current_skills or [])[:8]) + "."
            if current_skills else "No resume skills were extracted yet; start with the diagnostic and record what you already know."
        )

        total_weeks = max(6, duration_weeks)
        base_weeks, extra_weeks = divmod(total_weeks, 6)
        phase_names = [
            "Baseline and setup", "Core concepts", "Role-specific tools",
            "Guided practice", "Capstone project", "Polish and job readiness",
        ]
        phase_actions = [
            "Assess the topics below with a short diagnostic; set up a clean repository and study plan.",
            "Study each topic and explain it in your own words; solve small exercises before using frameworks.",
            "Use the named tools on small tasks. Record commands, decisions and common failure modes.",
            "Complete 3 progressively harder exercises and review solutions for correctness and trade-offs.",
            roadmap["project"],
            "Polish the project, write tests and documentation, rehearse a technical walkthrough, and map evidence to job requirements.",
        ]
        phase_topics = [
            "Prerequisites; Git; command line; diagnostic for " + "; ".join(roadmap["focus"][:2]),
            "; ".join(roadmap["focus"][0:2]),
            "; ".join(roadmap["focus"][2:4]),
            "; ".join(roadmap["focus"][4:6]),
            "Integrate all role skills in the capstone: " + "; ".join(roadmap["focus"]),
            "Review quality, deployment and role evidence across: " + "; ".join(roadmap["focus"]),
        ]
        milestones = []
        next_week = 1
        for index, (name, action) in enumerate(zip(phase_names, phase_actions)):
            weeks = base_weeks + (1 if index < extra_weeks else 0)
            week_start = next_week
            week_end = week_start + weeks - 1
            next_week = week_end + 1
            phase_focus = roadmap["focus"][max(0, index - 1):min(len(roadmap["focus"]), index + 1)]
            expected_evidence = set(extract_skill_evidence("; ".join(phase_focus)))
            detected_gaps = sorted(expected_evidence - resume_evidence)
            priority_note = (
                f"Resume keyword gaps to verify or strengthen: {', '.join(detected_gaps[:6])}."
                if detected_gaps else "Resume evidence already covers these areas; focus on deeper implementation and explaining trade-offs."
            )
            practice = (
                f"Practice: explain each topic from first principles; implement a small example; test an edge case; and write down one trade-off. {priority_note}"
                if index in (1, 2, 3) else ""
            )
            personalization = ""
            if index == 0:
                answer_evidence = f" Discovery evidence: {', '.join(answer_skills[:8])}." if answer_skills else ""
                personalization = f"Personalization: {interest_note} {baseline_note}{answer_evidence}\n"
            description = (
                f"Phase {index + 1} - Weeks {week_start}-{week_end}.\n"
                f"Focus topics: {phase_topics[index]}.\n"
                f"Work: {action}\n"
                f"{practice + chr(10) if practice else ''}"
                + personalization
                + "Deliverable: Commit your work, explain the key decisions in your own words, demonstrate one tested edge case, and record one next improvement."
            )
            if index == 4:
                description += "\nProject depth checklist: define the user and problem; turn the problem into functional requirements; sketch the architecture and data flow; compare two design choices and trade-offs; implement a working vertical slice; add unit and integration tests; handle errors and edge cases; assess security, accessibility, and privacy; measure one quality or performance metric; deploy a demo; write setup instructions; and reflect on what you would improve next."
                if interests:
                    description += f"\nProject theme: Use a problem related to {', '.join(interests[:3])} that you described in career discovery."
            milestones.append({
                "title": f"Phase {index + 1}: {name}",
                "description": description,
                "category": "project" if index == 4 else "learning",
                "estimated_hours": max(12, weeks * 8),
                "sequence_number": index + 1,
                "resources": roadmap["docs"],
            })

        return {
            "title": f"Development Roadmap for {role_name}",
            "description": f"[plan-v2] A personalized {total_weeks}-week plan for {role_name}, grounded in your resume evidence and saved career discovery interests.",
            "target_duration_weeks": total_weeks,
            "milestones": milestones,
        }

    async def _get_or_create_role(
        self, db: AsyncSession, role_name: str, category: str
    ) -> CareerRole:
        """Get or create a career role."""
        result = await db.execute(
            select(CareerRole).where(CareerRole.name == role_name)
        )
        role = result.scalar_one_or_none()
        
        if not role:
            role = CareerRole(
                name=role_name,
                category=category,
                description=f"Career in {role_name}",
            )
            db.add(role)
            await db.flush()
        
        return role


# Singleton instance
career_recommendation_service = CareerRecommendationService()
