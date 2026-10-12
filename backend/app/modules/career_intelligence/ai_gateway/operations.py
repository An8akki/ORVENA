"""
AI Operations

Specific AI-powered operations with rule-based fallbacks.
Each operation has:
- AI prompt template
- Fallback function
- Typed inputs/outputs
"""
from typing import List, Dict, Optional
from .gateway import AIGateway, AIOperation, AIResponse


# ============================================================================
# Resume Enhancement
# ============================================================================

def _fallback_resume_summary(
    skills: List[str],
    experience_years: float,
    education: str,
    **kwargs
) -> str:
    """Rule-based resume summary fallback."""
    
    # Build summary from structured data
    parts = []
    
    # Experience
    if experience_years >= 5:
        level = "Senior"
    elif experience_years >= 2:
        level = "Experienced"
    else:
        level = "Motivated"
    
    parts.append(f"{level} professional")
    
    # Skills
    if skills:
        top_skills = skills[:3]
        parts.append(f"with expertise in {', '.join(top_skills)}")
    
    # Education
    if education:
        parts.append(f"holding a {education}")
    
    # Experience detail
    if experience_years > 0:
        parts.append(f"with {experience_years:.1f} years of industry experience")
    
    summary = " ".join(parts) + "."
    
    return summary


async def enhance_resume_summary(
    gateway: AIGateway,
    skills: List[str],
    experience_years: float,
    education: str,
    current_summary: Optional[str] = None
) -> AIResponse:
    """
    Enhance or generate resume professional summary.
    
    Args:
        gateway: AI Gateway instance
        skills: List of candidate skills
        experience_years: Years of experience
        education: Education level
        current_summary: Existing summary to enhance (optional)
        
    Returns:
        AIResponse with enhanced summary
    """
    
    # Build AI prompt
    prompt = f"""Generate a professional resume summary for a candidate with:
- Skills: {', '.join(skills[:5])}
- Experience: {experience_years} years
- Education: {education}

{f"Current summary: {current_summary}" if current_summary else ""}

Write a compelling 2-3 sentence professional summary that highlights key strengths.
Be specific and achievement-focused. Avoid clichés."""

    return await gateway.execute(
        operation=AIOperation.RESUME_ENHANCEMENT,
        prompt=prompt,
        fallback_fn=_fallback_resume_summary,
        skills=skills,
        experience_years=experience_years,
        education=education,
        max_tokens=150
    )


# ============================================================================
# Skill Recommendations
# ============================================================================

def _fallback_skill_recommendations(
    current_skills: List[str],
    target_role: str,
    missing_skills: List[str],
    **kwargs
) -> str:
    """Rule-based skill recommendation fallback."""
    
    recommendations = []
    
    # Priority: missing required skills
    if missing_skills:
        required = missing_skills[:3]
        recommendations.append(
            f"Focus on developing these required skills: {', '.join(required)}. "
            f"These are essential for the {target_role} role."
        )
    
    # Suggest learning path
    if current_skills:
        recommendations.append(
            f"Leverage your existing skills in {', '.join(current_skills[:2])} "
            f"as a foundation for learning new technologies."
        )
    
    # General advice
    recommendations.append(
        f"Consider building projects that demonstrate these skills in action. "
        f"Hands-on experience is highly valued for {target_role} positions."
    )
    
    return " ".join(recommendations)


async def generate_skill_recommendations(
    gateway: AIGateway,
    current_skills: List[str],
    target_role: str,
    missing_skills: List[str]
) -> AIResponse:
    """
    Generate personalized skill learning recommendations.
    
    Args:
        gateway: AI Gateway instance
        current_skills: Skills the candidate currently has
        target_role: Target career role
        missing_skills: Skills needed for target role
        
    Returns:
        AIResponse with skill recommendations
    """
    
    prompt = f"""Provide learning recommendations for a candidate targeting a {target_role} role.

Current skills: {', '.join(current_skills)}
Skills needed: {', '.join(missing_skills)}

Generate specific, actionable recommendations for:
1. Which skills to prioritize
2. How to leverage existing skills
3. Practical learning strategies

Keep it concise and motivating."""

    return await gateway.execute(
        operation=AIOperation.SKILL_RECOMMENDATION,
        prompt=prompt,
        fallback_fn=_fallback_skill_recommendations,
        current_skills=current_skills,
        target_role=target_role,
        missing_skills=missing_skills,
        max_tokens=300
    )


# ============================================================================
# Roadmap Personalization
# ============================================================================

def _fallback_roadmap_description(
    role_name: str,
    starting_level: str,
    duration_weeks: int,
    **kwargs
) -> str:
    """Rule-based roadmap description fallback."""
    
    level_text = {
        'beginner': 'foundational concepts and gradually build expertise',
        'intermediate': 'intermediate concepts and advance your existing skills',
        'advanced': 'advanced topics and specialist knowledge'
    }
    
    description = (
        f"This personalized {duration_weeks}-week learning roadmap will guide you "
        f"to become a {role_name}. Starting at the {starting_level} level, "
        f"you'll learn {level_text.get(starting_level, 'key concepts')}. "
        f"The roadmap includes hands-on projects, curated resources, and clear milestones "
        f"to track your progress toward your career goals."
    )
    
    return description


async def personalize_roadmap_description(
    gateway: AIGateway,
    role_name: str,
    starting_level: str,
    duration_weeks: int,
    student_name: Optional[str] = None
) -> AIResponse:
    """
    Generate personalized roadmap description.
    
    Args:
        gateway: AI Gateway instance
        role_name: Target role name
        starting_level: Student's starting level
        duration_weeks: Roadmap duration
        student_name: Optional student name for personalization
        
    Returns:
        AIResponse with personalized description
    """
    
    prompt = f"""Write a motivating introduction for a personalized learning roadmap.

Target role: {role_name}
Starting level: {starting_level}
Duration: {duration_weeks} weeks
{f"Student: {student_name}" if student_name else ""}

Create an engaging 2-3 sentence intro that:
- Acknowledges their starting point
- Highlights what they'll achieve
- Motivates them to begin

Be encouraging and specific."""

    return await gateway.execute(
        operation=AIOperation.ROADMAP_PERSONALIZATION,
        prompt=prompt,
        fallback_fn=_fallback_roadmap_description,
        role_name=role_name,
        starting_level=starting_level,
        duration_weeks=duration_weeks,
        max_tokens=150
    )


# ============================================================================
# Interview Questions
# ============================================================================

def _fallback_interview_questions(
    role: str,
    skills: List[str],
    **kwargs
) -> str:
    """Rule-based interview questions fallback."""
    
    questions = [
        f"1. Describe a challenging {role} project you've worked on. What technologies did you use and what was your role?",
        f"2. How do you stay current with developments in {', '.join(skills[:2])}?",
        f"3. Walk me through your approach to problem-solving when facing a complex technical challenge.",
        f"4. Describe a time when you had to learn a new technology quickly. How did you approach it?",
        f"5. What interests you most about working as a {role}?"
    ]
    
    return "\n\n".join(questions)


async def generate_interview_questions(
    gateway: AIGateway,
    role: str,
    skills: List[str],
    count: int = 5
) -> AIResponse:
    """
    Generate interview questions for a role.
    
    Args:
        gateway: AI Gateway instance
        role: Job role
        skills: Key skills to assess
        count: Number of questions to generate
        
    Returns:
        AIResponse with interview questions
    """
    
    prompt = f"""Generate {count} insightful interview questions for a {role} candidate.

Key skills to assess: {', '.join(skills)}

Create questions that:
- Assess both technical skills and problem-solving
- Include behavioral and situational questions
- Are specific to the role and skills
- Help evaluate real-world experience

Format as numbered list."""

    return await gateway.execute(
        operation=AIOperation.INTERVIEW_QUESTIONS,
        prompt=prompt,
        fallback_fn=_fallback_interview_questions,
        role=role,
        skills=skills,
        max_tokens=400
    )
