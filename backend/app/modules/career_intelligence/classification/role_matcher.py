"""
Role Fit Scorer

Calculates how well a student's profile matches each career role
using evidence-based, explainable scoring without requiring ML models.
"""
from typing import List, Dict, Optional
from uuid import UUID

from ..types import (
    StudentFeatures, RoleFitScore, SkillEvidence,
    EvidenceState, ConfidenceLevel, RequirementImportance
)
from ..taxonomy.roles import CAREER_ROLES, get_all_roles
from ..taxonomy.requirements import (
    get_role_requirements, calculate_role_match_score
)


class RoleFitScorer:
    """Calculate role fit scores using transparent, rule-based logic."""
    
    def __init__(self):
        """Initialize the scorer with role definitions."""
        self.roles = get_all_roles()
    
    def score_all_roles(
        self,
        student_features: StudentFeatures
    ) -> List[RoleFitScore]:
        """
        Score all roles and return ranked results.
        
        Args:
            student_features: Normalized student features and evidence
            
        Returns:
            List of RoleFitScore objects, sorted by fit_score descending
        """
        scores = []
        
        for role_key, role_data in CAREER_ROLES.items():
            score = self.score_role(role_key, role_data, student_features)
            scores.append(score)
        
        # Sort by fit score descending
        scores.sort(key=lambda x: x.fit_score, reverse=True)
        
        return scores
    
    def score_role(
        self,
        role_key: str,
        role_data: Dict,
        student_features: StudentFeatures
    ) -> RoleFitScore:
        """
        Calculate fit score for a specific role.
        
        Args:
            role_key: Role identifier
            role_data: Role definition
            student_features: Student features
            
        Returns:
            RoleFitScore with detailed breakdown
        """
        # Calculate skill match score
        skill_match = calculate_role_match_score(
            role_key,
            student_features.skills
        )
        
        # Ensure required keys exist
        if "required_matched" not in skill_match:
            skill_match["required_matched"] = 0
        if "required_total" not in skill_match:
            skill_match["required_total"] = 0
        
        # Calculate interest alignment
        interest_score = self._calculate_interest_alignment(
            role_data,
            student_features
        )
        
        # Calculate experience factor
        experience_score = self._calculate_experience_factor(
            role_data,
            student_features
        )
        
        # Combine scores with weights
        # Skills: 50%, Interests: 30%, Experience: 20%
        overall_score = (
            skill_match["score"] * 0.5 +
            interest_score * 0.3 +
            experience_score * 0.2
        )
        
        # Determine confidence level
        confidence = self._determine_confidence(
            overall_score,
            skill_match,
            student_features
        )
        
        # Generate explanation
        reasoning = self._generate_reasoning(
            role_data,
            skill_match,
            interest_score,
            experience_score,
            student_features
        )
        
        # Extract strengths and gaps
        strengths = self._identify_strengths(
            role_data,
            skill_match,
            student_features
        )
        
        gaps = self._identify_gaps(
            role_data,
            skill_match,
            student_features
        )
        
        # Determine next steps
        next_steps = self._suggest_next_steps(
            role_data,
            skill_match,
            gaps
        )
        
        return RoleFitScore(
            role_id=UUID(role_data["id"]),
            role_name=role_data["name"],
            role_category=role_data["family"],
            fit_score=overall_score,
            confidence=confidence,
            matching_skills=[m["skill"] for m in skill_match["matched"]],
            missing_skills=[m["skill"] for m in skill_match["missing"] if m["importance"] == RequirementImportance.REQUIRED],
            partially_matched_skills=[p["skill"] for p in skill_match["partial"]],
            strengths=strengths,
            gaps=gaps,
            reasoning=reasoning,
            next_steps=next_steps
        )
    
    def _calculate_interest_alignment(
        self,
        role_data: Dict,
        student_features: StudentFeatures
    ) -> float:
        """Calculate how well interests align with role."""
        if not student_features.interests:
            return 0.5  # Neutral when no interest data
        
        # Map interests to role families
        role_family = role_data["family"]
        
        interest_role_mapping = {
            "programming": ["software_engineering"],
            "data_analysis": ["ai_and_data"],
            "machine_learning": ["ai_and_data"],
            "design": ["product_design"],
            "security": ["security_infrastructure"],
        }
        
        alignment_count = 0
        for interest in student_features.interests:
            matching_families = interest_role_mapping.get(interest, [])
            if role_family in matching_families:
                alignment_count += 1
        
        # Also check role-specific interests
        role_name_lower = role_data["name"].lower()
        for interest in student_features.interests:
            if interest in role_name_lower:
                alignment_count += 1
        
        # Normalize to 0-1 scale
        return min(alignment_count / len(student_features.interests), 1.0) if student_features.interests else 0.5
    
    def _calculate_experience_factor(
        self,
        role_data: Dict,
        student_features: StudentFeatures
    ) -> float:
        """Calculate experience relevance."""
        score = 0.0
        
        # Projects count
        if student_features.project_count > 0:
            score += 0.3 * min(student_features.project_count / 3, 1.0)
        
        # Internship/work experience
        if student_features.has_internship:
            score += 0.3
        
        # Education relevance
        if student_features.field_of_study:
            field_lower = student_features.field_of_study.lower()
            role_family = role_data["family"]
            
            if role_family == "software_engineering" and any(
                keyword in field_lower 
                for keyword in ["computer", "software", "engineering"]
            ):
                score += 0.2
            elif role_family == "ai_and_data" and any(
                keyword in field_lower
                for keyword in ["data", "statistics", "mathematics", "computer"]
            ):
                score += 0.2
            elif role_family == "product_design" and any(
                keyword in field_lower
                for keyword in ["design", "art", "media", "hci"]
            ):
                score += 0.2
            else:
                score += 0.1  # Any relevant education
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _determine_confidence(
        self,
        overall_score: float,
        skill_match: Dict,
        student_features: StudentFeatures
    ) -> ConfidenceLevel:
        """Determine confidence level in the classification."""
        # High confidence criteria
        if overall_score > 0.7 and skill_match["required_matched"] >= skill_match["required_total"]:
            return ConfidenceLevel.HIGH
        
        # Medium confidence
        if overall_score > 0.5 and skill_match["required_matched"] > 0:
            return ConfidenceLevel.MEDIUM
        
        # Low confidence
        if overall_score > 0.3:
            return ConfidenceLevel.LOW
        
        # Uncertain
        return ConfidenceLevel.UNCERTAIN
    
    def _generate_reasoning(
        self,
        role_data: Dict,
        skill_match: Dict,
        interest_score: float,
        experience_score: float,
        student_features: StudentFeatures
    ) -> str:
        """Generate human-readable explanation of the score."""
        parts = []
        
        # Role introduction
        parts.append(f"{role_data['name']} is a candidate role.")
        
        # Skill match explanation
        if skill_match["required_matched"] == skill_match["required_total"]:
            parts.append(
                f"You meet all {skill_match['required_total']} required skills for this role."
            )
        elif skill_match["required_matched"] > 0:
            parts.append(
                f"You meet {skill_match['required_matched']} of {skill_match['required_total']} required skills."
            )
        else:
            parts.append(
                f"You don't yet demonstrate the required skills for this role."
            )
        
        # Matched skills
        if skill_match["matched"]:
            matched_names = [m["skill"] for m in skill_match["matched"][:3]]
            parts.append(
                f"Demonstrated skills include: {', '.join(matched_names)}."
            )
        
        # Interest alignment
        if interest_score > 0.6 and student_features.interests:
            parts.append(
                f"Your interests in {', '.join(student_features.interests[:2])} align well with this role."
            )
        
        # Experience
        if student_features.project_count > 0:
            parts.append(
                f"You have {student_features.project_count} relevant project(s)."
            )
        
        # Missing skills
        missing_required = [
            m["skill"] for m in skill_match["missing"]
            if m["importance"] == RequirementImportance.REQUIRED
        ]
        if missing_required:
            parts.append(
                f"Key skills to develop: {', '.join(missing_required[:3])}."
            )
        
        return " ".join(parts)
    
    def _identify_strengths(
        self,
        role_data: Dict,
        skill_match: Dict,
        student_features: StudentFeatures
    ) -> List[str]:
        """Identify student's strengths for this role."""
        strengths = []
        
        # Demonstrated skills
        if skill_match["matched"]:
            for match in skill_match["matched"][:5]:
                strengths.append(
                    f"Demonstrated {match['skill']}"
                )
        
        # Projects
        if student_features.project_count >= 2:
            strengths.append(
                f"{student_features.project_count} relevant projects completed"
            )
        
        # Education
        if student_features.education_level:
            strengths.append(
                f"{student_features.education_level} in {student_features.field_of_study or 'relevant field'}"
            )
        
        # Interests
        if student_features.interests:
            strengths.append(
                f"Strong interest in {', '.join(student_features.interests[:2])}"
            )
        
        return strengths
    
    def _identify_gaps(
        self,
        role_data: Dict,
        skill_match: Dict,
        student_features: StudentFeatures
    ) -> List[str]:
        """Identify gaps to address."""
        gaps = []
        
        # Missing required skills
        for missing in skill_match["missing"]:
            if missing["importance"] == RequirementImportance.REQUIRED:
                gaps.append(
                    f"Need to develop {missing['skill']}: {missing['text']}"
                )
        
        # Partial skills
        for partial in skill_match["partial"]:
            gaps.append(
                f"Strengthen {partial['skill']} skills"
            )
        
        # Experience gaps
        if student_features.project_count == 0:
            gaps.append("Build portfolio with practical projects")
        
        if not student_features.has_internship:
            gaps.append("Gain practical experience through internship or job")
        
        return gaps
    
    def _suggest_next_steps(
        self,
        role_data: Dict,
        skill_match: Dict,
        gaps: List[str]
    ) -> List[str]:
        """Suggest actionable next steps."""
        steps = []
        
        # Skill development
        missing_required = [
            m for m in skill_match["missing"]
            if m["importance"] == RequirementImportance.REQUIRED
        ]
        
        if missing_required:
            first_missing = missing_required[0]
            steps.append(
                f"Start learning {first_missing['skill']}"
            )
        
        # Project suggestion
        if "example_projects" in role_data and role_data["example_projects"]:
            steps.append(
                f"Build a project: {role_data['example_projects'][0]}"
            )
        
        # Assessment
        if len(gaps) > 3:
            steps.append(
                "Complete a skill assessment to identify specific areas for improvement"
            )
        
        # Follow-up questions
        if skill_match["score"] < 0.5:
            steps.append(
                "Answer more discovery questions to help us better understand your background"
            )
        
        return steps[:4]  # Limit to 4 actionable steps
