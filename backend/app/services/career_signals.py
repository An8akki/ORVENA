"""Shared deterministic career signal extraction for AI-independent matching."""

import re
from typing import Iterable


# Expressions deliberately include common paraphrases, tools, activities, and
# role outcomes. This makes the fallback useful when a student describes an
# interest in everyday language instead of using a job title verbatim.
ROLE_SIGNALS = {
    "Software Engineer": [
        "software engineer", "software developer", "software development", "build software",
        "building software", "programming", "coding", "write code", "solve technical problems",
        "application development", "computer science", "algorithms", "developer tools",
        "backend systems", "scalable systems", "technical problem solving",
    ],
    "Full-Stack Developer": [
        "full stack", "full-stack", "frontend and backend", "front end and back end",
        "both frontend and backend", "entire web application", "end-to-end application",
        "web app", "web application", "web development", "website and api", "react and django",
        "user interface and server", "client and server", "complete product",
    ],
    "Frontend Developer": [
        "frontend", "front-end", "front end", "user interface", "user experience",
        "web design", "interactive website", "responsive design", "browser", "react",
        "visual interface", "accessibility", "design systems", "css", "javascript interface",
    ],
    "Backend Developer": [
        "backend", "back-end", "back end", "server side", "server-side", "api development",
        "rest api", "database systems", "distributed systems", "microservices", "django",
        "fastapi", "authentication", "scalable backend", "data modeling",
    ],
    "Data Scientist": [
        "data scientist", "data science", "analyze data", "data analysis", "find patterns",
        "statistics", "experimentation", "predictive analytics", "data visualization",
        "business insights", "pandas", "research data", "statistical modeling",
    ],
    "Data Engineer": [
        "data engineer", "data engineering", "data pipeline", "data pipelines", "etl",
        "elt", "data warehouse", "data infrastructure", "move and transform data",
        "streaming data", "batch processing", "airflow", "spark", "kafka", "data platform",
    ],
    "Machine Learning Engineer": [
        "machine learning", "artificial intelligence", " ai ", " ml ", "deep learning",
        "neural network", "neural networks", "train models", "model training", "computer vision",
        "natural language processing", "generative ai", "large language model", "llm",
        "pytorch", "tensorflow", "intelligent systems", "predictive model", "model deployment",
    ],
    "Cybersecurity Analyst": [
        "cybersecurity", "cyber security", "information security", "application security",
        "network security", "ethical hacking", "penetration testing", "vulnerability assessment",
        "threat detection", "incident response", "digital forensics", "security operations",
        "siem", "wireshark", "nmap", "protect systems", "defend networks", "risk assessment",
    ],
    "Cloud Engineer": [
        "cloud engineer", "cloud computing", "cloud infrastructure", "aws", "amazon web services",
        "azure", "google cloud", "gcp", "deploy to cloud", "cloud architecture", "containers",
        "kubernetes", "infrastructure as code", "terraform", "reliable infrastructure",
    ],
    "DevOps Engineer": [
        "devops", "continuous integration", "continuous delivery", "ci/cd", "deployment automation",
        "automate deployments", "release engineering", "site reliability", "sre", "build pipelines",
        "monitoring systems", "linux administration", "docker", "infrastructure automation",
    ],
    "Product Manager": [
        "product manager", "product management", "product strategy", "product planning",
        "understand user needs", "customer problems", "lead a product", "roadmap planning",
        "prioritize features", "business strategy", "market research", "cross-functional team",
    ],
    "UX/UI Designer": [
        "ux designer", "ui designer", "ux/ui", "user experience", "user interface design",
        "interaction design", "visual design", "figma", "wireframes", "prototypes",
        "user research", "usability testing", "accessible design", "design digital products",
    ],
}


# Canonical skill signals collected from CV text and saved answers. Canonical
# values intentionally overlap matcher vocabulary so aliases become useful in
# scoring without pretending the candidate knows every related technology.
SKILL_SIGNALS = {
    "programming": ["programming", "coding", "write code", "software development", "python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust"],
    "algorithms": ["algorithms", "data structures", "problem solving", "leetcode", "complexity analysis", "computational thinking"],
    "testing": ["testing", "unit test", "integration test", "pytest", "jest", "quality assurance", "debugging"],
    "git": ["git", "github", "version control", "pull request", "source control"],
    "html": ["html", "html5", "semantic markup"],
    "css": ["css", "css3", "tailwind", "bootstrap", "sass", "responsive styling"],
    "javascript": ["javascript", "ecmascript", "js", "typescript", "tsx", "jsx"],
    "react": ["react", "next.js", "nextjs", "react native"],
    "backend": ["backend", "back-end", "server side", "django", "fastapi", "flask", "spring boot", "express.js", "node.js"],
    "database": ["database", "sql", "postgresql", "postgres", "mysql", "sqlite", "mongodb", "nosql", "redis"],
    "api design": ["api", "apis", "rest", "restful", "graphql", "django rest framework", "api integration"],
    "python": ["python", "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow", "fastapi"],
    "statistics": ["statistics", "probability", "hypothesis testing", "regression analysis", "statistical analysis"],
    "data analysis": ["data analysis", "analytics", "exploratory data analysis", "data visualization", "tableau", "power bi"],
    "machine learning": ["machine learning", " ml ", "deep learning", "predictive modeling", "model training", "scikit-learn"],
    "computer vision": ["computer vision", "opencv", "image classification", "object detection", "image processing"],
    "data pipeline": ["data pipeline", "data pipelines", "etl", "elt", "airflow", "spark", "kafka", "data ingestion"],
    "cloud": ["cloud", "aws", "amazon web services", "azure", "gcp", "google cloud", "cloud deployment"],
    "docker": ["docker", "containerization", "containers", "docker compose"],
    "automation": ["automation", "automate", "ci/cd", "continuous integration", "continuous delivery", "jenkins", "github actions"],
    "linux": ["linux", "ubuntu", "bash", "shell scripting", "command line", "unix"],
    "networking": ["networking", "tcp/ip", "dns", "http", "tls", "firewall", "network traffic", "wireshark", "nmap", "zeek"],
    "security": ["cybersecurity", "cyber security", "security", "vulnerability", "threat modeling", "penetration testing", "owasp", "secure coding", "hashcat", "ettercap"],
    "incident response": ["incident response", "security operations", "siem", "threat hunting", "digital forensics"],
    "leadership": ["leadership", "led a team", "team lead", "mentoring", "coordinated a team", "managed a team"],
    "communication": ["communication", "presented", "presentation", "technical writing", "documentation", "explained technical"],
    "teamwork": ["teamwork", "collaboration", "collaborated", "cross-functional", "team project", "worked with a team"],
    "project management": ["project management", "project planning", "agile", "scrum", "sprint planning", "delivered a project"],
    "design": ["design", "figma", "wireframe", "prototype", "user research", "usability", "accessibility"],
    "critical thinking": ["critical thinking", "analytical thinking", "root cause", "evaluate trade-offs", "reasoning"],
}


def _has_phrase(text: str, phrase: str) -> bool:
    phrase = phrase.strip().lower()
    if not phrase:
        return False
    return bool(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text))


def infer_preferred_roles(text: str, limit: int = 8) -> list[str]:
    """Rank roles by varied phrase evidence instead of a few exact title words."""
    normalized = re.sub(r"\s+", " ", (text or "").lower())
    ranked = []
    for role, phrases in ROLE_SIGNALS.items():
        hits = [phrase for phrase in phrases if _has_phrase(normalized, phrase)]
        if hits:
            # A direct target title or highly specific tool counts more than a
            # broad activity, while several independent clues accumulate.
            score = sum(3 if len(phrase.split()) >= 2 else 1 for phrase in hits)
            ranked.append((score, role))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [role for _, role in ranked[:limit]]


def extract_skill_evidence(text: str, existing: Iterable[str] = ()) -> list[str]:
    """Return de-duplicated canonical skills evidenced in supplied text."""
    normalized = re.sub(r"\s+", " ", (text or "").lower())
    skills = {str(item).strip() for item in existing if item and str(item).strip()}
    for canonical, phrases in SKILL_SIGNALS.items():
        if any(_has_phrase(normalized, phrase) for phrase in phrases):
            skills.add(canonical)
    return sorted(skills, key=str.lower)


def extract_interest_summary(text: str, limit: int = 4) -> list[str]:
    """Find concrete role/skill themes for readable plan personalization."""
    roles = infer_preferred_roles(text, limit=limit)
    skills = extract_skill_evidence(text)
    role_terms = {role.lower() for role in roles}
    skill_terms = [skill for skill in skills if skill.lower() not in role_terms]
    return (roles + skill_terms)[:limit]
