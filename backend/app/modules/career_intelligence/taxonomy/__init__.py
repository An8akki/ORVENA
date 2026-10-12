"""
Career Taxonomy Module

Maintainable career role definitions, skill taxonomy, and role requirements.
All role data is structured and versioned for consistency.
"""

from .roles import CAREER_ROLES, ROLE_FAMILIES, get_role_by_id, get_roles_by_family
from .skills import CANONICAL_SKILLS, SKILL_SYNONYMS, normalize_skill_name
from .requirements import get_role_requirements, check_requirement_match

__all__ = [
    "CAREER_ROLES",
    "ROLE_FAMILIES",
    "CANONICAL_SKILLS",
    "SKILL_SYNONYMS",
    "get_role_by_id",
    "get_roles_by_family",
    "normalize_skill_name",
    "get_role_requirements",
    "check_requirement_match",
]
