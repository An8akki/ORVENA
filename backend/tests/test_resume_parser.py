"""
Tests for structured resume parser.
"""
import pytest
from app.modules.resume_intelligence.extraction.structured_parser import (
    StructuredResumeParser,
    ParsedResume
)


@pytest.fixture
def parser():
    """Create parser instance."""
    return StructuredResumeParser()


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
John Doe
john.doe@example.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe
San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years building scalable web applications.
Passionate about clean code and user experience.

EDUCATION
Bachelor of Science in Computer Science
Stanford University | 2018
GPA: 3.8/4.0

WORK EXPERIENCE

Senior Software Engineer
Tech Company Inc | January 2021 - Present
• Led development of microservices architecture serving 1M+ users
• Implemented CI/CD pipeline reducing deployment time by 50%
• Mentored team of 3 junior developers
• Technologies: Python, Django, PostgreSQL, Docker, AWS

Software Engineer
Startup Corp | June 2018 - December 2020
• Built RESTful APIs for mobile applications
• Optimized database queries improving performance by 40%
• Collaborated with cross-functional teams on product features
• Technologies: Node.js, Express, MongoDB, React

SKILLS
Python, JavaScript, TypeScript, React, Django, Flask, Node.js, PostgreSQL, MongoDB, 
Docker, Kubernetes, AWS, Git, CI/CD, REST APIs, GraphQL, Microservices, Agile

PROJECTS

E-Commerce Platform
Personal project built with React and Node.js
• Implemented shopping cart, payment integration, and order tracking
• Deployed on AWS with automated CI/CD
• Technologies: React, Node.js, Express, PostgreSQL, Stripe

Machine Learning Image Classifier
• Built CNN model for image classification using TensorFlow
• Achieved 95% accuracy on test dataset
• Technologies: Python, TensorFlow, Keras, NumPy

CERTIFICATIONS
AWS Certified Solutions Architect - Amazon Web Services - 2022
Certified Kubernetes Administrator (CKA) - Cloud Native Computing Foundation - 2021
"""


def test_parse_contact_info(parser, sample_resume_text):
    """Test extraction of contact information."""
    result = parser.parse(sample_resume_text)
    
    assert result.name == "John Doe"
    assert result.email == "john.doe@example.com"
    assert result.phone == "(555) 123-4567"
    assert "linkedin.com/in/johndoe" in result.linkedin
    assert "github.com/johndoe" in result.github


def test_parse_education(parser, sample_resume_text):
    """Test parsing of education section."""
    result = parser.parse(sample_resume_text)
    
    assert len(result.education) >= 1
    
    edu = result.education[0]
    assert edu['institution'] is not None
    assert edu['graduation_year'] == 2018
    assert 'computer science' in edu['raw_text'].lower()


def test_parse_experience(parser, sample_resume_text):
    """Test parsing of work experience."""
    result = parser.parse(sample_resume_text)
    
    assert len(result.experience) >= 2
    
    # Check first experience entry
    exp = result.experience[0]
    assert exp['title'] is not None
    assert exp['company'] is not None
    assert len(exp['description']) > 0
    
    # Check for current position
    current_positions = [e for e in result.experience if e.get('current')]
    assert len(current_positions) >= 1


def test_parse_skills(parser, sample_resume_text):
    """Test parsing of skills section."""
    result = parser.parse(sample_resume_text)
    
    assert len(result.skills) > 0
    
    # Check that common skills are extracted
    skills_lower = [s.lower() for s in result.skills]
    assert any('python' in s for s in skills_lower)
    assert any('javascript' in s for s in skills_lower)
    assert any('react' in s for s in skills_lower)


def test_parse_projects(parser, sample_resume_text):
    """Test parsing of projects section."""
    result = parser.parse(sample_resume_text)
    
    assert len(result.projects) >= 2
    
    # Check first project
    proj = result.projects[0]
    assert proj['name'] is not None
    assert proj['description'] is not None or len(proj['technologies']) > 0


def test_parse_certifications(parser, sample_resume_text):
    """Test parsing of certifications section."""
    result = parser.parse(sample_resume_text)
    
    assert len(result.certifications) >= 2
    
    # Check first certification
    cert = result.certifications[0]
    assert cert['name'] is not None
    assert cert['year'] is not None or cert['issuer'] is not None


def test_sections_found(parser, sample_resume_text):
    """Test that major sections are identified."""
    result = parser.parse(sample_resume_text)
    
    assert 'education' in result.sections_found
    assert 'experience' in result.sections_found
    assert 'skills' in result.sections_found
    assert 'projects' in result.sections_found
    assert 'certifications' in result.sections_found


def test_parse_confidence(parser, sample_resume_text):
    """Test that parse confidence is calculated."""
    result = parser.parse(sample_resume_text)
    
    assert result.parse_confidence > 0.0
    assert result.parse_confidence <= 1.0
    
    # Good resume should have high confidence
    assert result.parse_confidence >= 0.7


def test_minimal_resume():
    """Test parsing of minimal resume."""
    minimal_text = """
Jane Smith
jane@email.com

EDUCATION
BS Computer Science, MIT, 2020

EXPERIENCE
Software Engineer, Company XYZ, 2020-2022

SKILLS
Python, Java
"""
    
    parser = StructuredResumeParser()
    result = parser.parse(minimal_text)
    
    assert result.email == "jane@email.com"
    assert len(result.education) >= 1
    assert len(result.experience) >= 1
    assert len(result.skills) >= 2


def test_empty_resume():
    """Test parsing of empty/invalid resume."""
    parser = StructuredResumeParser()
    result = parser.parse("")
    
    # Should not crash, but should have low confidence
    assert result.parse_confidence == 0.0
    assert len(result.sections_found) == 0


def test_resume_without_sections():
    """Test parsing resume without clear section headers."""
    text_without_sections = """
John Developer
john@dev.com | 555-0000

Worked at Tech Corp as Engineer from 2020 to 2022.
Built web applications using React and Node.js.
Have degree from State University.
"""
    
    parser = StructuredResumeParser()
    result = parser.parse(text_without_sections)
    
    # Should still extract contact info
    assert result.email == "john@dev.com"
    assert result.phone == "555-0000"
    
    # Confidence should be lower
    assert result.parse_confidence < 0.5


def test_contact_info_variations():
    """Test parsing various contact info formats."""
    text = """
Alice Johnson
alice.johnson+test@company.co.uk
+1-555-123-4567
linkedin.com/pub/alicejohnson
https://github.com/alice-dev
New York, NY
"""
    
    parser = StructuredResumeParser()
    result = parser.parse(text)
    
    assert result.email == "alice.johnson+test@company.co.uk"
    assert result.phone is not None
    assert result.linkedin is not None or result.github is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
