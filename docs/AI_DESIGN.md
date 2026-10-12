# ORVENA AI Design Documentation

## AI Strategy

ORVENA uses Large Language Models (LLMs) to enhance career guidance, resume analysis, and interview preparation. Our AI strategy prioritizes:

1. **Transparency**: Clear explanations of AI-generated content
2. **Validation**: All AI outputs are validated against schemas
3. **Fallbacks**: Graceful degradation when AI fails
4. **Accuracy**: Never fabricate facts, citations, or credentials
5. **Privacy**: User data protection in external API calls
6. **Cost Efficiency**: Optimize for free-tier limits
7. **Provider Independence**: Easy switching between AI providers

## AI Provider Architecture

### Provider Abstraction Layer

```python
from abc import ABC, abstractmethod
from typing import Type, Optional
from pydantic import BaseModel

class LLMProvider(ABC):
    """Base interface for all LLM providers"""
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 30
    ) -> BaseModel:
        """Generate structured output validated against schema"""
        pass
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 30
    ) -> str:
        """Generate free-form text response"""
        pass
    
    @abstractmethod
    async def generate_streaming(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AsyncIterator[str]:
        """Stream text generation in chunks"""
        pass
    
    def get_provider_name(self) -> str:
        """Return provider identifier"""
        return self.__class__.__name__
```

### Gemini Provider Implementation

```python
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.model_name = model
    
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: int = 30
    ) -> BaseModel:
        try:
            # Configure generation
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
                response_schema=schema
            )
            
            # Generate with timeout
            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    prompt,
                    generation_config=generation_config
                ),
                timeout=timeout
            )
            
            # Parse and validate
            result_json = response.text
            validated = schema.parse_raw(result_json)
            
            return validated
            
        except asyncio.TimeoutError:
            raise LLMTimeoutError(f"Gemini request timed out after {timeout}s")
        except Exception as e:
            raise LLMProviderError(f"Gemini generation failed: {str(e)}")
```

### Provider Factory

```python
class LLMProviderFactory:
    @staticmethod
    def create(provider: str, **config) -> LLMProvider:
        providers = {
            "gemini": GeminiProvider,
            "openai": OpenAIProvider,  # Future
            "anthropic": AnthropicProvider,  # Future
        }
        
        provider_class = providers.get(provider.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider}")
        
        return provider_class(**config)
```

## AI Use Cases

### 1. Career Discovery - Adaptive Question Generation

**Purpose**: Generate contextual follow-up questions based on student responses.

**Model Requirements**: Fast, conversational, contextual

**Recommended Model**: `gemini-1.5-flash`

**Input Schema:**
```python
class QuestionGenerationInput(BaseModel):
    session_context: Dict[str, Any]
    previous_responses: List[Dict[str, str]]
    current_phase: str
    student_profile: Dict[str, Any]
```

**Output Schema:**
```python
class GeneratedQuestion(BaseModel):
    question_text: str
    question_type: str  # 'open_ended', 'multiple_choice', 'ranking'
    category: str
    follow_up_reasoning: Optional[str]
    options: Optional[List[str]]  # For multiple choice
```

**Prompt Template:**
```python
QUESTION_GENERATION_PROMPT = """
You are a career counselor helping students discover suitable career paths.

STUDENT CONTEXT:
{student_context}

PREVIOUS CONVERSATION:
{conversation_history}

CURRENT PHASE: {phase}

Generate ONE insightful follow-up question that:
1. Builds on previous responses
2. Uncovers genuine preferences and constraints
3. Avoids generic career assessment clichés
4. Is specific and actionable

Return a structured JSON response matching this format:
{schema}
"""
```

**Quality Controls:**
- Prevent repetitive questions
- Ensure questions are relevant to phase
- Avoid yes/no questions for complex topics
- Limit questions per phase

### 2. Career Recommendations with Reasoning

**Purpose**: Generate personalized career recommendations with transparent reasoning.

**Model Requirements**: Analytical, thorough reasoning

**Recommended Model**: `gemini-1.5-pro` (for critical decisions)

**Input Schema:**
```python
class CareerRecommendationInput(BaseModel):
    student_profile: StudentProfile
    skills: List[StudentSkill]
    projects: List[Project]
    discovery_responses: List[DiscoveryResponse]
    career_roles: List[CareerRole]
```

**Output Schema:**
```python
class CareerRecommendation(BaseModel):
    career_role_id: UUID
    fit_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=100, max_length=1000)
    strengths: List[str] = Field(..., min_items=2, max_items=5)
    gaps: List[str] = Field(..., max_items=5)
    opportunities: List[str] = Field(..., max_items=5)
    threats: List[str] = Field(..., max_items=5)
    confidence_level: str  # 'high', 'medium', 'low'
    evidence_quality: str  # 'strong', 'moderate', 'weak'
```

**Prompt Template:**
```python
CAREER_RECOMMENDATION_PROMPT = """
Analyze this student's profile and generate career recommendations.

STUDENT PROFILE:
{student_profile}

DEMONSTRATED SKILLS:
{skills}

PROJECTS & EXPERIENCE:
{projects}

CAREER INTERESTS (from discovery):
{discovery_insights}

AVAILABLE CAREER ROLES:
{career_roles}

For each recommended career:
1. Calculate fit score (0.0-1.0) based on EVIDENCE not assumptions
2. Explain reasoning transparently
3. Identify concrete strengths with evidence
4. Identify specific skill gaps
5. Note realistic opportunities and threats
6. Assess confidence based on evidence quality

IMPORTANT RULES:
- Base recommendations on actual demonstrated skills and projects
- Don't overfit to stated interests without supporting evidence
- Distinguish "interested in" from "capable of"
- Flag when more evidence is needed
- Never fabricate skills or achievements

Return top 3-5 recommendations as JSON:
{schema}
"""
```

### 3. Resume Extraction

**Purpose**: Extract structured data from unstructured resume text.

**Model Requirements**: Accurate extraction, structured output

**Recommended Model**: `gemini-1.5-flash`

**Input Schema:**
```python
class ResumeExtractionInput(BaseModel):
    raw_text: str
    filename: str
    file_type: str
```

**Output Schema:**
```python
class ContactInfo(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    portfolio: Optional[str]

class Education(BaseModel):
    institution: str
    degree: str
    field: str
    start_date: Optional[str]
    end_date: Optional[str]
    gpa: Optional[str]
    achievements: List[str] = []

class Experience(BaseModel):
    company: str
    title: str
    start_date: Optional[str]
    end_date: Optional[str]
    current: bool = False
    description: str
    achievements: List[str] = []

class ResumeExtraction(BaseModel):
    contact_info: ContactInfo
    education: List[Education]
    experience: List[Experience]
    skills: Dict[str, List[str]]
    projects: List[Dict[str, Any]]
    certifications: List[Dict[str, str]]
    achievements: List[str]
    extraction_confidence: str  # 'high', 'medium', 'low'
    extraction_notes: Optional[str]
```

**Prompt Template:**
```python
RESUME_EXTRACTION_PROMPT = """
Extract structured information from this resume text.

RESUME TEXT:
{resume_text}

Extract all available information accurately:
- Contact information
- Education history
- Work experience with achievements
- Technical and soft skills
- Projects with descriptions
- Certifications
- Notable achievements

RULES:
- Extract exactly what's written, don't infer
- Preserve bullet points and achievements
- Use null for missing information
- Flag low confidence extractions
- Note any parsing difficulties

Return as JSON:
{schema}
"""
```

### 4. Resume Review and Feedback

**Purpose**: Analyze resume and provide actionable improvement suggestions.

**Model Requirements**: Critical analysis, specific feedback

**Recommended Model**: `gemini-1.5-pro`

**Input Schema:**
```python
class ResumeReviewInput(BaseModel):
    resume_extraction: ResumeExtraction
    target_role: Optional[str]
    target_job_description: Optional[str]
```

**Output Schema:**
```python
class ResumeFinding(BaseModel):
    category: str  # 'content', 'format', 'grammar', 'keywords', 'achievements'
    severity: str  # 'critical', 'major', 'minor', 'suggestion'
    section: Optional[str]
    current_text: Optional[str]
    suggested_improvement: str
    reasoning: str

class ResumeReview(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=1.0)
    overall_feedback: str
    findings: List[ResumeFinding]
    strengths: List[str]
    priority_improvements: List[str]
```

**Prompt Template:**
```python
RESUME_REVIEW_PROMPT = """
Review this resume and provide specific, actionable feedback.

RESUME CONTENT:
{resume_content}

TARGET ROLE: {target_role}

Analyze for:
1. Content quality and impact
2. Achievement quantification
3. Keyword optimization
4. Clarity and conciseness
5. ATS compatibility
6. Role alignment

For each finding:
- Identify specific issue
- Suggest concrete improvement
- Explain why it matters

IMPORTANT:
- Never suggest fabricating achievements
- Only suggest changes to existing content
- Be specific, not generic
- Prioritize high-impact improvements

Return as JSON:
{schema}
"""
```

### 5. Interview Question Generation

**Purpose**: Generate relevant practice interview questions.

**Model Requirements**: Role-appropriate, varied difficulty

**Recommended Model**: `gemini-1.5-flash`

**Input Schema:**
```python
class QuestionGenerationInput(BaseModel):
    target_role: str
    experience_level: str
    student_skills: List[str]
    company_context: Optional[str]
    question_category: str  # 'technical', 'behavioral', 'situational'
    difficulty: str  # 'easy', 'medium', 'hard'
    count: int
```

**Output Schema:**
```python
class InterviewQuestion(BaseModel):
    question_text: str
    category: str
    difficulty: str
    expected_topics: List[str]
    evaluation_criteria: List[str]
    sample_answer_outline: Optional[str]
```

### 6. Answer Evaluation

**Purpose**: Evaluate interview practice answers and provide feedback.

**Model Requirements**: Constructive feedback, rubric-based

**Recommended Model**: `gemini-1.5-pro`

**Input Schema:**
```python
class AnswerEvaluationInput(BaseModel):
    question: str
    student_answer: str
    evaluation_criteria: List[str]
    role_context: str
```

**Output Schema:**
```python
class AnswerEvaluation(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    feedback: str
    strengths: List[str]
    improvements: List[str]
    missing_topics: List[str]
    sample_answer: str
    follow_up_suggestions: List[str]
```

## Prompt Engineering Best Practices

### 1. Prompt Structure

```
[ROLE DEFINITION]
[CONTEXT]
[TASK DESCRIPTION]
[CONSTRAINTS/RULES]
[OUTPUT FORMAT]
[EXAMPLES - if helpful]
```

### 2. Preventing Hallucinations

**DO:**
- Request citations when making factual claims
- Ask for confidence levels
- Require evidence-based reasoning
- Explicitly forbid fabrication

**DON'T:**
- Ask AI to recall specific external data
- Trust salary/market data without sources
- Assume AI knows current company hiring practices

### 3. Structured Output

Always use JSON schema for structured outputs:

```python
# Define output format explicitly
response_schema = {
    "type": "object",
    "properties": {
        "field": {"type": "string"},
        ...
    },
    "required": ["field"]
}
```

### 4. Context Management

**Minimize Context Size:**
```python
def prepare_student_context(profile: StudentProfile) -> dict:
    """Extract only relevant fields for AI context"""
    return {
        "skills": [s.skill.name for s in profile.skills],
        "experience_years": calculate_experience_years(profile),
        "education_level": profile.education_records[0].degree,
        "recent_projects": [p.title for p in profile.projects[:3]]
    }
```

## Error Handling and Retries

### Retry Strategy

```python
class LLMService:
    async def generate_with_retry(
        self,
        prompt: str,
        schema: Type[BaseModel],
        max_retries: int = 3
    ) -> BaseModel:
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await self.provider.generate_structured(
                    prompt=prompt,
                    schema=schema,
                    timeout=30
                )
            except LLMTimeoutError as e:
                last_error = e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except LLMValidationError as e:
                # Don't retry validation errors
                raise
            except LLMRateLimitError as e:
                retry_after = e.retry_after or (2 ** attempt)
                await asyncio.sleep(retry_after)
                last_error = e
            except LLMProviderError as e:
                if attempt == max_retries - 1:
                    raise
                last_error = e
                await asyncio.sleep(2 ** attempt)
        
        raise LLMProviderError(f"Failed after {max_retries} attempts: {last_error}")
```

### Fallback Mechanisms

```python
async def generate_career_recommendations(
    student_id: UUID
) -> List[CareerRecommendation]:
    try:
        # Attempt AI-generated recommendations
        return await ai_recommendation_service.generate(student_id)
    except LLMProviderError:
        # Fallback to rule-based matching
        logger.warning("AI provider failed, using rule-based fallback")
        return await rule_based_matcher.match_careers(student_id)
```

## Performance Optimization

### 1. Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedLLMService:
    def __init__(self):
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.ttl = timedelta(hours=1)
    
    def cache_key(self, prompt: str, schema: Type[BaseModel]) -> str:
        return hashlib.sha256(
            f"{prompt}{schema.__name__}".encode()
        ).hexdigest()
    
    async def generate_with_cache(
        self,
        prompt: str,
        schema: Type[BaseModel]
    ) -> BaseModel:
        key = self.cache_key(prompt, schema)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return result
        
        result = await self.llm_service.generate(prompt, schema)
        self.cache[key] = (result, datetime.now())
        return result
```

### 2. Batch Processing

```python
async def process_multiple_resumes(
    resume_ids: List[UUID]
) -> List[ResumeReview]:
    # Process concurrently with semaphore to limit parallelism
    semaphore = asyncio.Semaphore(3)
    
    async def process_one(resume_id: UUID):
        async with semaphore:
            return await resume_service.analyze(resume_id)
    
    tasks = [process_one(rid) for rid in resume_ids]
    return await asyncio.gather(*tasks)
```

### 3. Token Usage Tracking

```python
class TokenTracker:
    def __init__(self):
        self.usage_log: List[Dict] = []
    
    def log_usage(
        self,
        user_id: UUID,
        operation: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str
    ):
        self.usage_log.append({
            "user_id": str(user_id),
            "operation": operation,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "model": model,
            "timestamp": datetime.utcnow()
        })
    
    async def get_user_usage(
        self,
        user_id: UUID,
        period: timedelta = timedelta(days=1)
    ) -> Dict[str, int]:
        cutoff = datetime.utcnow() - period
        user_logs = [
            log for log in self.usage_log
            if log["user_id"] == str(user_id) and log["timestamp"] > cutoff
        ]
        
        return {
            "total_tokens": sum(log["total_tokens"] for log in user_logs),
            "operations": len(user_logs)
        }
```

## Cost Management

### Free Tier Limits (Gemini)

- **gemini-1.5-flash**: 15 requests/minute, 1M tokens/day (free tier)
- **gemini-1.5-pro**: 2 requests/minute, 50 requests/day (free tier)

### Budget Controls

```python
class AIBudgetControl:
    def __init__(self, daily_limit_tokens: int = 100000):
        self.daily_limit = daily_limit_tokens
        self.tracker = TokenTracker()
    
    async def check_budget(self, user_id: UUID) -> bool:
        usage = await self.tracker.get_user_usage(
            user_id,
            period=timedelta(days=1)
        )
        return usage["total_tokens"] < self.daily_limit
    
    async def enforce_budget(self, user_id: UUID):
        if not await self.check_budget(user_id):
            raise RateLimitError("Daily AI usage limit exceeded")
```

## Testing AI Components

### Mock Provider for Testing

```python
class MockLLMProvider(LLMProvider):
    def __init__(self):
        self.responses = {}
    
    def set_response(self, prompt_key: str, response: BaseModel):
        self.responses[prompt_key] = response
    
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        **kwargs
    ) -> BaseModel:
        # Return predetermined response for testing
        for key, response in self.responses.items():
            if key in prompt:
                return response
        
        # Return empty valid schema
        return schema()
```

### Test Cases

```python
async def test_career_recommendations():
    # Arrange
    mock_provider = MockLLMProvider()
    mock_response = CareerRecommendation(
        career_role_id=uuid4(),
        fit_score=0.85,
        reasoning="Test reasoning",
        strengths=["Skill 1", "Skill 2"],
        gaps=["Gap 1"],
        opportunities=["Opp 1"],
        threats=["Threat 1"],
        confidence_level="high",
        evidence_quality="strong"
    )
    mock_provider.set_response("career", mock_response)
    
    service = CareerService(llm_provider=mock_provider)
    
    # Act
    result = await service.generate_recommendations(student_id)
    
    # Assert
    assert len(result) > 0
    assert result[0].fit_score == 0.85
```

## Monitoring and Observability

### Logging AI Operations

```python
async def log_ai_operation(
    operation: str,
    user_id: UUID,
    provider: str,
    model: str,
    prompt_length: int,
    response_length: int,
    duration_ms: int,
    success: bool,
    error: Optional[str] = None
):
    await ai_logs.create({
        "operation": operation,
        "user_id": str(user_id),
        "provider": provider,
        "model": model,
        "prompt_length": prompt_length,
        "response_length": response_length,
        "duration_ms": duration_ms,
        "success": success,
        "error": error,
        "timestamp": datetime.utcnow()
    })
```

---

**AI Design Version**: 1.0  
**Last Updated**: 2024  
**Primary Provider**: Gemini API
