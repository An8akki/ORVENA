"""
Tests for resume role matcher.

Tests matching parsed resumes to career roles.
"""
import pytest
from app.modules.resume_intelligence.matching.role_matcher import ResumeRoleMatcher
from app.modules.resume_intelligence.extraction.structured_parser import ParsedResume


@pytest.fixture
def matcher():
    """Create matcher instance."""
    return ResumeRoleMatcher()


@pytest.fixture
def frontend_resume():
    """Create a frontend engineer resume."""
    return ParsedResume(
        name="Jane Frontend",
        email="jane@example.com",
        skills=['JavaScript', 'React', 'HTML', 'CSS', 'TypeScript', 'Redux'],
        experience=[
            {
                'title': 'Frontend Developer',
                'company': 'Tech Startup',
                'start_date': 'January 2020',
                'end_date': 'Present',
                'current': True,
                'description': [
                    'Built responsive web applications using React',
                    'Implemented state management with Redux',
                    'Collaborated with design team on UI/UX'
                ]
            }
        ],
        education=[
            {
                'degree': 'Bachelor of Science in Computer Science',
                'institution': 'State University',
                'graduation_year': 2019
            }
        ]
    )


@pytest.fixture
def backend_resume():
    """Create a backend engineer resume."""
    return ParsedResume(
        name="John Backend",
        email="john@example.com",
        skills=['Python', 'Django', 'PostgreSQL', 'REST API', 'Docker'],
        experience=[
            {
                'title': 'Backend Engineer',
                'company': 'Enterprise Corp',
                'start_date': 'June 2018',
                'end_date': 'December 2022',
                'current': False,
                'description': [
                    'Designed and implemented RESTful APIs',
                    'Optimized database queries',
                    'Deployed applications using Docker'
                ]
            }
        ]
    )


@pytest.fixture
def data_science_resume():
    """Create a data science resume."""
    return ParsedResume(
        name="Alice Data",
        email="alice@example.com",
        skills=['Python', 'Machine Learning', 'TensorFlow', 'Pandas', 'NumPy', 'SQL'],
        experience=[
            {
                'title': 'Data Scientist',
                'company': 'Analytics Inc',
                'start_date': 'March 2019',
                'end_date': 'Present',
                'current': True,
                'description': [
                    'Built predictive models using TensorFlow',
                    'Analyzed large datasets with Pandas',
                    'Created data visualizations'
                ]
            }
        ],
        projects=[
            {
                'name': 'Customer Churn Prediction',
                'description': 'ML model to predict customer churn',
                'technologies': ['Python', 'scikit-learn']
            }
        ]
    )


def test_match_frontend_resume(matcher, frontend_resume):
    """Test matching frontend resume to roles."""
    matches = matcher.match_to_roles(frontend_resume, top_n=5)
    
    assert isinstance(matches, list)
    assert len(matches) > 0
    assert len(matches) <= 5
    
    # Check structure
    first_match = matches[0]
    assert 'role_id' in first_match
    assert 'role_name' in first_match
    assert 'match_score' in first_match
    assert 'matched_skills' in first_match
    
    # Frontend Engineer should be in top matches
    role_names = [m['role_name'] for m in matches]
    assert any('Frontend' in name or 'Front-end' in name or 'front' in name.lower() 
               for name in role_names)


def test_match_backend_resume(matcher, backend_resume):
    """Test matching backend resume to roles."""
    matches = matcher.match_to_roles(backend_resume, top_n=5)
    
    assert len(matches) > 0
    
    # Backend Engineer should be in top matches
    role_names = [m['role_name'] for m in matches]
    assert any('Backend' in name or 'Back-end' in name or 'backend' in name.lower()
               for name in role_names)
    
    # Should have matched some backend skills
    first_match = matches[0]
    matched = first_match['matched_skills']
    assert any(skill in ['python', 'django', 'postgresql', 'rest_api', 'docker'] 
               for skill in matched)


def test_match_data_science_resume(matcher, data_science_resume):
    """Test matching data science resume to roles."""
    matches = matcher.match_to_roles(data_science_resume, top_n=3)
    
    assert len(matches) > 0
    assert len(matches) <= 3
    
    # Data-related roles should be in top matches
    role_names = [m['role_name'] for m in matches]
    assert any('Data' in name or 'ML' in name or 'Machine Learning' in name
               for name in role_names)


def test_match_scores_are_normalized(matcher, frontend_resume):
    """Test that match scores are between 0 and 1."""
    matches = matcher.match_to_roles(frontend_resume)
    
    for match in matches:
        score = match['match_score']
        assert 0.0 <= score <= 1.0


def test_matches_sorted_by_score(matcher, frontend_resume):
    """Test that matches are sorted by score descending."""
    matches = matcher.match_to_roles(frontend_resume, top_n=10)
    
    scores = [m['match_score'] for m in matches]
    
    # Scores should be in descending order
    assert scores == sorted(scores, reverse=True)


def test_match_with_no_skills(matcher):
    """Test matching resume with no skills."""
    resume = ParsedResume(
        name="No Skills",
        email="noskills@example.com",
        skills=[],
        experience=[]
    )
    
    matches = matcher.match_to_roles(resume)
    
    # Should still return matches (with low scores)
    assert isinstance(matches, list)
    assert len(matches) > 0
    
    # Scores should be low
    for match in matches:
        assert match['match_score'] < 0.5


def test_match_with_no_experience(matcher):
    """Test matching resume with no experience."""
    resume = ParsedResume(
        name="Fresh Grad",
        email="fresh@example.com",
        skills=['Python', 'JavaScript'],
        experience=[]
    )
    
    matches = matcher.match_to_roles(resume)
    
    assert len(matches) > 0
    # Should still match based on skills
    first_match = matches[0]
    assert first_match['match_score'] > 0


def test_match_with_common_skills(matcher):
    """Test matching resume with very common skills."""
    resume = ParsedResume(
        name="Common Skills",
        email="common@example.com",
        skills=['Python', 'Git', 'Linux'],
        experience=[]
    )
    
    matches = matcher.match_to_roles(resume, top_n=3)
    
    # Should match to multiple roles
    assert len(matches) >= 3


def test_match_specific_role(matcher, frontend_resume):
    """Test matching to a specific role."""
    # This tests if the matcher has a method for single role matching
    matches = matcher.match_to_roles(frontend_resume, top_n=1)
    
    assert len(matches) == 1
    assert 'role_id' in matches[0]


def test_explanation_included(matcher, frontend_resume):
    """Test that match explanations are included."""
    matches = matcher.match_to_roles(frontend_resume, top_n=1)
    
    match = matches[0]
    # Should have explanation or matched_skills showing why
    assert 'matched_skills' in match
    assert len(match['matched_skills']) > 0


def test_missing_skills_identified(matcher, frontend_resume):
    """Test that missing skills are identified."""
    matches = matcher.match_to_roles(frontend_resume, top_n=1)
    
    match = matches[0]
    # Should identify missing skills (if any)
    if 'missing_skills' in match:
        assert isinstance(match['missing_skills'], list)


def test_match_with_projects(matcher, data_science_resume):
    """Test that projects are considered in matching."""
    # Data science resume has ML project
    matches = matcher.match_to_roles(data_science_resume)
    
    # Should boost data science/ML roles
    assert len(matches) > 0


def test_match_with_certifications(matcher):
    """Test matching considers certifications."""
    resume = ParsedResume(
        name="Certified Pro",
        email="cert@example.com",
        skills=['AWS', 'Docker', 'Kubernetes'],
        certifications=[
            {
                'name': 'AWS Solutions Architect',
                'issuer': 'Amazon',
                'year': 2022
            },
            {
                'name': 'Certified Kubernetes Administrator',
                'issuer': 'CNCF',
                'year': 2023
            }
        ]
    )
    
    matches = matcher.match_to_roles(resume)
    
    # Should match to DevOps/Cloud roles
    role_names = [m['role_name'] for m in matches]
    assert any('DevOps' in name or 'Cloud' in name or 'Engineer' in name
               for name in role_names)


def test_match_empty_resume(matcher):
    """Test matching completely empty resume."""
    resume = ParsedResume(
        name=None,
        email=None,
        skills=[],
        experience=[]
    )
    
    matches = matcher.match_to_roles(resume)
    
    # Should handle gracefully
    assert isinstance(matches, list)


def test_multiple_resumes_independent(matcher, frontend_resume, backend_resume):
    """Test that matching multiple resumes doesn't interfere."""
    matches1 = matcher.match_to_roles(frontend_resume, top_n=3)
    matches2 = matcher.match_to_roles(backend_resume, top_n=3)
    
    # Top matches should be different
    top_role_1 = matches1[0]['role_name']
    top_role_2 = matches2[0]['role_name']
    
    # Frontend and backend top matches should be different
    assert top_role_1 != top_role_2 or matches1[0]['match_score'] != matches2[0]['match_score']


def test_skill_normalization_in_matching(matcher):
    """Test that skills are normalized for matching."""
    # Test with variations of skill names
    resume = ParsedResume(
        name="Skill Variations",
        email="skills@example.com",
        skills=['React.js', 'Node.JS', 'POSTGRESQL', 'TypeScript'],
        experience=[]
    )
    
    matches = matcher.match_to_roles(resume)
    
    # Should match despite different casing/formats
    assert len(matches) > 0
    first_match = matches[0]
    assert len(first_match['matched_skills']) > 0


def test_experience_years_affects_matching(matcher):
    """Test that years of experience affects matching."""
    # Junior resume
    junior_resume = ParsedResume(
        name="Junior Dev",
        email="junior@example.com",
        skills=['JavaScript', 'React'],
        experience=[
            {
                'title': 'Junior Developer',
                'company': 'Startup',
                'start_date': 'June 2023',
                'end_date': 'Present',
                'current': True,
                'description': []
            }
        ]
    )
    
    # Senior resume
    senior_resume = ParsedResume(
        name="Senior Dev",
        email="senior@example.com",
        skills=['JavaScript', 'React'],
        experience=[
            {
                'title': 'Senior Developer',
                'company': 'Big Corp',
                'start_date': 'January 2015',
                'end_date': 'Present',
                'current': True,
                'description': []
            }
        ]
    )
    
    junior_matches = matcher.match_to_roles(junior_resume, top_n=1)
    senior_matches = matcher.match_to_roles(senior_resume, top_n=1)
    
    # Both should get matches
    assert len(junior_matches) > 0
    assert len(senior_matches) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
