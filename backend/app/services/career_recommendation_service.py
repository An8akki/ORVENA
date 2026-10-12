"""Service layer for career recommendations and roadmaps."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json

from app.db.models.student import StudentProfile, StudentSkill, EducationRecord
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
        education_data = [
            {
                "institution": e.institution_name,
                "degree": e.degree_name,
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
            )
            session = session_result.scalar_one_or_none()
            if session and session.analysis_data:
                preferences = session.analysis_data.get("preferences", {})

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
        """Get all recommendations for a profile."""
        result = await db.execute(
            select(CareerRecommendation)
            .where(CareerRecommendation.student_profile_id == profile_id)
            .options(selectinload(CareerRecommendation.career_role))
            .order_by(CareerRecommendation.recommendation_rank)
        )
        return list(result.scalars().all())

    async def generate_roadmap(
        self,
        db: AsyncSession,
        profile_id: UUID,
        career_goal_id: UUID,
        recommendation_id: Optional[UUID] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        target_timeline_weeks: int = 12,
    ) -> CareerRoadmap:
        """Generate a personalized career development roadmap."""
        llm = get_llm_provider()
        
        # Get career goal
        goal_result = await db.execute(
            select(CareerGoal).where(CareerGoal.id == career_goal_id)
        )
        career_goal = goal_result.scalar_one_or_none()
        if not career_goal:
            raise NotFoundError("Career goal not found")

        # Get target role from goal or recommendation
        target_role = None
        if career_goal.career_role_id:
            role_result = await db.execute(
                select(CareerRole).where(CareerRole.id == career_goal.career_role_id)
            )
            target_role = role_result.scalar_one_or_none()
        
        # If no role from goal, try to get from recommendation
        if not target_role and recommendation_id:
            rec_result = await db.execute(
                select(CareerRecommendation)
                .where(CareerRecommendation.id == recommendation_id)
                .options(selectinload(CareerRecommendation.career_role))
            )
            recommendation = rec_result.scalar_one_or_none()
            if recommendation:
                target_role = recommendation.career_role
        
        if not target_role:
            raise ValidationError("Could not determine target career role")

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
        context = f"""Target Role: {target_role.name}
Goal: {career_goal.title}
Timeline: {target_timeline_weeks} weeks
Current Level: Entry/Junior

Student Profile:
- Name: {profile.full_name if profile else "Student"}
- Current Skills: {', '.join([s.skill.name for s in skills[:10]])}

Create a detailed development roadmap to prepare for this role and achieve the career goal."""

        # Generate roadmap with AI
        response = await llm.generate_with_system(
            system_prompt=self.ROADMAP_SYSTEM_PROMPT,
            user_message=context,
            temperature=0.7,
            max_tokens=2000,
        )

        # Parse roadmap data
        roadmap_data = self._parse_roadmap(response.content, target_role.name)

        # Create roadmap
        roadmap = CareerRoadmap(
            student_profile_id=profile_id,
            career_goal_id=career_goal_id,
            recommendation_id=recommendation_id,
            title=title or roadmap_data.get("title", f"Roadmap to {target_role.name}"),
            description=description or roadmap_data.get("description", ""),
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
            .options(
                selectinload(CareerRoadmap.milestones),
                selectinload(CareerRoadmap.target_role),
            )
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
            .options(selectinload(RoadmapMilestone.roadmap))
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

        # Recalculate progress
        roadmap = milestone.roadmap
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
                    for r in session.responses[:3]  # Include first 3 Q&As
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

    def _parse_roadmap(self, ai_response: str, role_name: str) -> Dict[str, Any]:
        """Parse AI roadmap response."""
        try:
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        
        # Fallback roadmap
        return {
            "title": f"Development Roadmap for {role_name}",
            "description": f"Personalized plan to become a {role_name}",
            "target_duration_weeks": 12,
            "milestones": [
                {
                    "title": "Foundation Skills",
                    "description": "Build core technical skills",
                    "category": "learning",
                    "estimated_hours": 40,
                    "sequence_number": 1,
                    "resources": ["Online courses", "Documentation"],
                },
                {
                    "title": "Build Portfolio Project",
                    "description": "Create a showcase project",
                    "category": "project",
                    "estimated_hours": 60,
                    "sequence_number": 2,
                    "resources": ["GitHub", "Project ideas"],
                },
            ],
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
