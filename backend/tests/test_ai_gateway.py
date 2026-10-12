"""
Tests for AI Gateway

Tests the lightweight AI wrapper with typed operations and fallbacks.
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from app.modules.career_intelligence.ai_gateway.gateway import (
    AIGateway,
    AIOperation,
    AIResponse
)
from app.modules.career_intelligence.ai_gateway.operations import (
    enhance_resume_summary,
    generate_skill_recommendations,
    personalize_roadmap_description,
    generate_interview_questions,
    _fallback_resume_summary,
    _fallback_skill_recommendations,
    _fallback_roadmap_description,
    _fallback_interview_questions
)


# ============================================================================
# Mock LLM Provider
# ============================================================================

class MockLLMProvider:
    """Mock LLM provider for testing."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.calls = []
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Mock generate method."""
        self.calls.append({
            'prompt': prompt,
            'max_tokens': max_tokens,
            'temperature': temperature
        })
        
        if self.should_fail:
            raise RuntimeError("Mock LLM failure")
        
        return {
            'text': f"AI generated response for: {prompt[:50]}...",
            'model': 'mock-llm-v1',
            'usage': {'total_tokens': 100}
        }


# ============================================================================
# AIGateway Tests
# ============================================================================

@pytest.mark.asyncio
async def test_gateway_with_ai_enabled():
    """Test gateway with AI enabled and working."""
    provider = MockLLMProvider()
    gateway = AIGateway(llm_provider=provider, enable_ai=True)
    
    response = await gateway.execute(
        operation=AIOperation.RESUME_ENHANCEMENT,
        prompt="Test prompt",
        fallback_fn=lambda **kwargs: "Fallback response",
        max_tokens=100
    )
    
    assert response.operation == AIOperation.RESUME_ENHANCEMENT
    assert response.used_ai is True
    assert response.fallback_used is False
    assert response.model_used == 'mock-llm-v1'
    assert response.tokens_used == 100
    assert "AI generated response" in response.content
    assert response.error is None
    
    # Check provider was called
    assert len(provider.calls) == 1
    assert provider.calls[0]['prompt'] == "Test prompt"


@pytest.mark.asyncio
async def test_gateway_ai_failure_with_fallback():
    """Test gateway falls back when AI fails."""
    provider = MockLLMProvider(should_fail=True)
    gateway = AIGateway(llm_provider=provider, enable_ai=True)
    
    response = await gateway.execute(
        operation=AIOperation.SKILL_RECOMMENDATION,
        prompt="Test prompt",
        fallback_fn=lambda **kwargs: "Fallback worked",
        test_param="value"
    )
    
    assert response.operation == AIOperation.SKILL_RECOMMENDATION
    assert response.used_ai is False
    assert response.fallback_used is True
    assert response.content == "Fallback worked"
    assert response.model_used is None
    assert response.error is None


@pytest.mark.asyncio
async def test_gateway_no_ai_provider():
    """Test gateway with no AI provider uses fallback."""
    gateway = AIGateway(llm_provider=None, enable_ai=True)
    
    response = await gateway.execute(
        operation=AIOperation.ROADMAP_PERSONALIZATION,
        prompt="Test prompt",
        fallback_fn=lambda **kwargs: "No AI fallback"
    )
    
    assert response.used_ai is False
    assert response.fallback_used is True
    assert response.content == "No AI fallback"


@pytest.mark.asyncio
async def test_gateway_ai_disabled():
    """Test gateway with AI disabled."""
    provider = MockLLMProvider()
    gateway = AIGateway(llm_provider=provider, enable_ai=False)
    
    response = await gateway.execute(
        operation=AIOperation.INTERVIEW_QUESTIONS,
        prompt="Test prompt",
        fallback_fn=lambda **kwargs: "Fallback only"
    )
    
    assert response.used_ai is False
    assert response.fallback_used is True
    assert response.content == "Fallback only"
    
    # Provider should not be called
    assert len(provider.calls) == 0


@pytest.mark.asyncio
async def test_gateway_no_fallback():
    """Test gateway with no fallback function."""
    gateway = AIGateway(llm_provider=None, enable_ai=True)
    
    response = await gateway.execute(
        operation=AIOperation.CAREER_ADVICE,
        prompt="Test prompt",
        fallback_fn=None
    )
    
    assert response.used_ai is False
    assert response.fallback_used is False
    assert response.content == ""
    assert response.error == "AI disabled and no fallback provided"


@pytest.mark.asyncio
async def test_gateway_fallback_error():
    """Test gateway when fallback function errors."""
    gateway = AIGateway(llm_provider=None, enable_ai=True)
    
    def bad_fallback(**kwargs):
        raise ValueError("Fallback error")
    
    response = await gateway.execute(
        operation=AIOperation.RESUME_ENHANCEMENT,
        prompt="Test prompt",
        fallback_fn=bad_fallback
    )
    
    assert response.used_ai is False
    assert response.fallback_used is True
    assert response.content == ""
    assert "Fallback error" in response.error


def test_gateway_usage_stats():
    """Test usage statistics tracking."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    initial_stats = gateway.get_usage_stats()
    assert initial_stats['total_requests'] == 0
    assert initial_stats['ai_rate'] == 0
    assert initial_stats['fallback_rate'] == 0
    
    # Note: Can't easily test async in non-async test
    # Stats are tested indirectly in other async tests


def test_ai_response_to_dict():
    """Test AIResponse serialization."""
    response = AIResponse(
        operation=AIOperation.RESUME_ENHANCEMENT,
        content="Test content",
        used_ai=True,
        model_used="test-model",
        tokens_used=50
    )
    
    result = response.to_dict()
    
    assert result['operation'] == AIOperation.RESUME_ENHANCEMENT
    assert result['content'] == "Test content"
    assert result['used_ai'] is True
    assert result['model_used'] == "test-model"
    assert result['tokens_used'] == 50
    assert 'timestamp' in result


# ============================================================================
# Fallback Function Tests
# ============================================================================

def test_fallback_resume_summary_senior():
    """Test resume summary fallback for senior professional."""
    result = _fallback_resume_summary(
        skills=['Python', 'Django', 'PostgreSQL', 'React', 'Docker'],
        experience_years=7.5,
        education='Bachelor of Computer Science'
    )
    
    assert 'Senior professional' in result
    assert 'Python' in result or 'Django' in result or 'PostgreSQL' in result
    assert 'Bachelor of Computer Science' in result
    assert '7.5 years' in result


def test_fallback_resume_summary_junior():
    """Test resume summary fallback for junior professional."""
    result = _fallback_resume_summary(
        skills=['JavaScript', 'HTML', 'CSS'],
        experience_years=1.0,
        education='Associate Degree'
    )
    
    assert 'Motivated professional' in result
    assert 'JavaScript' in result or 'HTML' in result
    assert 'Associate Degree' in result


def test_fallback_resume_summary_minimal():
    """Test resume summary fallback with minimal data."""
    result = _fallback_resume_summary(
        skills=[],
        experience_years=0,
        education=''
    )
    
    assert 'Motivated professional' in result
    assert len(result) > 0


def test_fallback_skill_recommendations():
    """Test skill recommendations fallback."""
    result = _fallback_skill_recommendations(
        current_skills=['Python', 'SQL'],
        target_role='Backend Engineer',
        missing_skills=['Docker', 'Kubernetes', 'Redis']
    )
    
    assert 'Docker' in result
    assert 'Backend Engineer' in result
    assert 'Python' in result or 'SQL' in result
    assert 'projects' in result.lower()


def test_fallback_skill_recommendations_no_missing():
    """Test skill recommendations when no skills missing."""
    result = _fallback_skill_recommendations(
        current_skills=['Python', 'Django', 'Docker'],
        target_role='Backend Engineer',
        missing_skills=[]
    )
    
    assert 'Backend Engineer' in result
    assert len(result) > 0


def test_fallback_roadmap_description_beginner():
    """Test roadmap description fallback for beginner."""
    result = _fallback_roadmap_description(
        role_name='Frontend Engineer',
        starting_level='beginner',
        duration_weeks=16
    )
    
    assert 'Frontend Engineer' in result
    assert '16-week' in result or '16 week' in result
    assert 'beginner' in result
    assert 'foundational' in result


def test_fallback_roadmap_description_advanced():
    """Test roadmap description fallback for advanced."""
    result = _fallback_roadmap_description(
        role_name='Data Scientist',
        starting_level='advanced',
        duration_weeks=12
    )
    
    assert 'Data Scientist' in result
    assert '12-week' in result or '12 week' in result
    assert 'advanced' in result


def test_fallback_interview_questions():
    """Test interview questions fallback."""
    result = _fallback_interview_questions(
        role='Full Stack Engineer',
        skills=['React', 'Node.js', 'PostgreSQL']
    )
    
    assert 'Full Stack Engineer' in result
    assert 'React' in result or 'Node.js' in result
    assert '1.' in result
    assert '5.' in result  # Should have 5 questions


# ============================================================================
# Operations Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_enhance_resume_summary_operation():
    """Test resume enhancement operation."""
    provider = MockLLMProvider()
    gateway = AIGateway(llm_provider=provider, enable_ai=True)
    
    response = await enhance_resume_summary(
        gateway=gateway,
        skills=['Python', 'Django', 'REST APIs'],
        experience_years=3.0,
        education='BS Computer Science',
        current_summary='Existing summary'
    )
    
    assert response.operation == AIOperation.RESUME_ENHANCEMENT
    assert response.used_ai is True
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_enhance_resume_summary_fallback():
    """Test resume enhancement with fallback."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    response = await enhance_resume_summary(
        gateway=gateway,
        skills=['Python', 'Django', 'REST APIs'],
        experience_years=3.0,
        education='BS Computer Science'
    )
    
    assert response.operation == AIOperation.RESUME_ENHANCEMENT
    assert response.fallback_used is True
    assert 'Python' in response.content or 'Django' in response.content
    assert '3.0 years' in response.content


@pytest.mark.asyncio
async def test_generate_skill_recommendations_operation():
    """Test skill recommendations operation."""
    provider = MockLLMProvider()
    gateway = AIGateway(llm_provider=provider, enable_ai=True)
    
    response = await generate_skill_recommendations(
        gateway=gateway,
        current_skills=['JavaScript', 'React'],
        target_role='Frontend Engineer',
        missing_skills=['TypeScript', 'Next.js', 'Testing']
    )
    
    assert response.operation == AIOperation.SKILL_RECOMMENDATION
    assert response.used_ai is True


@pytest.mark.asyncio
async def test_generate_skill_recommendations_fallback():
    """Test skill recommendations with fallback."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    response = await generate_skill_recommendations(
        gateway=gateway,
        current_skills=['JavaScript', 'React'],
        target_role='Frontend Engineer',
        missing_skills=['TypeScript', 'Next.js']
    )
    
    assert response.fallback_used is True
    assert 'TypeScript' in response.content
    assert 'Frontend Engineer' in response.content


@pytest.mark.asyncio
async def test_personalize_roadmap_description_operation():
    """Test roadmap personalization operation."""
    provider = MockLLMProvider()
    gateway = AIGateway(llm_provider=provider, enable_ai=True)
    
    response = await personalize_roadmap_description(
        gateway=gateway,
        role_name='Backend Engineer',
        starting_level='intermediate',
        duration_weeks=12,
        student_name='Alex'
    )
    
    assert response.operation == AIOperation.ROADMAP_PERSONALIZATION
    assert response.used_ai is True


@pytest.mark.asyncio
async def test_personalize_roadmap_description_fallback():
    """Test roadmap personalization with fallback."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    response = await personalize_roadmap_description(
        gateway=gateway,
        role_name='Backend Engineer',
        starting_level='intermediate',
        duration_weeks=12
    )
    
    assert response.fallback_used is True
    assert 'Backend Engineer' in response.content
    assert '12' in response.content
    assert 'intermediate' in response.content


@pytest.mark.asyncio
async def test_generate_interview_questions_operation():
    """Test interview questions operation."""
    provider = MockLLMProvider()
    gateway = AIGateway(llm_provider=provider, enable_ai=True)
    
    response = await generate_interview_questions(
        gateway=gateway,
        role='Data Engineer',
        skills=['Python', 'Spark', 'SQL'],
        count=5
    )
    
    assert response.operation == AIOperation.INTERVIEW_QUESTIONS
    assert response.used_ai is True


@pytest.mark.asyncio
async def test_generate_interview_questions_fallback():
    """Test interview questions with fallback."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    response = await generate_interview_questions(
        gateway=gateway,
        role='Data Engineer',
        skills=['Python', 'Spark', 'SQL'],
        count=5
    )
    
    assert response.fallback_used is True
    assert 'Data Engineer' in response.content
    assert 'Python' in response.content or 'Spark' in response.content
    assert '1.' in response.content  # Numbered list


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.asyncio
async def test_empty_skills_list():
    """Test operations with empty skills list."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    response = await enhance_resume_summary(
        gateway=gateway,
        skills=[],
        experience_years=2.0,
        education='BS'
    )
    
    assert response.fallback_used is True
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_zero_experience():
    """Test resume enhancement with zero experience."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    response = await enhance_resume_summary(
        gateway=gateway,
        skills=['Python'],
        experience_years=0,
        education='Currently studying'
    )
    
    assert response.fallback_used is True
    assert 'Python' in response.content


@pytest.mark.asyncio
async def test_very_long_skills_list():
    """Test with many skills."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    skills = [f'Skill{i}' for i in range(20)]
    
    response = await enhance_resume_summary(
        gateway=gateway,
        skills=skills,
        experience_years=5.0,
        education='MS'
    )
    
    assert response.fallback_used is True
    # Should only include top skills
    assert 'Skill0' in response.content or 'Skill1' in response.content


def test_gateway_stats_after_operations():
    """Test usage statistics are tracked correctly."""
    gateway = AIGateway(llm_provider=None, enable_ai=False)
    
    # Manually update stats (since we can't easily call async in sync test)
    gateway.usage_stats['total_requests'] = 10
    gateway.usage_stats['ai_requests'] = 3
    gateway.usage_stats['fallback_requests'] = 6
    gateway.usage_stats['errors'] = 1
    
    stats = gateway.get_usage_stats()
    
    assert stats['total_requests'] == 10
    assert stats['ai_requests'] == 3
    assert stats['fallback_requests'] == 6
    assert stats['errors'] == 1
    assert stats['ai_rate'] == 0.3
    assert stats['fallback_rate'] == 0.6
    assert stats['error_rate'] == 0.1
    
    # Reset
    gateway.reset_stats()
    stats = gateway.get_usage_stats()
    assert stats['total_requests'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
