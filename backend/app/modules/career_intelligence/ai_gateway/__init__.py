"""
AI Gateway Module

Lightweight wrapper around LLM services with:
- Typed operations for specific tasks
- Graceful fallback to rule-based systems
- Usage tracking and monitoring
- Rate limiting and caching
"""

from .gateway import AIGateway, AIOperation, AIResponse
from .operations import (
    enhance_resume_summary,
    generate_skill_recommendations,
    personalize_roadmap_description,
    generate_interview_questions
)

__all__ = [
    "AIGateway",
    "AIOperation",
    "AIResponse",
    "enhance_resume_summary",
    "generate_skill_recommendations",
    "personalize_roadmap_description",
    "generate_interview_questions",
]
