# AI Gateway

Lightweight AI/LLM wrapper with automatic fallbacks for ORVENA Intelligence Engine.

## Overview

The AI Gateway provides optional AI enhancement for intelligence operations while **always** providing reliable rule-based fallbacks. The system works completely offline without AI/ML but can be enhanced with AI when available.

## Key Features

- **Always Works**: Rule-based fallbacks ensure operations never fail
- **Optional AI**: Can work with or without LLM provider
- **Typed Operations**: Strongly typed operation definitions
- **Usage Tracking**: Monitor AI vs fallback usage
- **Zero Dependencies**: No AI libraries required to run
- **Transparent**: Clear indication of whether AI or fallback was used

## Architecture

```
┌─────────────────────────────────────────┐
│         Intelligence Engine             │
│   (Classifier, Matcher, Roadmap, etc.)  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│           AI Gateway                    │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ AI Operation │──│ LLM Provider │    │
│  │   Handler    │  │  (Optional)  │    │
│  └──────┬───────┘  └──────────────┘    │
│         │                               │
│         ▼                               │
│  ┌──────────────┐                      │
│  │   Fallback   │                      │
│  │   Function   │                      │
│  └──────────────┘                      │
└─────────────────────────────────────────┘
```

## Operations

### 1. Resume Enhancement
Enhance or generate professional resume summaries.

```python
from app.modules.career_intelligence.ai_gateway import AIGateway
from app.modules.career_intelligence.ai_gateway.operations import enhance_resume_summary

gateway = AIGateway(enable_ai=False)  # Works offline

response = await enhance_resume_summary(
    gateway=gateway,
    skills=['Python', 'Django', 'PostgreSQL'],
    experience_years=3.5,
    education='BS Computer Science'
)

print(response.content)  # Rule-based summary
print(response.used_ai)  # False
print(response.fallback_used)  # True
```

### 2. Skill Recommendations
Generate personalized learning recommendations.

```python
from app.modules.career_intelligence.ai_gateway.operations import generate_skill_recommendations

response = await generate_skill_recommendations(
    gateway=gateway,
    current_skills=['JavaScript', 'React'],
    target_role='Frontend Engineer',
    missing_skills=['TypeScript', 'Next.js', 'Testing']
)

print(response.content)
# "Focus on developing these required skills: TypeScript, Next.js, Testing..."
```

### 3. Roadmap Personalization
Personalize learning roadmap descriptions.

```python
from app.modules.career_intelligence.ai_gateway.operations import personalize_roadmap_description

response = await personalize_roadmap_description(
    gateway=gateway,
    role_name='Backend Engineer',
    starting_level='intermediate',
    duration_weeks=12,
    student_name='Alex'
)

print(response.content)
# "This personalized 12-week learning roadmap will guide you..."
```

### 4. Interview Questions
Generate role-specific interview questions.

```python
from app.modules.career_intelligence.ai_gateway.operations import generate_interview_questions

response = await generate_interview_questions(
    gateway=gateway,
    role='Data Engineer',
    skills=['Python', 'Spark', 'SQL'],
    count=5
)

print(response.content)
# "1. Describe a challenging Data Engineer project..."
```

## Configuration

### Offline Mode (Default)
```python
# No AI, only fallbacks
gateway = AIGateway(enable_ai=False)
```

### With AI Provider
```python
from app.services.llm import get_llm_provider

llm_provider = get_llm_provider()  # Your LLM provider
gateway = AIGateway(
    llm_provider=llm_provider,
    enable_ai=True,
    fallback_enabled=True  # Still use fallbacks if AI fails
)
```

### AI-Only Mode (Not Recommended)
```python
# Will return empty responses if AI fails
gateway = AIGateway(
    llm_provider=llm_provider,
    enable_ai=True,
    fallback_enabled=False  # ⚠️ Risky
)
```

## Usage Tracking

```python
# Execute operations...
await enhance_resume_summary(gateway, ...)
await generate_skill_recommendations(gateway, ...)

# Get statistics
stats = gateway.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"AI rate: {stats['ai_rate']:.1%}")
print(f"Fallback rate: {stats['fallback_rate']:.1%}")
print(f"Error rate: {stats['error_rate']:.1%}")

# Reset statistics
gateway.reset_stats()
```

## Response Structure

All operations return an `AIResponse` object:

```python
@dataclass
class AIResponse:
    operation: AIOperation          # Type of operation
    content: str                    # Generated content
    used_ai: bool                   # True if AI was used
    fallback_used: bool            # True if fallback was used
    model_used: Optional[str]       # AI model name (if used)
    tokens_used: int               # Token count (if AI used)
    processing_time_ms: int        # Processing time
    error: Optional[str]            # Error message (if failed)
    metadata: Dict[str, Any]        # Additional metadata
    timestamp: datetime             # When generated
```

## Fallback Behavior

Each operation has a rule-based fallback that:
- Never fails (returns sensible defaults)
- Uses structured input data
- Follows proven templates
- Is fast and predictable

Example fallback for resume summary:
```python
def _fallback_resume_summary(
    skills: List[str],
    experience_years: float,
    education: str,
    **kwargs
) -> str:
    # Determine level
    if experience_years >= 5:
        level = "Senior"
    elif experience_years >= 2:
        level = "Experienced"
    else:
        level = "Motivated"
    
    # Build from structured data
    parts = [f"{level} professional"]
    if skills:
        parts.append(f"with expertise in {', '.join(skills[:3])}")
    if education:
        parts.append(f"holding a {education}")
    
    return " ".join(parts) + "."
```

## Adding New Operations

1. **Define operation type**:
```python
class AIOperation(str, Enum):
    YOUR_OPERATION = "your_operation"
```

2. **Create fallback function**:
```python
def _fallback_your_operation(
    param1: str,
    param2: int,
    **kwargs
) -> str:
    # Rule-based logic
    return result
```

3. **Create operation function**:
```python
async def your_operation(
    gateway: AIGateway,
    param1: str,
    param2: int
) -> AIResponse:
    prompt = f"Generate something for {param1} and {param2}"
    
    return await gateway.execute(
        operation=AIOperation.YOUR_OPERATION,
        prompt=prompt,
        fallback_fn=_fallback_your_operation,
        param1=param1,
        param2=param2,
        max_tokens=200
    )
```

4. **Add tests** in `test_ai_gateway.py`

## Testing

```bash
# Run all tests
pytest backend/tests/test_ai_gateway.py -v

# With coverage
pytest backend/tests/test_ai_gateway.py --cov=backend/app/modules/career_intelligence/ai_gateway --cov-report=term-missing

# Test specific operation
pytest backend/tests/test_ai_gateway.py::test_enhance_resume_summary_fallback -v
```

## Integration Example

```python
from app.modules.career_intelligence.ai_gateway import AIGateway
from app.modules.career_intelligence.ai_gateway.operations import (
    enhance_resume_summary,
    generate_skill_recommendations
)

# Initialize once
gateway = AIGateway(enable_ai=False)

# Use in your services
class ResumeService:
    def __init__(self, ai_gateway: AIGateway):
        self.gateway = ai_gateway
    
    async def enhance_profile(self, user_data):
        # AI-enhanced summary with automatic fallback
        summary_response = await enhance_resume_summary(
            gateway=self.gateway,
            skills=user_data.skills,
            experience_years=user_data.experience_years,
            education=user_data.education
        )
        
        # Get skill recommendations
        recs_response = await generate_skill_recommendations(
            gateway=self.gateway,
            current_skills=user_data.skills,
            target_role=user_data.target_role,
            missing_skills=user_data.missing_skills
        )
        
        return {
            'summary': summary_response.content,
            'recommendations': recs_response.content,
            'used_ai': summary_response.used_ai
        }
```

## Design Principles

1. **Offline First**: Always works without AI
2. **Transparent**: Clear about AI vs fallback usage
3. **Predictable**: Fallbacks use structured logic
4. **Lightweight**: Minimal dependencies
5. **Testable**: Easy to test both paths
6. **Typed**: Strong type hints throughout
7. **Tracked**: Monitor usage patterns

## Performance

- **Fallback latency**: < 10ms
- **AI latency**: 500-2000ms (depends on provider)
- **Memory overhead**: < 1MB (without AI provider)
- **No API calls**: When AI disabled

## Security

- No data sent externally when AI disabled
- LLM provider connection controlled by caller
- No API keys stored in gateway
- Input validation in operation functions
- Fallbacks never call external services

## License

Part of ORVENA Intelligence Engine - All Rights Reserved
