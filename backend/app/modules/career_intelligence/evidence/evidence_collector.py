"""
Evidence Collector

Collects and normalizes evidence from various sources:
- Career discovery responses
- Student profile data
- Projects and experience
- Skills and certifications
- Resume data
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.student import (
    StudentProfile, Project, Certification, 
    StudentSkill, EducationRecord
)
from app.db.models.career import CareerDiscoverySession, CareerDiscoveryResponse
from app.db.models.resume import Resume, ResumeExtraction
from ..types import (
    StudentFeatures, SkillEvidence, EvidenceType, 
    EvidenceState, ProficiencyLevel
)
from ..taxonomy.skills import normalize_skill_name


class EvidenceCollector:
    """Collects and normalizes evidence from student profile and activities."""
    
    async def collect_student_features(
        self,
        db: AsyncSession,
        student_profile_id: UUID,
        session_id: Optional[UUID] = None
    ) -> StudentFeatures:
        """
        Collect and normalize all evidence for a student.
        
        Args:
            db: Database session
            student_profile_id: Student profile UUID
            session_id: Optional discovery session UUID
            
        Returns:
            StudentFeatures with normalized data
        """
        # Load student profile
        result = await db.execute(
            select(StudentProfile)
            .where(StudentProfile.id == student_profile_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Student profile {student_profile_id} not found")
        
        features = StudentFeatures()
        
        # Collect from discovery session if provided
        if session_id:
            discovery_features = await self._collect_from_discovery(db, session_id)
            features.interests = discovery_features.get("interests", [])
            features.work_preferences = discovery_features.get("work_preferences", {})
        
        # Collect education
        education = await self._collect_education(db, student_profile_id)
        features.education_level = education.get("level")
        features.field_of_study = education.get("field")
        features.graduation_year = education.get("graduation_year")
        
        # Collect skills with evidence
        features.skills = await self._collect_skills(db, student_profile_id)
        
        # Collect projects
        project_data = await self._collect_projects(db, student_profile_id)
        features.has_projects = project_data["count"] > 0
        features.project_count = project_data["count"]
        
        # Collect experience
        features.has_internship = profile.current_status == "employed"
        features.work_experience_months = 0  # Calculate from projects/experience
        
        # Collect preferences from profile
        features.preferred_industries = profile.preferred_locations or []
        features.willing_to_relocate = getattr(profile, "willing_to_relocate", False)
        
        # Salary expectations
        if profile.expected_salary_min:
            features.salary_expectations = {
                "min": profile.expected_salary_min,
                "max": profile.expected_salary_max or profile.expected_salary_min
            }
        
        return features
    
    async def _collect_from_discovery(
        self,
        db: AsyncSession,
        session_id: UUID
    ) -> Dict[str, Any]:
        """Extract features from discovery session responses."""
        result = await db.execute(
            select(CareerDiscoveryResponse)
            .where(CareerDiscoveryResponse.session_id == session_id)
            .order_by(CareerDiscoveryResponse.sequence_number)
        )
        responses = result.scalars().all()
        
        interests = []
        work_preferences = {}
        
        for response in responses:
            # Parse responses to extract interests
            question_lower = response.question_text.lower()
            answer_lower = response.response_text.lower()
            
            # Interest detection (simple keyword matching)
            if "interest" in question_lower or "enjoy" in question_lower:
                if "python" in answer_lower or "programming" in answer_lower:
                    interests.append("programming")
                if "data" in answer_lower or "analysis" in answer_lower:
                    interests.append("data_analysis")
                if "design" in answer_lower or "ui" in answer_lower or "ux" in answer_lower:
                    interests.append("design")
                if "security" in answer_lower or "cybersecurity" in answer_lower:
                    interests.append("security")
                if "machine learning" in answer_lower or "ai" in answer_lower or "ml" in answer_lower:
                    interests.append("machine_learning")
            
            # Work preference detection
            if "environment" in question_lower or "work style" in question_lower:
                if "team" in answer_lower or "collaborative" in answer_lower:
                    work_preferences["collaboration"] = "high"
                elif "independent" in answer_lower or "solo" in answer_lower:
                    work_preferences["collaboration"] = "low"
                
                if "remote" in answer_lower:
                    work_preferences["remote_preference"] = "remote"
                elif "office" in answer_lower:
                    work_preferences["remote_preference"] = "onsite"
        
        return {
            "interests": list(set(interests)),
            "work_preferences": work_preferences
        }
    
    async def _collect_education(
        self,
        db: AsyncSession,
        student_profile_id: UUID
    ) -> Dict[str, Any]:
        """Collect education information."""
        result = await db.execute(
            select(EducationRecord)
            .where(EducationRecord.student_profile_id == student_profile_id)
            .order_by(EducationRecord.start_date.desc())
        )
        education_records = result.scalars().all()
        
        if not education_records:
            return {}
        
        # Get the most recent/highest degree
        latest = education_records[0]
        
        return {
            "level": latest.degree,
            "field": latest.field_of_study,
            "graduation_year": latest.end_date.year if latest.end_date else None,
            "institution": latest.institution_name
        }
    
    async def _collect_skills(
        self,
        db: AsyncSession,
        student_profile_id: UUID
    ) -> List[SkillEvidence]:
        """Collect skills with evidence."""
        result = await db.execute(
            select(StudentSkill)
            .where(StudentSkill.student_profile_id == student_profile_id)
        )
        student_skills = result.scalars().all()
        
        evidence_list = []
        
        for student_skill in student_skills:
            # Determine evidence state based on available data
            evidence_state = EvidenceState.DECLARED_UNVERIFIED
            evidence_type = EvidenceType.DECLARED
            
            if student_skill.is_verified:
                evidence_state = EvidenceState.DEMONSTRATED
                
                # Determine evidence type
                if student_skill.evidence_type == "project":
                    evidence_type = EvidenceType.PROJECT
                elif student_skill.evidence_type == "work":
                    evidence_type = EvidenceType.WORK_EXPERIENCE
                elif student_skill.evidence_type == "certification":
                    evidence_type = EvidenceType.CERTIFICATION
                else:
                    evidence_type = EvidenceType.ASSESSMENT
            elif student_skill.evidence_description:
                evidence_state = EvidenceState.PARTIALLY_DEMONSTRATED
                evidence_type = EvidenceType.PROJECT
            
            # Map proficiency
            proficiency_map = {
                "beginner": ProficiencyLevel.BEGINNER,
                "intermediate": ProficiencyLevel.INTERMEDIATE,
                "advanced": ProficiencyLevel.ADVANCED,
                "expert": ProficiencyLevel.EXPERT
            }
            proficiency = proficiency_map.get(
                student_skill.proficiency_level,
                ProficiencyLevel.BEGINNER
            )
            
            # Get skill name from relationship
            skill_name = None
            if student_skill.skill:
                skill_name = student_skill.skill.name
            
            if skill_name:
                evidence = SkillEvidence(
                    skill_name=normalize_skill_name(skill_name) or skill_name,
                    skill_id=student_skill.skill_id,
                    evidence_type=evidence_type,
                    evidence_state=evidence_state,
                    proficiency_level=proficiency,
                    source_description=student_skill.evidence_description or "Student declared skill",
                    confidence=1.0 if student_skill.is_verified else 0.5
                )
                evidence_list.append(evidence)
        
        return evidence_list
    
    async def _collect_projects(
        self,
        db: AsyncSession,
        student_profile_id: UUID
    ) -> Dict[str, Any]:
        """Collect project information."""
        result = await db.execute(
            select(Project)
            .where(Project.student_profile_id == student_profile_id)
        )
        projects = result.scalars().all()
        
        return {
            "count": len(projects),
            "projects": [
                {
                    "title": p.title,
                    "technologies": p.technologies,
                    "role": p.role
                }
                for p in projects
            ]
        }
    
    async def extract_skills_from_projects(
        self,
        db: AsyncSession,
        student_profile_id: UUID
    ) -> List[SkillEvidence]:
        """Extract skill evidence from project technologies."""
        result = await db.execute(
            select(Project)
            .where(Project.student_profile_id == student_profile_id)
        )
        projects = result.scalars().all()
        
        skill_evidence = []
        
        for project in projects:
            for tech in project.technologies:
                canonical_name = normalize_skill_name(tech)
                
                if canonical_name:
                    evidence = SkillEvidence(
                        skill_name=canonical_name,
                        evidence_type=EvidenceType.PROJECT,
                        evidence_state=EvidenceState.DEMONSTRATED,
                        proficiency_level=None,  # Unknown from project alone
                        source_description=f"Used in project: {project.title}",
                        confidence=0.8
                    )
                    skill_evidence.append(evidence)
        
        return skill_evidence
    
    async def collect_resume_skills(
        self,
        db: AsyncSession,
        student_profile_id: UUID
    ) -> List[SkillEvidence]:
        """Collect skills from resume if available."""
        result = await db.execute(
            select(Resume)
            .where(
                Resume.student_profile_id == student_profile_id,
                Resume.is_primary == True
            )
        )
        resume = result.scalar_one_or_none()
        
        if not resume:
            return []
        
        # Get extraction data
        extraction_result = await db.execute(
            select(ResumeExtraction)
            .where(ResumeExtraction.resume_id == resume.id)
        )
        extraction = extraction_result.scalar_one_or_none()
        
        if not extraction or not extraction.skills:
            return []
        
        skill_evidence = []
        
        # Parse skills from extraction
        skills_data = extraction.skills
        if isinstance(skills_data, dict):
            all_skills = []
            all_skills.extend(skills_data.get("technical", []))
            all_skills.extend(skills_data.get("tools", []))
            all_skills.extend(skills_data.get("languages", []))
            
            for skill_text in all_skills:
                canonical_name = normalize_skill_name(skill_text)
                
                if canonical_name:
                    evidence = SkillEvidence(
                        skill_name=canonical_name,
                        evidence_type=EvidenceType.RESUME,
                        evidence_state=EvidenceState.DECLARED_UNVERIFIED,
                        proficiency_level=None,
                        source_description=f"Found in resume",
                        confidence=0.6
                    )
                    skill_evidence.append(evidence)
        
        return skill_evidence
