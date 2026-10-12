"""
Candidate Matcher

Orchestrates the complete matching pipeline:
1. Parse resume (if needed)
2. Normalize skills
3. Assess readiness for roles
4. Generate transparent match scores
5. Provide hiring recommendations

Works for both students (career guidance) and candidates (job matching).
"""
import logging
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from ..types import (
    StudentFeatures,
    SkillEvidence,
    EvidenceState,
    ProficiencyLevel,
    ConfidenceLevel,
    RequirementImportance
)
from ..taxonomy.roles import CAREER_ROLES
from ..taxonomy.requirements import get_role_requirements, calculate_role_match_score
from ..classification.role_matcher import RoleFitScorer
from ..evidence.skill_assessor import SkillAssessor
from ...resume_intelligence.extraction.structured_parser import (
    StructuredResumeParser,
    ParsedResume
)
from ...resume_intelligence.matching.skill_normalizer import SkillNormalizer
from ...resume_intelligence.matching.role_matcher import ResumeRoleMatcher

logger = logging.getLogger(__name__)


@dataclass
class SkillGap:
    """Represents a skill gap for a role."""
    skill_name: str
    importance: str  # 'required', 'preferred', 'optional'
    current_level: Optional[str] = None  # Current proficiency if any
    target_level: str = 'intermediate'  # Expected level for role
    evidence_state: str = 'not_demonstrated'
    learning_resources: List[str] = field(default_factory=list)


@dataclass
class CandidateMatch:
    """
    Result of matching a candidate to a specific role.
    
    Provides transparent, evidence-based scoring with detailed breakdown.
    """
    
    # Identity
    candidate_id: Optional[UUID] = None
    role_id: str = ''
    role_name: str = ''
    
    # Overall scores
    match_score: float = 0.0  # 0.0 to 1.0
    confidence: str = ConfidenceLevel.UNCERTAIN  # high, medium, low, uncertain
    
    # Detailed breakdown
    skills_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    project_score: float = 0.0
    
    # Skill analysis
    matched_skills: List[str] = field(default_factory=list)
    skill_gaps: List[SkillGap] = field(default_factory=list)
    
    # Evidence quality
    demonstrated_skills_count: int = 0
    declared_skills_count: int = 0
    total_skills_assessed: int = 0
    
    # Experience
    years_of_experience: float = 0.0
    relevant_experience_years: float = 0.0
    has_relevant_internship: bool = False
    
    # Education
    education_level: Optional[str] = None
    relevant_degree: bool = False
    
    # Projects
    project_count: int = 0
    relevant_projects: int = 0
    
    # Recommendations
    hiring_recommendation: str = 'review'  # 'strong_fit', 'good_fit', 'possible_fit', 'review', 'not_recommended'
    recommendation_reasoning: str = ''
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    interview_focus_areas: List[str] = field(default_factory=list)
    
    # Metadata
    assessment_date: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'candidate_id': str(self.candidate_id) if self.candidate_id else None,
            'role_id': self.role_id,
            'role_name': self.role_name,
            'match_score': self.match_score,
            'confidence': self.confidence,
            'breakdown': {
                'skills': self.skills_score,
                'experience': self.experience_score,
                'education': self.education_score,
                'projects': self.project_score
            },
            'skills': {
                'matched': self.matched_skills,
                'gaps': [
                    {
                        'skill': g.skill_name,
                        'importance': g.importance,
                        'current_level': g.current_level,
                        'target_level': g.target_level
                    }
                    for g in self.skill_gaps
                ],
                'demonstrated_count': self.demonstrated_skills_count,
                'declared_count': self.declared_skills_count
            },
            'experience': {
                'total_years': self.years_of_experience,
                'relevant_years': self.relevant_experience_years,
                'has_internship': self.has_relevant_internship
            },
            'education': {
                'level': self.education_level,
                'relevant': self.relevant_degree
            },
            'projects': {
                'total': self.project_count,
                'relevant': self.relevant_projects
            },
            'recommendation': {
                'level': self.hiring_recommendation,
                'reasoning': self.recommendation_reasoning,
                'strengths': self.strengths,
                'concerns': self.concerns,
                'interview_focus': self.interview_focus_areas
            },
            'assessment_date': self.assessment_date.isoformat()
        }


@dataclass
class MatchReport:
    """
    Complete matching report for a candidate across multiple roles.
    """
    candidate_id: Optional[UUID] = None
    candidate_name: Optional[str] = None
    
    # Top matches
    top_matches: List[CandidateMatch] = field(default_factory=list)
    
    # Overall profile
    total_skills: int = 0
    demonstrated_skills: int = 0
    total_experience_years: float = 0.0
    education_level: Optional[str] = None
    
    # Summary
    best_role: Optional[str] = None
    career_stage: str = 'entry_level'  # entry_level, mid_level, senior_level
    key_strengths: List[str] = field(default_factory=list)
    development_areas: List[str] = field(default_factory=list)
    
    # Metadata
    report_date: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'candidate_id': str(self.candidate_id) if self.candidate_id else None,
            'candidate_name': self.candidate_name,
            'top_matches': [m.to_dict() for m in self.top_matches],
            'profile_summary': {
                'total_skills': self.total_skills,
                'demonstrated_skills': self.demonstrated_skills,
                'experience_years': self.total_experience_years,
                'education_level': self.education_level,
                'career_stage': self.career_stage
            },
            'best_role': self.best_role,
            'key_strengths': self.key_strengths,
            'development_areas': self.development_areas,
            'report_date': self.report_date.isoformat()
        }


class CandidateMatcher:
    """
    Orchestrates candidate-role matching with transparent scoring.
    
    Integrates:
    - Resume parsing
    - Skill normalization
    - Evidence assessment
    - Role matching
    - Gap analysis
    - Hiring recommendations
    """
    
    def __init__(self):
        self.resume_parser = StructuredResumeParser()
        self.skill_normalizer = SkillNormalizer()
        self.resume_role_matcher = ResumeRoleMatcher()
        self.role_scorer = RoleFitScorer()
        self.skill_assessor = SkillAssessor()
    
    def match_candidate(
        self,
        candidate_data: Union[ParsedResume, StudentFeatures, str],
        target_role_id: Optional[str] = None,
        top_n: int = 5,
        candidate_id: Optional[UUID] = None
    ) -> Union[CandidateMatch, MatchReport]:
        """
        Match candidate to role(s).
        
        Args:
            candidate_data: ParsedResume, StudentFeatures, or resume text
            target_role_id: Specific role to match (returns CandidateMatch)
                           If None, returns top N matches (returns MatchReport)
            top_n: Number of top matches to return if no target_role
            candidate_id: Optional candidate UUID
            
        Returns:
            CandidateMatch if target_role_id provided, else MatchReport
        """
        # Parse input to StudentFeatures
        features = self._prepare_features(candidate_data)
        
        if target_role_id:
            # Match to specific role
            return self._match_to_role(
                features,
                target_role_id,
                candidate_id
            )
        else:
            # Generate full report with top matches
            return self._generate_match_report(
                features,
                top_n,
                candidate_id
            )
    
    def _prepare_features(
        self,
        candidate_data: Union[ParsedResume, StudentFeatures, str]
    ) -> StudentFeatures:
        """Convert various input types to StudentFeatures."""
        
        if isinstance(candidate_data, StudentFeatures):
            return candidate_data
        
        elif isinstance(candidate_data, ParsedResume):
            # Convert parsed resume to features
            return self.resume_role_matcher._resume_to_features(candidate_data)
        
        elif isinstance(candidate_data, str):
            # Parse resume text first
            parsed_resume = self.resume_parser.parse(candidate_data)
            return self.resume_role_matcher._resume_to_features(parsed_resume)
        
        else:
            raise ValueError(f"Unsupported candidate_data type: {type(candidate_data)}")
    
    def _match_to_role(
        self,
        features: StudentFeatures,
        role_id: str,
        candidate_id: Optional[UUID]
    ) -> CandidateMatch:
        """Generate detailed match for specific role."""
        
        if role_id not in CAREER_ROLES:
            raise ValueError(f"Unknown role: {role_id}")
        
        role_data = CAREER_ROLES[role_id]
        
        # Initialize match
        match = CandidateMatch(
            candidate_id=candidate_id or uuid4(),
            role_id=role_id,
            role_name=role_data['name']
        )
        
        # Get role requirements
        requirements = get_role_requirements(role_id)
        
        # Calculate skill match
        skill_analysis = self._analyze_skills(features, requirements)
        match.skills_score = skill_analysis['score']
        match.matched_skills = skill_analysis['matched']
        match.skill_gaps = skill_analysis['gaps']
        match.demonstrated_skills_count = skill_analysis['demonstrated_count']
        match.declared_skills_count = skill_analysis['declared_count']
        match.total_skills_assessed = len(features.skills)
        
        # Calculate experience score
        exp_analysis = self._analyze_experience(features, role_data)
        match.experience_score = exp_analysis['score']
        match.years_of_experience = features.work_experience_months / 12.0
        match.relevant_experience_years = exp_analysis['relevant_years']
        match.has_relevant_internship = features.has_internship
        
        # Calculate education score
        edu_analysis = self._analyze_education(features, role_data)
        match.education_score = edu_analysis['score']
        match.education_level = features.education_level
        match.relevant_degree = edu_analysis['relevant']
        
        # Calculate project score
        proj_analysis = self._analyze_projects(features, requirements)
        match.project_score = proj_analysis['score']
        match.project_count = features.project_count
        match.relevant_projects = proj_analysis['relevant_count']
        
        # Calculate overall match score (weighted average)
        match.match_score = self._calculate_overall_score(
            match.skills_score,
            match.experience_score,
            match.education_score,
            match.project_score
        )
        
        # Determine confidence
        match.confidence = self._determine_confidence(match)
        
        # Generate recommendation
        self._generate_recommendation(match, features, role_data)
        
        return match
    
    def _analyze_skills(
        self,
        features: StudentFeatures,
        requirements: List  # List of RoleRequirement models
    ) -> Dict[str, Any]:
        """Analyze skill match and gaps."""
        
        # Extract candidate skills
        candidate_skills = {
            s.skill_name: s for s in features.skills
        }
        
        matched_skills = []
        skill_gaps = []
        demonstrated_count = 0
        declared_count = 0
        
        # Separate requirements by importance
        required_skills = [r for r in requirements if r.importance == RequirementImportance.REQUIRED]
        preferred_skills = [r for r in requirements if r.importance == RequirementImportance.PREFERRED]
        
        # Check required skills
        for req in required_skills:
            skill_name = req.skill_name if hasattr(req, 'skill_name') else ''
            
            if skill_name in candidate_skills:
                evidence = candidate_skills[skill_name]
                matched_skills.append(skill_name)
                
                if evidence.evidence_state == EvidenceState.DEMONSTRATED:
                    demonstrated_count += 1
                elif evidence.evidence_state == EvidenceState.DECLARED_UNVERIFIED:
                    declared_count += 1
            else:
                # Skill gap
                skill_gaps.append(SkillGap(
                    skill_name=skill_name,
                    importance='required',
                    target_level=str(req.min_proficiency) if hasattr(req, 'min_proficiency') else 'intermediate'
                ))
        
        # Check preferred skills
        for req in preferred_skills:
            skill_name = req.skill_name if hasattr(req, 'skill_name') else ''
            
            if skill_name in candidate_skills:
                if skill_name not in matched_skills:
                    matched_skills.append(skill_name)
                    evidence = candidate_skills[skill_name]
                    if evidence.evidence_state == EvidenceState.DEMONSTRATED:
                        demonstrated_count += 1
            else:
                skill_gaps.append(SkillGap(
                    skill_name=skill_name,
                    importance='preferred',
                    target_level=str(req.min_proficiency) if hasattr(req, 'min_proficiency') else 'beginner'
                ))
        
        # Calculate score
        total_required = len(required_skills)
        total_preferred = len(preferred_skills)
        
        if total_required == 0:
            score = 0.5  # Default if no requirements defined
        else:
            required_matched = sum(1 for s in matched_skills if any(
                (r.skill_name if hasattr(r, 'skill_name') else '') == s for r in required_skills
            ))
            preferred_matched = sum(1 for s in matched_skills if any(
                (r.skill_name if hasattr(r, 'skill_name') else '') == s for r in preferred_skills
            ))
            
            # Weight: 80% required, 20% preferred
            required_score = required_matched / total_required if total_required > 0 else 1.0
            preferred_score = preferred_matched / total_preferred if total_preferred > 0 else 1.0
            
            score = (required_score * 0.8) + (preferred_score * 0.2)
        
        return {
            'score': score,
            'matched': matched_skills,
            'gaps': skill_gaps,
            'demonstrated_count': demonstrated_count,
            'declared_count': declared_count
        }
    
    def _analyze_experience(
        self,
        features: StudentFeatures,
        role_data: Dict
    ) -> Dict[str, Any]:
        """Analyze experience fit."""
        
        years_exp = features.work_experience_months / 12.0
        
        # Estimate relevant experience (simplified)
        # In production, would analyze job titles, descriptions, etc.
        relevant_ratio = 0.7 if features.has_projects else 0.5
        relevant_years = years_exp * relevant_ratio
        
        # Score based on experience level
        # Entry: 0-2 years, Mid: 2-5 years, Senior: 5+ years
        if years_exp < 1:
            score = 0.3
        elif years_exp < 2:
            score = 0.6
        elif years_exp < 5:
            score = 0.85
        else:
            score = 1.0
        
        # Boost for internships
        if features.has_internship:
            score = min(1.0, score + 0.1)
        
        return {
            'score': score,
            'relevant_years': relevant_years
        }
    
    def _analyze_education(
        self,
        features: StudentFeatures,
        role_data: Dict
    ) -> Dict[str, Any]:
        """Analyze education fit."""
        
        # Map education levels to scores
        education_scores = {
            'doctorate': 1.0,
            'masters_completed': 0.95,
            'masters_in_progress': 0.85,
            'bachelors_completed': 0.8,
            'bachelors_in_progress': 0.7,
            'associates_completed': 0.6,
            'high_school': 0.4,
            None: 0.3
        }
        
        score = education_scores.get(features.education_level, 0.3)
        
        # Check if degree is relevant (simplified - would check field_of_study)
        relevant = features.field_of_study is not None if hasattr(features, 'field_of_study') else False
        
        return {
            'score': score,
            'relevant': relevant
        }
    
    def _analyze_projects(
        self,
        features: StudentFeatures,
        requirements: List  # List of RoleRequirement models
    ) -> Dict[str, Any]:
        """Analyze project portfolio."""
        
        project_count = features.project_count
        
        # Score based on project count
        if project_count == 0:
            score = 0.0
        elif project_count == 1:
            score = 0.4
        elif project_count == 2:
            score = 0.7
        else:
            score = 1.0
        
        # Estimate relevant projects (simplified)
        relevant_count = min(project_count, 3)
        
        return {
            'score': score,
            'relevant_count': relevant_count
        }
    
    def _calculate_overall_score(
        self,
        skills_score: float,
        experience_score: float,
        education_score: float,
        project_score: float
    ) -> float:
        """Calculate weighted overall match score."""
        
        # Weights: Skills 50%, Experience 25%, Education 15%, Projects 10%
        overall = (
            skills_score * 0.50 +
            experience_score * 0.25 +
            education_score * 0.15 +
            project_score * 0.10
        )
        
        return round(overall, 3)
    
    def _determine_confidence(self, match: CandidateMatch) -> str:
        """Determine confidence level in the match."""
        
        # High confidence: Good score + strong evidence
        if match.match_score >= 0.7 and match.demonstrated_skills_count >= 3:
            return ConfidenceLevel.HIGH
        
        # Medium confidence: Decent score OR some evidence
        elif match.match_score >= 0.5 or match.demonstrated_skills_count >= 2:
            return ConfidenceLevel.MEDIUM
        
        # Low confidence: Low score but some potential
        elif match.match_score >= 0.3:
            return ConfidenceLevel.LOW
        
        # Uncertain: Not enough information
        else:
            return ConfidenceLevel.UNCERTAIN
    
    def _generate_recommendation(
        self,
        match: CandidateMatch,
        features: StudentFeatures,
        role_data: Dict
    ) -> None:
        """Generate hiring recommendation and interview focus areas."""
        
        # Determine recommendation level
        if match.match_score >= 0.75 and match.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]:
            match.hiring_recommendation = 'strong_fit'
            match.recommendation_reasoning = f"Excellent match with {match.match_score:.0%} overall score and strong skill evidence."
        
        elif match.match_score >= 0.60:
            match.hiring_recommendation = 'good_fit'
            match.recommendation_reasoning = f"Good match with {match.match_score:.0%} overall score. Some skill gaps can be addressed with training."
        
        elif match.match_score >= 0.45:
            match.hiring_recommendation = 'possible_fit'
            match.recommendation_reasoning = f"Possible match with {match.match_score:.0%} overall score. Requires further assessment."
        
        elif match.match_score >= 0.30:
            match.hiring_recommendation = 'review'
            match.recommendation_reasoning = f"Below target threshold ({match.match_score:.0%}). Review carefully before proceeding."
        
        else:
            match.hiring_recommendation = 'not_recommended'
            match.recommendation_reasoning = f"Significant gaps ({match.match_score:.0%} match). Not recommended for this role."
        
        # Identify strengths
        if match.demonstrated_skills_count > 0:
            match.strengths.append(f"{match.demonstrated_skills_count} demonstrated technical skills")
        
        if match.years_of_experience >= 2:
            match.strengths.append(f"{match.years_of_experience:.1f} years of relevant experience")
        
        if match.project_count >= 2:
            match.strengths.append(f"{match.project_count} project(s) in portfolio")
        
        if match.education_score >= 0.8:
            match.strengths.append(f"Strong educational background ({match.education_level})")
        
        # Identify concerns
        required_gaps = [g for g in match.skill_gaps if g.importance == 'required']
        if required_gaps:
            match.concerns.append(f"Missing {len(required_gaps)} required skill(s): {', '.join(g.skill_name for g in required_gaps[:3])}")
        
        if match.declared_skills_count > match.demonstrated_skills_count:
            match.concerns.append(f"{match.declared_skills_count} skills are self-reported without evidence")
        
        if match.years_of_experience < 1:
            match.concerns.append("Limited professional experience")
        
        # Interview focus areas
        if match.declared_skills_count > 0:
            match.interview_focus_areas.append("Verify self-reported skills through technical assessment")
        
        if required_gaps:
            match.interview_focus_areas.append(f"Assess willingness/ability to learn: {', '.join(g.skill_name for g in required_gaps[:2])}")
        
        if match.project_count > 0:
            match.interview_focus_areas.append("Deep dive into project experience and problem-solving approach")
        
        match.interview_focus_areas.append("Cultural fit and communication skills")
    
    def _generate_match_report(
        self,
        features: StudentFeatures,
        top_n: int,
        candidate_id: Optional[UUID]
    ) -> MatchReport:
        """Generate complete match report across all roles."""
        
        # Match to all roles
        all_matches = []
        for role_id in CAREER_ROLES.keys():
            match = self._match_to_role(features, role_id, candidate_id)
            all_matches.append(match)
        
        # Sort by score
        all_matches.sort(key=lambda m: m.match_score, reverse=True)
        
        # Create report
        report = MatchReport(
            candidate_id=candidate_id or uuid4(),
            top_matches=all_matches[:top_n]
        )
        
        # Profile summary
        report.total_skills = len(features.skills)
        report.demonstrated_skills = sum(
            1 for s in features.skills
            if s.evidence_state == EvidenceState.DEMONSTRATED
        )
        report.total_experience_years = features.work_experience_months / 12.0
        report.education_level = features.education_level
        
        # Best role
        if all_matches:
            report.best_role = all_matches[0].role_name
        
        # Career stage
        if report.total_experience_years < 2:
            report.career_stage = 'entry_level'
        elif report.total_experience_years < 5:
            report.career_stage = 'mid_level'
        else:
            report.career_stage = 'senior_level'
        
        # Key strengths (from top match)
        if all_matches:
            report.key_strengths = all_matches[0].strengths
        
        # Development areas (common gaps across top roles)
        gap_counter = {}
        for match in all_matches[:top_n]:
            for gap in match.skill_gaps:
                if gap.importance == 'required':
                    gap_counter[gap.skill_name] = gap_counter.get(gap.skill_name, 0) + 1
        
        # If no common gaps found (e.g., top matches have no requirements),
        # look at gaps from any roles with requirements
        if not gap_counter and report.career_stage == 'entry_level':
            for match in all_matches:
                if match.skill_gaps:  # Has actual gaps defined
                    for gap in match.skill_gaps[:2]:  # Take top 2 gaps from each role
                        if gap.importance == 'required':
                            gap_counter[gap.skill_name] = gap_counter.get(gap.skill_name, 0) + 1
        
        # Skills missing in multiple roles (or at least 1 if junior)
        common_gaps = [
            skill for skill, count in sorted(gap_counter.items(), key=lambda x: -x[1])
            if count >= 2 or (report.career_stage == 'entry_level' and count >= 1)
        ]
        report.development_areas = common_gaps[:5]
        
        return report
