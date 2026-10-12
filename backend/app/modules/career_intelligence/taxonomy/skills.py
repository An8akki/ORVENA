"""
Canonical Skill Taxonomy

Structured catalog of skills with categories, synonyms, and normalization.
This enables consistent skill matching across resumes, projects, and requirements.
"""
from typing import Dict, List, Optional, Set
from enum import Enum


class SkillCategory(str, Enum):
    """Skill categories for organization."""
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD_PLATFORM = "cloud_platform"
    DEVOPS_TOOL = "devops_tool"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    WEB_DEVELOPMENT = "web_development"
    MOBILE_DEVELOPMENT = "mobile_development"
    SECURITY = "security"
    DESIGN = "design"
    SOFT_SKILL = "soft_skill"
    DOMAIN_KNOWLEDGE = "domain_knowledge"


# Canonical Skills Dictionary
# Format: canonical_name -> {category, display_name, description, level_required}
CANONICAL_SKILLS: Dict[str, Dict[str, any]] = {
    # Programming Languages
    "python": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "Python",
        "description": "Python programming language",
        "related_skills": ["django", "flask", "fastapi", "pandas", "numpy"]
    },
    "javascript": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "JavaScript",
        "description": "JavaScript programming language",
        "related_skills": ["nodejs", "react", "vue", "angular", "typescript"]
    },
    "typescript": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "TypeScript",
        "description": "TypeScript programming language",
        "related_skills": ["javascript", "nodejs", "react", "angular"]
    },
    "java": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "Java",
        "description": "Java programming language",
        "related_skills": ["spring", "hibernate", "maven", "gradle"]
    },
    "csharp": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "C#",
        "description": "C# programming language",
        "related_skills": ["dotnet", "aspnet", "unity"]
    },
    "cpp": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "C++",
        "description": "C++ programming language",
        "related_skills": ["c", "embedded_systems"]
    },
    "go": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "Go",
        "description": "Go programming language",
        "related_skills": ["kubernetes", "docker", "microservices"]
    },
    "rust": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "Rust",
        "description": "Rust programming language",
        "related_skills": ["systems_programming", "webassembly"]
    },
    "sql": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "SQL",
        "description": "SQL query language",
        "related_skills": ["postgresql", "mysql", "database_design"]
    },
    "html": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "HTML",
        "description": "HTML markup language",
        "related_skills": ["css", "javascript", "web_development"]
    },
    "css": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "CSS",
        "description": "CSS styling language",
        "related_skills": ["html", "sass", "tailwind"]
    },
    "r": {
        "category": SkillCategory.PROGRAMMING_LANGUAGE,
        "display_name": "R",
        "description": "R programming language for statistics",
        "related_skills": ["statistics", "data_analysis", "ggplot"]
    },
    
    # Web Development Frameworks
    "react": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "React",
        "description": "React JavaScript library",
        "related_skills": ["javascript", "typescript", "redux", "nextjs"]
    },
    "nextjs": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "Next.js",
        "description": "Next.js React framework",
        "related_skills": ["react", "typescript", "nodejs"]
    },
    "vue": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "Vue.js",
        "description": "Vue.js JavaScript framework",
        "related_skills": ["javascript", "typescript", "nuxt"]
    },
    "angular": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "Angular",
        "description": "Angular TypeScript framework",
        "related_skills": ["typescript", "rxjs"]
    },
    "nodejs": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "Node.js",
        "description": "Node.js JavaScript runtime",
        "related_skills": ["javascript", "express", "nestjs"]
    },
    "express": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "Express.js",
        "description": "Express.js Node.js framework",
        "related_skills": ["nodejs", "rest_api"]
    },
    "django": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "Django",
        "description": "Django Python web framework",
        "related_skills": ["python", "rest_api", "orm"]
    },
    "flask": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "Flask",
        "description": "Flask Python microframework",
        "related_skills": ["python", "rest_api"]
    },
    "fastapi": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "FastAPI",
        "description": "FastAPI Python framework",
        "related_skills": ["python", "rest_api", "async"]
    },
    "spring": {
        "category": SkillCategory.FRAMEWORK,
        "display_name": "Spring Boot",
        "description": "Spring Boot Java framework",
        "related_skills": ["java", "rest_api", "microservices"]
    },
    
    # Databases
    "postgresql": {
        "category": SkillCategory.DATABASE,
        "display_name": "PostgreSQL",
        "description": "PostgreSQL relational database",
        "related_skills": ["sql", "database_design"]
    },
    "mysql": {
        "category": SkillCategory.DATABASE,
        "display_name": "MySQL",
        "description": "MySQL relational database",
        "related_skills": ["sql", "database_design"]
    },
    "mongodb": {
        "category": SkillCategory.DATABASE,
        "display_name": "MongoDB",
        "description": "MongoDB NoSQL database",
        "related_skills": ["nosql", "json"]
    },
    "redis": {
        "category": SkillCategory.DATABASE,
        "display_name": "Redis",
        "description": "Redis in-memory database",
        "related_skills": ["caching", "nosql"]
    },
    "elasticsearch": {
        "category": SkillCategory.DATABASE,
        "display_name": "Elasticsearch",
        "description": "Elasticsearch search engine",
        "related_skills": ["search", "nosql"]
    },
    
    # Cloud Platforms
    "aws": {
        "category": SkillCategory.CLOUD_PLATFORM,
        "display_name": "AWS",
        "description": "Amazon Web Services",
        "related_skills": ["cloud", "ec2", "s3", "lambda"]
    },
    "azure": {
        "category": SkillCategory.CLOUD_PLATFORM,
        "display_name": "Azure",
        "description": "Microsoft Azure",
        "related_skills": ["cloud", "devops"]
    },
    "gcp": {
        "category": SkillCategory.CLOUD_PLATFORM,
        "display_name": "Google Cloud Platform",
        "description": "Google Cloud Platform",
        "related_skills": ["cloud", "kubernetes"]
    },
    
    # DevOps & Tools
    "docker": {
        "category": SkillCategory.DEVOPS_TOOL,
        "display_name": "Docker",
        "description": "Docker containerization",
        "related_skills": ["kubernetes", "devops", "containers"]
    },
    "kubernetes": {
        "category": SkillCategory.DEVOPS_TOOL,
        "display_name": "Kubernetes",
        "description": "Kubernetes container orchestration",
        "related_skills": ["docker", "devops", "cloud"]
    },
    "git": {
        "category": SkillCategory.DEVOPS_TOOL,
        "display_name": "Git",
        "description": "Git version control",
        "related_skills": ["github", "gitlab", "version_control"]
    },
    "cicd": {
        "category": SkillCategory.DEVOPS_TOOL,
        "display_name": "CI/CD",
        "description": "Continuous Integration/Deployment",
        "related_skills": ["jenkins", "github_actions", "gitlab_ci"]
    },
    "terraform": {
        "category": SkillCategory.DEVOPS_TOOL,
        "display_name": "Terraform",
        "description": "Terraform infrastructure as code",
        "related_skills": ["cloud", "devops", "iac"]
    },
    
    # Data Science & ML
    "pandas": {
        "category": SkillCategory.DATA_SCIENCE,
        "display_name": "Pandas",
        "description": "Pandas data manipulation library",
        "related_skills": ["python", "data_analysis", "numpy"]
    },
    "numpy": {
        "category": SkillCategory.DATA_SCIENCE,
        "display_name": "NumPy",
        "description": "NumPy numerical computing",
        "related_skills": ["python", "data_analysis"]
    },
    "scikit_learn": {
        "category": SkillCategory.MACHINE_LEARNING,
        "display_name": "Scikit-learn",
        "description": "Scikit-learn machine learning library",
        "related_skills": ["python", "machine_learning", "data_science"]
    },
    "tensorflow": {
        "category": SkillCategory.MACHINE_LEARNING,
        "display_name": "TensorFlow",
        "description": "TensorFlow deep learning framework",
        "related_skills": ["python", "deep_learning", "neural_networks"]
    },
    "pytorch": {
        "category": SkillCategory.MACHINE_LEARNING,
        "display_name": "PyTorch",
        "description": "PyTorch deep learning framework",
        "related_skills": ["python", "deep_learning", "neural_networks"]
    },
    "deep_learning": {
        "category": SkillCategory.MACHINE_LEARNING,
        "display_name": "Deep Learning",
        "description": "Deep learning and neural networks",
        "related_skills": ["tensorflow", "pytorch", "machine_learning"]
    },
    "machine_learning": {
        "category": SkillCategory.MACHINE_LEARNING,
        "display_name": "Machine Learning",
        "description": "Machine learning algorithms and techniques",
        "related_skills": ["python", "scikit_learn", "data_science"]
    },
    "natural_language_processing": {
        "category": SkillCategory.MACHINE_LEARNING,
        "display_name": "Natural Language Processing",
        "description": "NLP and text processing",
        "related_skills": ["python", "deep_learning", "transformers"]
    },
    
    # Security
    "cybersecurity": {
        "category": SkillCategory.SECURITY,
        "display_name": "Cybersecurity",
        "description": "Cybersecurity principles and practices",
        "related_skills": ["penetration_testing", "security_analysis"]
    },
    "penetration_testing": {
        "category": SkillCategory.SECURITY,
        "display_name": "Penetration Testing",
        "description": "Penetration testing and ethical hacking",
        "related_skills": ["cybersecurity", "security_tools"]
    },
    "encryption": {
        "category": SkillCategory.SECURITY,
        "display_name": "Encryption",
        "description": "Encryption and cryptography",
        "related_skills": ["cybersecurity", "security"]
    },
    
    # Design
    "ui_design": {
        "category": SkillCategory.DESIGN,
        "display_name": "UI Design",
        "description": "User interface design",
        "related_skills": ["ux_design", "figma", "design_systems"]
    },
    "ux_design": {
        "category": SkillCategory.DESIGN,
        "display_name": "UX Design",
        "description": "User experience design",
        "related_skills": ["ui_design", "user_research", "prototyping"]
    },
    "figma": {
        "category": SkillCategory.DESIGN,
        "display_name": "Figma",
        "description": "Figma design tool",
        "related_skills": ["ui_design", "prototyping"]
    },
    
    # Soft Skills
    "problem_solving": {
        "category": SkillCategory.SOFT_SKILL,
        "display_name": "Problem Solving",
        "description": "Analytical and problem-solving skills",
        "related_skills": ["critical_thinking"]
    },
    "communication": {
        "category": SkillCategory.SOFT_SKILL,
        "display_name": "Communication",
        "description": "Effective communication skills",
        "related_skills": ["teamwork", "presentation"]
    },
    "teamwork": {
        "category": SkillCategory.SOFT_SKILL,
        "display_name": "Teamwork",
        "description": "Collaboration and teamwork",
        "related_skills": ["communication"]
    },
    "leadership": {
        "category": SkillCategory.SOFT_SKILL,
        "display_name": "Leadership",
        "description": "Leadership and team management",
        "related_skills": ["communication", "project_management"]
    },
    
    # Additional technical skills
    "rest_api": {
        "category": SkillCategory.WEB_DEVELOPMENT,
        "display_name": "REST API",
        "description": "RESTful API design and development",
        "related_skills": ["http", "json", "api_design"]
    },
    "linux": {
        "category": SkillCategory.DEVOPS_TOOL,
        "display_name": "Linux",
        "description": "Linux operating system",
        "related_skills": ["bash", "unix", "system_administration"]
    },
    "bash": {
        "category": SkillCategory.DEVOPS_TOOL,
        "display_name": "Bash",
        "description": "Bash shell scripting",
        "related_skills": ["linux", "shell_scripting"]
    },
    "statistics": {
        "category": SkillCategory.DATA_SCIENCE,
        "display_name": "Statistics",
        "description": "Statistical analysis and methods",
        "related_skills": ["mathematics", "data_analysis"]
    },
    "data_analysis": {
        "category": SkillCategory.DATA_SCIENCE,
        "display_name": "Data Analysis",
        "description": "Data analysis and interpretation",
        "related_skills": ["statistics", "python", "r"]
    },
    "prototyping": {
        "category": SkillCategory.DESIGN,
        "display_name": "Prototyping",
        "description": "Creating prototypes and mockups",
        "related_skills": ["figma", "ui_design", "user_testing"]
    },
    "user_research": {
        "category": SkillCategory.DESIGN,
        "display_name": "User Research",
        "description": "Conducting user research and testing",
        "related_skills": ["ux_design", "usability_testing"]
    },
}

# Skill Synonyms - Maps variations to canonical names
SKILL_SYNONYMS: Dict[str, str] = {
    # Python variations
    "python programming": "python",
    "python3": "python",
    "py": "python",
    
    # JavaScript variations
    "js": "javascript",
    "javascript programming": "javascript",
    "ecmascript": "javascript",
    
    # TypeScript variations
    "ts": "typescript",
    
    # React variations
    "react.js": "react",
    "reactjs": "react",
    
    # Next.js variations
    "next": "nextjs",
    "next.js": "nextjs",
    
    # Node.js variations
    "node": "nodejs",
    "node.js": "nodejs",
    
    # Database variations
    "postgres": "postgresql",
    "psql": "postgresql",
    "mongo": "mongodb",
    
    # Cloud variations
    "amazon web services": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    
    # ML variations
    "ml": "machine_learning",
    "sklearn": "scikit_learn",
    "scikit-learn": "scikit_learn",
    "tf": "tensorflow",
    "nlp": "natural_language_processing",
    "dl": "deep_learning",
    
    # Design variations
    "user interface design": "ui_design",
    "user experience design": "ux_design",
    "ui/ux": "ui_design",
    
    # Other
    "c++": "cpp",
    "c plus plus": "cpp",
    "c#": "csharp",
    "c sharp": "csharp",
    "ci/cd": "cicd",
    "continuous integration": "cicd",
}


def normalize_skill_name(skill_text: str) -> Optional[str]:
    """
    Normalize a skill name to its canonical form.
    
    Args:
        skill_text: Raw skill text (e.g., "React.js", "Python Programming")
        
    Returns:
        Canonical skill name or None if not recognized
    """
    if not skill_text:
        return None
    
    # Lowercase and strip
    normalized = skill_text.lower().strip()
    
    # Remove common suffixes
    normalized = normalized.replace(" programming", "").replace(" language", "")
    
    # Check if it's already canonical
    if normalized in CANONICAL_SKILLS:
        return normalized
    
    # Check synonyms
    if normalized in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[normalized]
    
    # Fuzzy matching (simple version)
    # Check if normalized is a substring of any canonical skill
    for canonical in CANONICAL_SKILLS.keys():
        if normalized in canonical or canonical in normalized:
            return canonical
    
    return None


def get_skill_category(skill_name: str) -> Optional[SkillCategory]:
    """Get the category of a canonical skill."""
    skill_data = CANONICAL_SKILLS.get(skill_name)
    return skill_data["category"] if skill_data else None


def get_related_skills(skill_name: str) -> List[str]:
    """Get related skills for a canonical skill."""
    skill_data = CANONICAL_SKILLS.get(skill_name)
    return skill_data.get("related_skills", []) if skill_data else []


def search_skills(query: str, limit: int = 10) -> List[str]:
    """
    Search for skills matching a query.
    
    Args:
        query: Search query
        limit: Maximum results to return
        
    Returns:
        List of matching canonical skill names
    """
    query_lower = query.lower()
    matches = []
    
    for canonical_name, skill_data in CANONICAL_SKILLS.items():
        display_name = skill_data["display_name"].lower()
        if query_lower in canonical_name or query_lower in display_name:
            matches.append(canonical_name)
    
    return matches[:limit]
