"""
Resume Intelligence Module

Structured resume parsing, skill extraction, normalization,
candidate-role matching, and job-description comparison.
"""

from .extraction.text_extractor import ResumeTextExtractor
from .extraction.structured_parser import StructuredResumeParser
from .matching.skill_normalizer import SkillNormalizer
from .matching.role_matcher import ResumeRoleMatcher

__all__ = [
    "ResumeTextExtractor",
    "StructuredResumeParser",
    "SkillNormalizer",
    "ResumeRoleMatcher",
]
