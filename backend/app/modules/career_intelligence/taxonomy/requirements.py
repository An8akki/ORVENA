"""
Role Requirements Module

Define and evaluate requirements for each career role,
including skill requirements, education, and experience.
"""
from typing import Dict, List, Optional
from ..types import (
    RoleRequirement, RequirementImportance, ProficiencyLevel,
    SkillEvidence, EvidenceState
)


# Role Requirements - Maps role keys to their detailed requirements
ROLE_REQUIREMENTS: Dict[str, List[Dict]] = {
    "frontend_engineer": [
        # Required Skills
        {
            "skill": "javascript",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Strong JavaScript fundamentals"
        },
        {
            "skill": "html",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "HTML and semantic markup"
        },
        {
            "skill": "css",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "CSS and responsive design"
        },
        {
            "skill": "react",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Experience with React or similar framework"
        },
        # Preferred Skills
        {
            "skill": "typescript",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "TypeScript knowledge"
        },
        {
            "skill": "git",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Version control with Git"
        },
    ],
    
    "backend_engineer": [
        {
            "skill": "python",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Backend language (Python, Java, or Node.js)"
        },
        {
            "skill": "rest_api",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "RESTful API design and development"
        },
        {
            "skill": "sql",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "SQL and database design"
        },
        {
            "skill": "postgresql",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Relational database experience"
        },
        {
            "skill": "git",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Version control"
        },
    ],
    
    "data_scientist": [
        {
            "skill": "python",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Python for data science"
        },
        {
            "skill": "machine_learning",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Machine learning fundamentals"
        },
        {
            "skill": "pandas",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Data manipulation with Pandas"
        },
        {
            "skill": "scikit_learn",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "ML libraries (scikit-learn, etc.)"
        },
        {
            "skill": "statistics",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Statistics and probability"
        },
    ],
    
    "machine_learning_engineer": [
        {
            "skill": "python",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.ADVANCED,
            "requirement_text": "Advanced Python programming"
        },
        {
            "skill": "machine_learning",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Machine learning algorithms"
        },
        {
            "skill": "tensorflow",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Deep learning frameworks (TensorFlow/PyTorch)"
        },
        {
            "skill": "docker",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Containerization and deployment"
        },
    ],
    
    "devops_engineer": [
        {
            "skill": "linux",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Linux system administration"
        },
        {
            "skill": "docker",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Docker containerization"
        },
        {
            "skill": "kubernetes",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Container orchestration"
        },
        {
            "skill": "cicd",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "CI/CD pipeline setup"
        },
        {
            "skill": "aws",
            "importance": RequirementImportance.PREFERRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Cloud platform experience"
        },
    ],
    
    "ui_ux_designer": [
        {
            "skill": "ui_design",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "UI design principles"
        },
        {
            "skill": "ux_design",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "UX research and design"
        },
        {
            "skill": "figma",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.INTERMEDIATE,
            "requirement_text": "Design tools (Figma/Sketch)"
        },
        {
            "skill": "prototyping",
            "importance": RequirementImportance.REQUIRED,
            "min_proficiency": ProficiencyLevel.BEGINNER,
            "requirement_text": "Prototyping and user testing"
        },
    ],
}


def get_role_requirements(role_key: str) -> List[RoleRequirement]:
    """
    Get structured requirements for a role.
    
    Args:
        role_key: The role identifier (e.g., "frontend_engineer")
        
    Returns:
        List of RoleRequirement objects
    """
    reqs = ROLE_REQUIREMENTS.get(role_key, [])
    
    return [
        RoleRequirement(
            requirement_type="skill",
            requirement_text=req["requirement_text"],
            importance=req["importance"],
            min_proficiency=req.get("min_proficiency"),
            skill_name=req.get("skill")
        )
        for req in reqs
    ]


def check_requirement_match(
    requirement: RoleRequirement,
    student_skills: List[SkillEvidence]
) -> Dict:
    """
    Check if a student meets a specific requirement.
    
    Args:
        requirement: The requirement to check
        student_skills: List of student's skill evidence
        
    Returns:
        Dict with match status and explanation
    """
    # Find matching skill in student's profile
    skill_name = requirement.skill_name
    matching_skills = [
        skill for skill in student_skills
        if skill.skill_name == skill_name
    ]
    
    if not matching_skills:
        return {
            "matched": False,
            "state": "missing",
            "explanation": f"No evidence found for {requirement.requirement_text}"
        }
    
    # Get the best evidence for this skill
    skill_evidence = max(
        matching_skills,
        key=lambda s: _evidence_strength(s.evidence_state)
    )
    
    # Check if evidence state is sufficient
    if skill_evidence.evidence_state == EvidenceState.DEMONSTRATED:
        # Check proficiency level if required
        if requirement.min_proficiency and skill_evidence.proficiency_level:
            if _proficiency_order(skill_evidence.proficiency_level) >= _proficiency_order(requirement.min_proficiency):
                return {
                    "matched": True,
                    "state": "demonstrated",
                    "explanation": f"Demonstrated {requirement.requirement_text}",
                    "evidence": skill_evidence.source_description
                }
            else:
                return {
                    "matched": False,
                    "state": "insufficient_proficiency",
                    "explanation": f"Proficiency below required level for {requirement.requirement_text}",
                    "current_level": skill_evidence.proficiency_level,
                    "required_level": requirement.min_proficiency
                }
        else:
            return {
                "matched": True,
                "state": "demonstrated",
                "explanation": f"Demonstrated {requirement.requirement_text}",
                "evidence": skill_evidence.source_description
            }
    
    elif skill_evidence.evidence_state == EvidenceState.PARTIALLY_DEMONSTRATED:
        return {
            "matched": requirement.importance != RequirementImportance.REQUIRED,
            "state": "partial",
            "explanation": f"Partially demonstrated {requirement.requirement_text}",
            "evidence": skill_evidence.source_description
        }
    
    elif skill_evidence.evidence_state == EvidenceState.DECLARED_UNVERIFIED:
        return {
            "matched": False,
            "state": "unverified",
            "explanation": f"Claimed but not verified: {requirement.requirement_text}"
        }
    
    else:
        return {
            "matched": False,
            "state": "not_assessed",
            "explanation": f"Not yet assessed: {requirement.requirement_text}"
        }


def _evidence_strength(state: EvidenceState) -> int:
    """Return numeric strength of evidence state for comparison."""
    strength_map = {
        EvidenceState.DEMONSTRATED: 4,
        EvidenceState.PARTIALLY_DEMONSTRATED: 3,
        EvidenceState.DECLARED_UNVERIFIED: 2,
        EvidenceState.NOT_ASSESSED: 1,
        EvidenceState.NOT_DEMONSTRATED: 0
    }
    return strength_map.get(state, 0)


def _proficiency_order(level: ProficiencyLevel) -> int:
    """Return numeric order of proficiency level."""
    order_map = {
        ProficiencyLevel.BEGINNER: 1,
        ProficiencyLevel.INTERMEDIATE: 2,
        ProficiencyLevel.ADVANCED: 3,
        ProficiencyLevel.EXPERT: 4
    }
    return order_map.get(level, 0)


def calculate_role_match_score(
    role_key: str,
    student_skills: List[SkillEvidence]
) -> Dict:
    """
    Calculate how well a student matches a role's requirements.
    
    Args:
        role_key: The role identifier
        student_skills: List of student's skill evidence
        
    Returns:
        Dict with score, matched/missing requirements, and explanation
    """
    requirements = get_role_requirements(role_key)
    
    if not requirements:
        return {
            "score": 0.0,
            "matched": [],
            "partial": [],
            "missing": [],
            "explanation": "No requirements defined for this role"
        }
    
    matched = []
    partial = []
    missing = []
    
    required_count = 0
    required_matched = 0
    
    for req in requirements:
        match_result = check_requirement_match(req, student_skills)
        
        # Track required vs optional
        is_required = req.importance == RequirementImportance.REQUIRED
        if is_required:
            required_count += 1
        
        if match_result["matched"]:
            if match_result["state"] == "demonstrated":
                matched.append({
                    "skill": req.skill_name,
                    "text": req.requirement_text,
                    "evidence": match_result.get("evidence")
                })
                if is_required:
                    required_matched += 1
            elif match_result["state"] == "partial":
                partial.append({
                    "skill": req.skill_name,
                    "text": req.requirement_text,
                    "evidence": match_result.get("evidence")
                })
        else:
            missing.append({
                "skill": req.skill_name,
                "text": req.requirement_text,
                "importance": req.importance,
                "state": match_result["state"]
            })
    
    # Calculate score
    # Required skills: 70% weight
    # Preferred skills: 30% weight
    required_score = (required_matched / required_count) if required_count > 0 else 1.0
    
    preferred_count = len(requirements) - required_count
    preferred_matched = len(matched) - required_matched
    preferred_score = (preferred_matched / preferred_count) if preferred_count > 0 else 0.0
    
    overall_score = (required_score * 0.7) + (preferred_score * 0.3)
    
    return {
        "score": overall_score,
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "required_matched": required_matched,
        "required_total": required_count,
        "explanation": _generate_match_explanation(
            required_matched, required_count, len(matched), len(requirements)
        )
    }


def _generate_match_explanation(
    required_matched: int,
    required_total: int,
    total_matched: int,
    total_requirements: int
) -> str:
    """Generate human-readable explanation of match."""
    if required_matched == required_total:
        return f"Meets all {required_total} required skills. Matched {total_matched}/{total_requirements} total requirements."
    elif required_matched > 0:
        missing = required_total - required_matched
        return f"Meets {required_matched}/{required_total} required skills. {missing} required skill(s) missing."
    else:
        return f"Does not meet required skills for this role. {required_total} required skills needed."
