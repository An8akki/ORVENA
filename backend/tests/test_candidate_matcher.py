"""
Tests for candidate-role matching engine.
"""
import pytest
from uuid import uuid4
from app.modules.career_intelligence.matching.candidate_matcher import (
    CandidateMatcher,
    CandidateMatch,
    MatchReport,
    SkillGap
)
from app.modules.career_intelligence.types import (
    StudentFeatures,
    SkillEvidence,
    EvidenceType,
    EvidenceState,
    ProficiencyLevel
)
from app.modules.resume_intelligence.extraction.structured_parser import ParsedResume


@pytest.fixture
def matcher():
    """Create matcher instance."""
    return CandidateMatcher()


@pytest.fixture
def frontend_candidate_features():
    """Create features for a frontend candidate."""
    return StudentFeatures(
        skills=[
            SkillEvidence(
                skill_name='javascript',
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description='3 years professional experience',
                confidence=0.9
            ),
            SkillEvidence(
                skill_name='react',
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description='Multiple projects',
                confidence=0.85
            ),
            SkillEvidence(
                skill_name='html',
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.ADVANCED,
                source_description='Professional work',
                confidence=0.95
            ),
            SkillEvidence(
                skill_name='css',
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.ADVANCED,
                source_description='Professional work',
                confidence=0.95
            ),
            SkillEvidence(
                skill_name='typescript',
                evidence_type=EvidenceType.DECLARED,
                evidence_state=EvidenceState.DECLARED_UNVERIFIED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description='Self-reported',
                confidence=0.5
            )
        ],
        interests=['frontend', 'web', 'ui'],
        work_experience_months=36,
        has_projects=True,
        project_count=3,
        has_internship=False,
        education_level='bachelors_completed'
    )


@pytest.fixture
def backend_candidate_features():
    """Create features for a backend candidate."""
    return StudentFeatures(
        skills=[
            SkillEvidence(
                skill_name='python',
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.ADVANCED,
                source_description='5 years experience',
                confidence=0.95
            ),
            SkillEvidence(
                skill_name='django',
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description='Multiple projects',
                confidence=0.85
            ),
            SkillEvidence(
                skill_name='postgresql',
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description='Professional work',
                confidence=0.8
            ),
            SkillEvidence(
                skill_name='docker',
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description='Personal projects',
                confidence=0.6
            )
        ],
        interests=['backend', 'api', 'databases'],
        work_experience_months=60,
        has_projects=True,
        project_count=5,
        has_internship=True,
        education_level='bachelors_completed'
    )


@pytest.fixture
def junior_candidate_features():
    """Create features for a junior candidate."""
    return StudentFeatures(
        skills=[
            SkillEvidence(
                skill_name='python',
                evidence_type=EvidenceType.EDUCATION,
                evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description='University coursework',
                confidence=0.6
            ),
            SkillEvidence(
                skill_name='javascript',
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description='School project',
                confidence=0.5
            )
        ],
        interests=['software', 'web'],
        work_experience_months=0,
        has_projects=True,
        project_count=2,
        has_internship=True,
        education_level='bachelors_in_progress'
    )


def test_match_frontend_candidate_to_frontend_role(matcher, frontend_candidate_features):
    """Test matching a strong frontend candidate to frontend role."""
    match = matcher.match_candidate(
        frontend_candidate_features,
        target_role_id='frontend_engineer',
        candidate_id=uuid4()
    )
    
    assert isinstance(match, CandidateMatch)
    assert match.role_id == 'frontend_engineer'
    assert match.match_score > 0.5  # Should be a good match
    
    # Should have matched key frontend skills
    assert 'javascript' in match.matched_skills or 'react' in match.matched_skills
    
    # Should have demonstrated skills
    assert match.demonstrated_skills_count >= 3
    
    # Should have positive recommendation
    assert match.hiring_recommendation in ['strong_fit', 'good_fit', 'possible_fit']


def test_match_backend_candidate_to_backend_role(matcher, backend_candidate_features):
    """Test matching a strong backend candidate to backend role."""
    match = matcher.match_candidate(
        backend_candidate_features,
        target_role_id='backend_engineer',
        candidate_id=uuid4()
    )
    
    assert isinstance(match, CandidateMatch)
    assert match.role_id == 'backend_engineer'
    # Adjusted: candidate has 2/5 required skills but strong experience
    assert match.match_score > 0.5  # Should be a reasonable match
    
    # Should have matched backend skills
    assert 'python' in match.matched_skills
    
    # Should recognize senior experience
    assert match.years_of_experience >= 4.0
    assert match.experience_score >= 0.8


def test_match_junior_candidate_has_gaps(matcher, junior_candidate_features):
    """Test that junior candidate shows appropriate skill gaps."""
    match = matcher.match_candidate(
        junior_candidate_features,
        target_role_id='frontend_engineer'
    )
    
    # Should have skill gaps
    assert len(match.skill_gaps) > 0
    
    # Should have low experience score
    assert match.experience_score < 0.7
    
    # Should note concerns
    assert len(match.concerns) > 0
    
    # Overall score should reflect junior status
    assert match.match_score < 0.6


def test_generate_match_report_multiple_roles(matcher, frontend_candidate_features):
    """Test generating full match report across multiple roles."""
    report = matcher.match_candidate(
        frontend_candidate_features,
        target_role_id=None,  # No specific role
        top_n=5
    )
    
    assert isinstance(report, MatchReport)
    assert len(report.top_matches) <= 5
    
    # Should have ranked matches
    for i in range(len(report.top_matches) - 1):
        assert report.top_matches[i].match_score >= report.top_matches[i + 1].match_score
    
    # Should have profile summary
    assert report.total_skills > 0
    assert report.demonstrated_skills >= 0
    
    # Should identify best role
    assert report.best_role is not None
    
    # Should determine career stage
    assert report.career_stage in ['entry_level', 'mid_level', 'senior_level']


def test_match_with_mismatched_role(matcher, frontend_candidate_features):
    """Test matching frontend candidate to unrelated role."""
    # Match frontend developer to data scientist role
    match = matcher.match_candidate(
        frontend_candidate_features,
        target_role_id='data_scientist'
    )
    
    # Should have lower match score
    assert match.match_score < 0.5
    
    # Should have many skill gaps
    assert len(match.skill_gaps) > 3
    
    # Should have appropriate recommendation
    assert match.hiring_recommendation in ['review', 'not_recommended', 'possible_fit']


def test_confidence_levels(matcher, frontend_candidate_features, junior_candidate_features):
    """Test that confidence levels are assigned appropriately."""
    # Strong candidate should have high/medium confidence
    strong_match = matcher.match_candidate(
        frontend_candidate_features,
        target_role_id='frontend_engineer'
    )
    assert strong_match.confidence in ['high', 'medium']
    
    # Junior candidate should have lower confidence
    weak_match = matcher.match_candidate(
        junior_candidate_features,
        target_role_id='frontend_engineer'
    )
    assert weak_match.confidence in ['low', 'uncertain', 'medium']


def test_interview_focus_areas_generated(matcher, frontend_candidate_features):
    """Test that interview focus areas are generated."""
    match = matcher.match_candidate(
        frontend_candidate_features,
        target_role_id='frontend_engineer'
    )
    
    assert len(match.interview_focus_areas) > 0
    
    # Should include cultural fit
    assert any('cultural' in area.lower() or 'communication' in area.lower() 
               for area in match.interview_focus_areas)


def test_strengths_and_concerns_identified(matcher, backend_candidate_features):
    """Test that strengths and concerns are properly identified."""
    match = matcher.match_candidate(
        backend_candidate_features,
        target_role_id='backend_engineer'
    )
    
    # Should identify strengths
    assert len(match.strengths) > 0
    
    # Strong candidate should have few concerns
    # (but might have some about unverified skills)
    assert len(match.concerns) <= 3


def test_skill_gap_importance_levels(matcher, junior_candidate_features):
    """Test that skill gaps are categorized by importance."""
    match = matcher.match_candidate(
        junior_candidate_features,
        target_role_id='frontend_engineer'
    )
    
    # Check that gaps have importance levels
    for gap in match.skill_gaps:
        assert gap.importance in ['required', 'preferred', 'optional']


def test_match_score_components(matcher, frontend_candidate_features):
    """Test that match score components are calculated."""
    match = matcher.match_candidate(
        frontend_candidate_features,
        target_role_id='frontend_engineer'
    )
    
    # All score components should be between 0 and 1
    assert 0.0 <= match.skills_score <= 1.0
    assert 0.0 <= match.experience_score <= 1.0
    assert 0.0 <= match.education_score <= 1.0
    assert 0.0 <= match.project_score <= 1.0
    
    # Overall score should be in range
    assert 0.0 <= match.match_score <= 1.0


def test_to_dict_serialization(matcher, frontend_candidate_features):
    """Test that match results can be serialized to dict."""
    match = matcher.match_candidate(
        frontend_candidate_features,
        target_role_id='frontend_engineer'
    )
    
    match_dict = match.to_dict()
    
    assert isinstance(match_dict, dict)
    assert 'role_id' in match_dict
    assert 'match_score' in match_dict
    assert 'breakdown' in match_dict
    assert 'skills' in match_dict
    assert 'recommendation' in match_dict


def test_report_to_dict_serialization(matcher, frontend_candidate_features):
    """Test that match report can be serialized to dict."""
    report = matcher.match_candidate(
        frontend_candidate_features,
        target_role_id=None,
        top_n=3
    )
    
    report_dict = report.to_dict()
    
    assert isinstance(report_dict, dict)
    assert 'top_matches' in report_dict
    assert 'profile_summary' in report_dict
    assert 'best_role' in report_dict
    assert len(report_dict['top_matches']) <= 3


def test_match_from_resume_text(matcher):
    """Test matching directly from resume text."""
    resume_text = """
John Developer
john@example.com | 555-1234

EXPERIENCE
Software Engineer at Tech Co | 2020-2023
• Built web applications with React and Node.js
• Worked on API development and database design

SKILLS
JavaScript, React, Node.js, Python, SQL

EDUCATION
BS Computer Science, State University, 2020
"""
    
    # Should be able to match from raw text
    match = matcher.match_candidate(
        resume_text,
        target_role_id='frontend_engineer'
    )
    
    assert isinstance(match, CandidateMatch)
    assert match.match_score > 0.0


def test_match_from_parsed_resume(matcher):
    """Test matching from ParsedResume object."""
    parsed_resume = ParsedResume(
        name="Jane Developer",
        email="jane@example.com",
        skills=['Python', 'Django', 'PostgreSQL'],
        experience=[
            {
                'title': 'Backend Developer',
                'company': 'Startup Inc',
                'start_date': '2021',
                'end_date': 'Present',
                'current': True,
                'description': []
            }
        ],
        education=[
            {
                'degree': 'BS Computer Science',
                'institution': 'University',
                'graduation_year': 2021
            }
        ],
        projects=[],
        certifications=[]
    )
    
    match = matcher.match_candidate(
        parsed_resume,
        target_role_id='backend_engineer'
    )
    
    assert isinstance(match, CandidateMatch)
    assert match.role_id == 'backend_engineer'


def test_development_areas_in_report(matcher, junior_candidate_features):
    """Test that development areas are identified in report."""
    report = matcher.match_candidate(
        junior_candidate_features,
        target_role_id=None,
        top_n=3
    )
    
    # Junior candidate should have development areas
    assert len(report.development_areas) > 0


def test_career_stage_classification(matcher, junior_candidate_features, backend_candidate_features):
    """Test career stage classification in reports."""
    # Junior candidate
    junior_report = matcher.match_candidate(
        junior_candidate_features,
        target_role_id=None
    )
    assert junior_report.career_stage == 'entry_level'
    
    # Senior candidate
    senior_report = matcher.match_candidate(
        backend_candidate_features,
        target_role_id=None
    )
    assert senior_report.career_stage in ['mid_level', 'senior_level']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
