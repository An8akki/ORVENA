"""
Resume Role Matcher

Matches candidates (via their resumes) to target roles based on
structured evidence from resume parsing and skill normalization.
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID, uuid4

from ...career_intelligence.types import (
    StudentFeatures,
    SkillEvidence,
    EvidenceType,
    EvidenceState,
    ProficiencyLevel
)
from ...career_intelligence.classification.role_matcher import RoleFitScorer
from ...career_intelligence.taxonomy.roles import CAREER_ROLES
from .skill_normalizer import SkillNormalizer
from ..extraction.structured_parser import ParsedResume

logger = logging.getLogger(__name__)


class ResumeRoleMatch:
    """Result of matching a resume to a role."""
    
    def __init__(
        self,
        role_id: str,
        role_name: str,
        match_score: float,
        confidence: str,
        reasoning: str
    ):
        self.role_id = role_id
        self.role_name = role_name
        self.match_score = match_score
        self.confidence = confidence
        self.reasoning = reasoning
        
        # Detailed breakdown
        self.matched_skills: List[str] = []
        self.missing_required_skills: List[str] = []
        self.missing_preferred_skills: List[str] = []
        self.relevant_experience_years: float = 0.0
        self.relevant_projects: int = 0
        
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'role_id': self.role_id,
            'role_name': self.role_name,
            'match_score': self.match_score,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'matched_skills': self.matched_skills,
            'missing_required_skills': self.missing_required_skills,
            'missing_preferred_skills': self.missing_preferred_skills,
            'relevant_experience_years': self.relevant_experience_years,
            'relevant_projects': self.relevant_projects
        }


class ResumeRoleMatcher:
    """
    Matches resumes to career roles.
    
    Process:
    1. Convert ParsedResume to StudentFeatures
    2. Use RoleFitScorer to calculate role fit
    3. Add resume-specific context (years of experience, etc.)
    4. Rank roles and provide detailed matches
    """
    
    def __init__(self):
        self.skill_normalizer = SkillNormalizer()
        self.role_scorer = RoleFitScorer()
    
    def match_resume_to_roles(
        self,
        parsed_resume: ParsedResume,
        top_n: int = 5
    ) -> List[ResumeRoleMatch]:
        """
        Match a parsed resume to career roles.
        
        Args:
            parsed_resume: ParsedResume object
            top_n: Number of top matches to return
            
        Returns:
            List of ResumeRoleMatch objects, sorted by score
        """
        # Convert resume to features
        features = self._resume_to_features(parsed_resume)
        
        # Score all roles
        all_matches = []
        
        for role_id, role_data in CAREER_ROLES.items():
            # Calculate base score
            role_fit = self.role_scorer.score_role(role_id, features)
            
            # Create match object
            match = ResumeRoleMatch(
                role_id=role_id,
                role_name=role_data['name'],
                match_score=role_fit['score'],
                confidence=role_fit['confidence'],
                reasoning=role_fit['reasoning']
            )
            
            # Add detailed breakdown
            self._enrich_match_details(match, features, role_data, role_fit)
            
            all_matches.append(match)
        
        # Sort by score
        all_matches.sort(key=lambda m: m.match_score, reverse=True)
        
        return all_matches[:top_n]
    
    def match_resume_to_role(
        self,
        parsed_resume: ParsedResume,
        target_role_id: str
    ) -> Optional[ResumeRoleMatch]:
        """
        Match a resume to a specific role.
        
        Args:
            parsed_resume: ParsedResume object
            target_role_id: Target role identifier
            
        Returns:
            ResumeRoleMatch object or None if role not found
        """
        if target_role_id not in CAREER_ROLES:
            logger.error(f"Role not found: {target_role_id}")
            return None
        
        # Convert resume to features
        features = self._resume_to_features(parsed_resume)
        
        # Score target role
        role_data = CAREER_ROLES[target_role_id]
        role_fit = self.role_scorer.score_role(target_role_id, features)
        
        # Create match object
        match = ResumeRoleMatch(
            role_id=target_role_id,
            role_name=role_data['name'],
            match_score=role_fit['score'],
            confidence=role_fit['confidence'],
            reasoning=role_fit['reasoning']
        )
        
        # Add detailed breakdown
        self._enrich_match_details(match, features, role_data, role_fit)
        
        return match
    
    def _resume_to_features(self, parsed_resume: ParsedResume) -> StudentFeatures:
        """
        Convert ParsedResume to StudentFeatures.
        
        Args:
            parsed_resume: ParsedResume object
            
        Returns:
            StudentFeatures object
        """
        # Normalize skills from resume
        skill_evidence_list = []
        
        if parsed_resume.skills:
            # Skills listed in skills section
            skill_records = self.skill_normalizer.normalize_with_evidence(
                parsed_resume.skills,
                source_type=EvidenceType.DECLARED,
                confidence_threshold=0.7
            )
            
            for record in skill_records:
                skill_evidence_list.append(SkillEvidence(
                    skill_name=record['skill_name'],
                    evidence_type=record['evidence_type'],
                    evidence_state=record['evidence_state'],
                    proficiency_level=ProficiencyLevel.BEGINNER,  # Default
                    source_description=record['source_description'],
                    confidence=record['confidence']
                ))
        
        # Extract skills from experience descriptions
        experience_skills = self._extract_skills_from_experience(parsed_resume.experience)
        for skill_name in experience_skills:
            # Check if already in list
            if not any(s.skill_name == skill_name for s in skill_evidence_list):
                skill_evidence_list.append(SkillEvidence(
                    skill_name=skill_name,
                    evidence_type=EvidenceType.WORK_EXPERIENCE,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.INTERMEDIATE,
                    source_description="Work experience",
                    confidence=0.8
                ))
        
        # Extract skills from projects
        project_skills = self._extract_skills_from_projects(parsed_resume.projects)
        for skill_name in project_skills:
            # Check if already in list
            if not any(s.skill_name == skill_name for s in skill_evidence_list):
                skill_evidence_list.append(SkillEvidence(
                    skill_name=skill_name,
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.BEGINNER,
                    source_description="Project work",
                    confidence=0.7
                ))
        
        # Calculate work experience
        work_experience_months = self._calculate_experience_months(parsed_resume.experience)
        
        # Extract interests from titles and descriptions
        interests = self._infer_interests(parsed_resume)
        
        # Determine education level
        education_level = self._determine_education_level(parsed_resume.education)
        
        # Create StudentFeatures
        features = StudentFeatures(
            skills=skill_evidence_list,
            interests=interests,
            work_experience_months=work_experience_months,
            has_projects=len(parsed_resume.projects) > 0,
            project_count=len(parsed_resume.projects),
            has_internship=self._has_internship(parsed_resume.experience),
            education_level=education_level
        )
        
        return features
    
    def _extract_skills_from_experience(
        self,
        experience_entries: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract skills mentioned in experience descriptions."""
        all_text = []
        
        for exp in experience_entries:
            if exp.get('title'):
                all_text.append(exp['title'])
            if exp.get('description'):
                all_text.extend(exp['description'])
        
        # Combine and extract potential skills
        combined_text = ' '.join(all_text).lower()
        
        # Match against canonical skills (CANONICAL_SKILLS is now a dict)
        found_skills = []
        for skill_name, skill_data in CANONICAL_SKILLS.items():
            # Check if skill name appears
            if skill_name in combined_text:
                found_skills.append(skill_name)
            # Note: synonyms would need to be added to the taxonomy
        
        return found_skills
    
    def _extract_skills_from_projects(
        self,
        project_entries: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract skills from project technologies."""
        all_technologies = []
        
        for project in project_entries:
            if project.get('technologies'):
                all_technologies.extend(project['technologies'])
        
        # Normalize technologies
        if all_technologies:
            skill_matches = self.skill_normalizer.normalize_skills(all_technologies)
            return [
                m.canonical_skill
                for m in skill_matches
                if m.canonical_skill and m.match_confidence >= 0.7
            ]
        
        return []
    
    def _calculate_experience_months(
        self,
        experience_entries: List[Dict[str, Any]]
    ) -> int:
        """Calculate total work experience in months."""
        # This is a simplified calculation
        # In production, would parse actual dates
        
        total_years = 0.0
        
        for exp in experience_entries:
            # Heuristic: assume each entry is ~1-2 years
            if exp.get('current'):
                total_years += 1.5  # Current job, assume 1.5 years average
            else:
                total_years += 1.0  # Past job, assume 1 year average
        
        return int(total_years * 12)
    
    def _infer_interests(self, parsed_resume: ParsedResume) -> List[str]:
        """Infer career interests from resume content."""
        interests = []
        
        # From job titles
        title_keywords = {
            'frontend': ['frontend', 'front-end', 'ui', 'react', 'angular', 'vue'],
            'backend': ['backend', 'back-end', 'api', 'server', 'django', 'flask'],
            'fullstack': ['fullstack', 'full-stack', 'full stack'],
            'data': ['data', 'analyst', 'scientist', 'ml', 'machine learning'],
            'mobile': ['mobile', 'ios', 'android', 'react native'],
            'devops': ['devops', 'sre', 'infrastructure', 'cloud'],
        }
        
        # Check all text
        all_text = []
        for exp in parsed_resume.experience:
            if exp.get('title'):
                all_text.append(exp['title'].lower())
        
        for proj in parsed_resume.projects:
            if proj.get('name'):
                all_text.append(proj['name'].lower())
        
        combined_text = ' '.join(all_text)
        
        for interest, keywords in title_keywords.items():
            if any(kw in combined_text for kw in keywords):
                interests.append(interest)
        
        return interests
    
    def _determine_education_level(
        self,
        education_entries: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Determine highest education level."""
        if not education_entries:
            return None
        
        education_hierarchy = {
            'doctorate': 4,
            'phd': 4,
            'master': 3,
            'm.s.': 3,
            'm.a.': 3,
            'bachelor': 2,
            'b.s.': 2,
            'b.a.': 2,
            'associate': 1,
            'diploma': 1
        }
        
        highest_level = 0
        highest_degree = None
        
        for edu in education_entries:
            degree_text = (edu.get('degree') or '').lower()
            
            for degree_kw, level in education_hierarchy.items():
                if degree_kw in degree_text:
                    if level > highest_level:
                        highest_level = level
                        highest_degree = degree_kw
        
        # Map to our standard levels
        if highest_level >= 4:
            return 'doctorate'
        elif highest_level == 3:
            return 'masters_completed'
        elif highest_level == 2:
            return 'bachelors_completed'
        elif highest_level == 1:
            return 'associates_completed'
        
        return 'high_school'
    
    def _has_internship(self, experience_entries: List[Dict[str, Any]]) -> bool:
        """Check if candidate has internship experience."""
        for exp in experience_entries:
            title = (exp.get('title') or '').lower()
            if 'intern' in title:
                return True
        return False
    
    def _enrich_match_details(
        self,
        match: ResumeRoleMatch,
        features: StudentFeatures,
        role_data: Dict,
        role_fit: Dict
    ) -> None:
        """
        Enrich match object with detailed breakdown.
        
        Args:
            match: ResumeRoleMatch to enrich
            features: StudentFeatures used for matching
            role_data: Role definition data
            role_fit: Role fit result from scorer
        """
        # Extract matched and missing skills from role_fit reasoning
        if 'matched_skills' in role_fit:
            match.matched_skills = role_fit['matched_skills']
        
        if 'missing_skills' in role_fit:
            match.missing_required_skills = role_fit['missing_skills']
        
        # Calculate relevant experience
        match.relevant_experience_years = features.work_experience_months / 12.0
        
        # Count relevant projects
        match.relevant_projects = features.project_count


# Import canonical skills at module level
from ...career_intelligence.taxonomy.skills import CANONICAL_SKILLS
