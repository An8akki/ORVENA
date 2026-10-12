"""
Skill Assessor

Evaluates a student's starting level for a target role by assessing
available evidence across required skills, experience, and prerequisites.

Separates declared skills from demonstrated competence.
"""
from typing import List, Dict, Optional, Tuple
from uuid import UUID

from ..types import (
    StudentFeatures, SkillEvidence, EvidenceState, 
    ProficiencyLevel, RoleRequirement, RequirementImportance
)
from ..taxonomy.requirements import get_role_requirements, check_requirement_match


class SkillAssessment:
    """Result of skill assessment for a target role."""
    
    def __init__(
        self,
        role_key: str,
        role_name: str,
        student_profile_id: UUID
    ):
        self.role_key = role_key
        self.role_name = role_name
        self.student_profile_id = student_profile_id
        
        # Skill categorization
        self.demonstrated_skills: List[Dict] = []
        self.partially_demonstrated_skills: List[Dict] = []
        self.declared_unverified_skills: List[Dict] = []
        self.not_demonstrated_skills: List[Dict] = []
        self.not_assessed_skills: List[Dict] = []
        
        # Overall assessment
        self.starting_level: str = "beginner"  # beginner, intermediate, advanced
        self.readiness_score: float = 0.0
        self.prerequisite_gaps: List[str] = []
        self.recommended_assessments: List[str] = []
        
        # Summary
        self.summary: str = ""
        self.strengths: List[str] = []
        self.areas_for_growth: List[str] = []
        self.next_actions: List[str] = []


class SkillAssessor:
    """
    Assess student's starting level for a target role.
    
    Evaluates evidence quality and distinguishes between:
    - Demonstrated competence (strong evidence)
    - Partial demonstration (some evidence)
    - Declared but unverified (self-reported)
    - Not demonstrated (no evidence)
    - Not assessed (haven't checked)
    """
    
    def assess_for_role(
        self,
        role_key: str,
        role_name: str,
        student_features: StudentFeatures,
        student_profile_id: UUID
    ) -> SkillAssessment:
        """
        Perform comprehensive skill assessment for a target role.
        
        Args:
            role_key: Role identifier
            role_name: Role display name
            student_features: Collected student evidence
            student_profile_id: Student UUID
            
        Returns:
            SkillAssessment with detailed breakdown
        """
        assessment = SkillAssessment(role_key, role_name, student_profile_id)
        
        # Get requirements for the role
        requirements = get_role_requirements(role_key)
        
        # Assess each requirement
        for requirement in requirements:
            match_result = check_requirement_match(
                requirement,
                student_features.skills
            )
            
            # Categorize based on evidence state
            skill_info = {
                "skill_name": requirement.skill_name,
                "requirement_text": requirement.requirement_text,
                "importance": requirement.importance,
                "match_result": match_result
            }
            
            if match_result["state"] == "demonstrated":
                assessment.demonstrated_skills.append(skill_info)
            elif match_result["state"] == "partial":
                assessment.partially_demonstrated_skills.append(skill_info)
            elif match_result["state"] == "unverified":
                assessment.declared_unverified_skills.append(skill_info)
            elif match_result["state"] == "not_assessed":
                assessment.not_assessed_skills.append(skill_info)
            else:
                assessment.not_demonstrated_skills.append(skill_info)
        
        # Calculate readiness score
        assessment.readiness_score = self._calculate_readiness_score(
            assessment,
            requirements
        )
        
        # Determine starting level
        assessment.starting_level = self._determine_starting_level(
            assessment,
            student_features
        )
        
        # Identify prerequisite gaps
        assessment.prerequisite_gaps = self._identify_prerequisite_gaps(
            assessment,
            requirements
        )
        
        # Recommend assessments for unverified skills
        assessment.recommended_assessments = self._recommend_assessments(
            assessment
        )
        
        # Generate summary and recommendations
        assessment.strengths = self._identify_strengths(assessment)
        assessment.areas_for_growth = self._identify_growth_areas(assessment)
        assessment.next_actions = self._suggest_next_actions(assessment)
        assessment.summary = self._generate_summary(
            assessment,
            student_features
        )
        
        return assessment
    
    def _calculate_readiness_score(
        self,
        assessment: SkillAssessment,
        requirements: List[RoleRequirement]
    ) -> float:
        """
        Calculate overall readiness score (0-1).
        
        Weights evidence states differently:
        - Demonstrated: 1.0
        - Partial: 0.5
        - Declared unverified: 0.25
        - Not assessed/demonstrated: 0.0
        """
        if not requirements:
            return 0.0
        
        total_weight = 0.0
        earned_weight = 0.0
        
        for req in requirements:
            # Weight by importance
            importance_weight = {
                RequirementImportance.REQUIRED: 1.0,
                RequirementImportance.PREFERRED: 0.5,
                RequirementImportance.OPTIONAL: 0.25
            }.get(req.importance, 0.5)
            
            total_weight += importance_weight
            
            # Find matching skill in assessment
            skill_name = req.skill_name
            
            # Check demonstrated
            if any(s["skill_name"] == skill_name for s in assessment.demonstrated_skills):
                earned_weight += importance_weight * 1.0
            # Check partial
            elif any(s["skill_name"] == skill_name for s in assessment.partially_demonstrated_skills):
                earned_weight += importance_weight * 0.5
            # Check declared
            elif any(s["skill_name"] == skill_name for s in assessment.declared_unverified_skills):
                earned_weight += importance_weight * 0.25
        
        return earned_weight / total_weight if total_weight > 0 else 0.0
    
    def _determine_starting_level(
        self,
        assessment: SkillAssessment,
        student_features: StudentFeatures
    ) -> str:
        """
        Determine starting level based on evidence.
        
        Levels:
        - beginner: Little to no demonstrated experience
        - intermediate: Some demonstrated skills, needs practice
        - advanced: Strong demonstrated skills, ready for role
        """
        readiness = assessment.readiness_score
        demonstrated_count = len(assessment.demonstrated_skills)
        project_count = student_features.project_count
        has_experience = student_features.has_internship
        
        # Advanced: High readiness + demonstrated skills + experience
        if readiness >= 0.7 and demonstrated_count >= 3 and (project_count >= 3 or has_experience):
            return "advanced"
        
        # Intermediate: Moderate readiness + some demonstrated skills
        if readiness >= 0.4 and demonstrated_count >= 2:
            return "intermediate"
        
        # Beginner: Low readiness or mostly unverified skills
        return "beginner"
    
    def _identify_prerequisite_gaps(
        self,
        assessment: SkillAssessment,
        requirements: List[RoleRequirement]
    ) -> List[str]:
        """Identify critical missing prerequisites."""
        gaps = []
        
        # Check required skills that are not demonstrated
        for req in requirements:
            if req.importance == RequirementImportance.REQUIRED:
                skill_name = req.skill_name
                
                # Not in demonstrated skills
                if not any(s["skill_name"] == skill_name for s in assessment.demonstrated_skills):
                    # Check if partially demonstrated or worse
                    if any(s["skill_name"] == skill_name for s in assessment.partially_demonstrated_skills):
                        gaps.append(f"Strengthen {req.requirement_text} (partially demonstrated)")
                    elif any(s["skill_name"] == skill_name for s in assessment.declared_unverified_skills):
                        gaps.append(f"Verify {req.requirement_text} through projects or assessments")
                    else:
                        gaps.append(f"Develop {req.requirement_text} (required skill)")
        
        return gaps
    
    def _recommend_assessments(
        self,
        assessment: SkillAssessment
    ) -> List[str]:
        """Recommend assessments for unverified skills."""
        recommendations = []
        
        # For declared but unverified skills
        for skill_info in assessment.declared_unverified_skills:
            skill_name = skill_info["skill_name"]
            recommendations.append(
                f"Complete a practical project demonstrating {skill_name} skills"
            )
        
        # For not assessed skills
        for skill_info in assessment.not_assessed_skills[:3]:  # Limit to 3
            skill_name = skill_info["skill_name"]
            recommendations.append(
                f"Take an assessment or build a project using {skill_name}"
            )
        
        return recommendations[:5]  # Limit total recommendations
    
    def _identify_strengths(self, assessment: SkillAssessment) -> List[str]:
        """Identify student's strengths for this role."""
        strengths = []
        
        # Demonstrated required skills are major strengths
        for skill_info in assessment.demonstrated_skills:
            if skill_info["importance"] == RequirementImportance.REQUIRED:
                strengths.append(
                    f"Demonstrated {skill_info['skill_name']}: {skill_info['match_result'].get('evidence', '')}"
                )
        
        # High readiness is a strength
        if assessment.readiness_score >= 0.6:
            strengths.append(
                f"Strong readiness score of {assessment.readiness_score:.0%}"
            )
        
        return strengths
    
    def _identify_growth_areas(self, assessment: SkillAssessment) -> List[str]:
        """Identify areas for growth and development."""
        growth_areas = []
        
        # Missing required skills
        for skill_info in assessment.not_demonstrated_skills:
            if skill_info["importance"] == RequirementImportance.REQUIRED:
                growth_areas.append(
                    f"Need to develop: {skill_info['requirement_text']}"
                )
        
        # Partially demonstrated skills need strengthening
        for skill_info in assessment.partially_demonstrated_skills:
            growth_areas.append(
                f"Strengthen: {skill_info['requirement_text']}"
            )
        
        # Unverified skills need evidence
        if len(assessment.declared_unverified_skills) > 2:
            growth_areas.append(
                "Build projects to demonstrate claimed skills"
            )
        
        return growth_areas[:6]  # Limit to top 6
    
    def _suggest_next_actions(self, assessment: SkillAssessment) -> List[str]:
        """Suggest concrete next actions."""
        actions = []
        
        # Based on starting level
        if assessment.starting_level == "beginner":
            actions.append(
                "Start with foundational learning in required skills"
            )
            
            # Suggest learning first missing required skill
            for skill_info in assessment.not_demonstrated_skills:
                if skill_info["importance"] == RequirementImportance.REQUIRED:
                    actions.append(
                        f"Begin learning {skill_info['skill_name']}"
                    )
                    break
        
        elif assessment.starting_level == "intermediate":
            actions.append(
                "Focus on building portfolio projects to demonstrate skills"
            )
            
            # Address gaps
            if assessment.prerequisite_gaps:
                actions.append(assessment.prerequisite_gaps[0])
        
        else:  # advanced
            actions.append(
                "You're ready to pursue opportunities in this role"
            )
            actions.append(
                "Focus on specialized skills to stand out"
            )
        
        # Add assessment recommendations
        if assessment.recommended_assessments:
            actions.append(assessment.recommended_assessments[0])
        
        return actions[:4]  # Limit to 4 actions
    
    def _generate_summary(
        self,
        assessment: SkillAssessment,
        student_features: StudentFeatures
    ) -> str:
        """Generate comprehensive assessment summary."""
        parts = []
        
        # Starting level statement
        level_descriptions = {
            "beginner": "You're at a beginner level for this role.",
            "intermediate": "You're at an intermediate level for this role.",
            "advanced": "You're at an advanced level and ready for this role."
        }
        parts.append(level_descriptions[assessment.starting_level])
        
        # Demonstrated skills
        if assessment.demonstrated_skills:
            skill_names = [s["skill_name"] for s in assessment.demonstrated_skills[:3]]
            parts.append(
                f"You have demonstrated competence in {', '.join(skill_names)}."
            )
        
        # Readiness score
        parts.append(
            f"Your readiness score is {assessment.readiness_score:.0%}."
        )
        
        # Gaps
        if assessment.prerequisite_gaps:
            parts.append(
                f"Key areas to develop: {assessment.prerequisite_gaps[0]}."
            )
        
        # Unverified skills warning
        if len(assessment.declared_unverified_skills) > 0:
            parts.append(
                f"You've claimed {len(assessment.declared_unverified_skills)} skills "
                f"that need verification through projects or work experience."
            )
        
        # Next step
        if assessment.next_actions:
            parts.append(
                f"Recommended next step: {assessment.next_actions[0]}"
            )
        
        return " ".join(parts)
    
    def compare_current_to_target(
        self,
        current_assessment: SkillAssessment,
        target_role_requirements: List[RoleRequirement]
    ) -> Dict:
        """
        Compare current skills to target role requirements.
        
        Returns:
            Dict with gap analysis and development path
        """
        gaps = {
            "missing_required": [],
            "missing_preferred": [],
            "needs_verification": [],
            "ready_skills": []
        }
        
        for req in target_role_requirements:
            skill_name = req.skill_name
            
            # Check if demonstrated
            if any(s["skill_name"] == skill_name for s in current_assessment.demonstrated_skills):
                gaps["ready_skills"].append(req.requirement_text)
            # Check if claimed but unverified
            elif any(s["skill_name"] == skill_name for s in current_assessment.declared_unverified_skills):
                gaps["needs_verification"].append(req.requirement_text)
            # Missing
            elif req.importance == RequirementImportance.REQUIRED:
                gaps["missing_required"].append(req.requirement_text)
            else:
                gaps["missing_preferred"].append(req.requirement_text)
        
        return gaps
    
    def estimate_learning_time(
        self,
        assessment: SkillAssessment,
        target_hours_per_week: int = 10
    ) -> Dict:
        """
        Estimate time needed to reach job-ready level.
        
        Args:
            assessment: Current skill assessment
            target_hours_per_week: Available study hours
            
        Returns:
            Dict with time estimates
        """
        # Estimate hours per skill based on starting point
        hours_per_skill = {
            "not_demonstrated": 40,  # Learn from scratch
            "partially_demonstrated": 20,  # Strengthen existing
            "declared_unverified": 10,  # Verify through projects
        }
        
        total_hours = 0
        
        # Count gaps
        total_hours += len(assessment.not_demonstrated_skills) * hours_per_skill["not_demonstrated"]
        total_hours += len(assessment.partially_demonstrated_skills) * hours_per_skill["partially_demonstrated"]
        total_hours += len(assessment.declared_unverified_skills) * hours_per_skill["declared_unverified"]
        
        weeks_needed = total_hours / target_hours_per_week if target_hours_per_week > 0 else 0
        
        return {
            "total_hours": total_hours,
            "weeks_at_current_pace": round(weeks_needed),
            "skills_to_develop": len(assessment.not_demonstrated_skills),
            "skills_to_strengthen": len(assessment.partially_demonstrated_skills),
            "skills_to_verify": len(assessment.declared_unverified_skills)
        }
