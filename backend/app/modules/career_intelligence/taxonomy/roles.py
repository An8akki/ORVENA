"""
Career Role Definitions

Structured, maintainable definitions for all supported career roles.
Each role includes description, requirements, typical responsibilities,
and entry-level expectations.
"""
from typing import Dict, List, Optional
from uuid import UUID, uuid5, NAMESPACE_DNS
from datetime import datetime


# Role Families
ROLE_FAMILIES = {
    "software_engineering": {
        "name": "Software Engineering",
        "description": "Building and maintaining software applications",
        "icon": "code"
    },
    "ai_and_data": {
        "name": "AI & Data",
        "description": "Working with data, machine learning, and AI systems",
        "icon": "brain"
    },
    "security_infrastructure": {
        "name": "Security & Infrastructure",
        "description": "Protecting systems and managing infrastructure",
        "icon": "shield"
    },
    "product_design": {
        "name": "Product & Design",
        "description": "Creating user experiences and product strategy",
        "icon": "layout"
    }
}


def generate_role_id(role_name: str) -> str:
    """Generate a deterministic UUID for a role based on its name."""
    return str(uuid5(NAMESPACE_DNS, f"orvena.role.{role_name}"))


# Career Roles Dictionary
# Format: role_key -> role_definition
CAREER_ROLES: Dict[str, Dict] = {
    "frontend_engineer": {
        "id": generate_role_id("frontend_engineer"),
        "name": "Frontend Engineer",
        "family": "software_engineering",
        "description": "Build user-facing web applications with modern JavaScript frameworks and responsive design.",
        
        "typical_responsibilities": [
            "Develop interactive user interfaces using React, Vue, or Angular",
            "Implement responsive designs and ensure cross-browser compatibility",
            "Collaborate with designers to translate mockups into working applications",
            "Optimize application performance and user experience",
            "Write clean, maintainable, and testable code",
            "Integrate with backend APIs and services"
        ],
        
        "core_skills": [
            "javascript", "typescript", "html", "css",
            "react", "vue", "angular",
            "responsive_design", "git"
        ],
        
        "optional_skills": [
            "nextjs", "redux", "webpack", "testing",
            "accessibility", "performance_optimization"
        ],
        
        "entry_requirements": [
            "Strong foundation in JavaScript/TypeScript",
            "Experience with at least one modern frontend framework",
            "Understanding of HTML, CSS, and responsive design",
            "Portfolio with 2-3 frontend projects"
        ],
        
        "typical_salary_range": {"min": 70000, "max": 130000, "currency": "USD"},
        "growth_outlook": "High demand with 15% projected growth. Remote work opportunities abundant.",
        "work_environment": "Typically office or remote, collaborative with design and backend teams",
        
        "example_projects": [
            "E-commerce product catalog with filtering and search",
            "Real-time dashboard with data visualization",
            "Responsive portfolio website with animations"
        ],
        
        "learning_path_priority": ["javascript_fundamentals", "react_basics", "state_management", "api_integration"],
        "related_roles": ["full_stack_developer", "ui_ux_designer"],
        
        "last_updated": "2024-01-15"
    },
    
    "backend_engineer": {
        "id": generate_role_id("backend_engineer"),
        "name": "Backend Engineer",
        "family": "software_engineering",
        "description": "Design and implement server-side logic, databases, and APIs that power applications.",
        
        "typical_responsibilities": [
            "Design and implement RESTful APIs and GraphQL services",
            "Develop server-side business logic and data processing",
            "Design and optimize database schemas",
            "Implement authentication, authorization, and security",
            "Write unit and integration tests",
            "Monitor and optimize system performance"
        ],
        
        "core_skills": [
            "python", "java", "nodejs", "go",
            "rest_api", "sql", "postgresql", "mongodb",
            "git", "testing"
        ],
        
        "optional_skills": [
            "microservices", "docker", "kubernetes",
            "redis", "message_queues", "graphql",
            "aws", "azure", "gcp"
        ],
        
        "entry_requirements": [
            "Proficiency in at least one backend language (Python/Java/Node.js)",
            "Understanding of databases and SQL",
            "Experience building RESTful APIs",
            "Knowledge of authentication and security basics"
        ],
        
        "typical_salary_range": {"min": 75000, "max": 140000, "currency": "USD"},
        "growth_outlook": "Strong demand with 13% projected growth. Critical for all software companies.",
        "work_environment": "Office or remote, collaborate with frontend, DevOps, and data teams",
        
        "example_projects": [
            "RESTful API for task management with authentication",
            "E-commerce backend with payment integration",
            "Real-time chat application with WebSockets"
        ],
        
        "learning_path_priority": ["backend_fundamentals", "database_design", "api_development", "deployment"],
        "related_roles": ["full_stack_developer", "devops_engineer"],
        
        "last_updated": "2024-01-15"
    },
    
    "full_stack_developer": {
        "id": generate_role_id("full_stack_developer"),
        "name": "Full-Stack Developer",
        "family": "software_engineering",
        "description": "Build complete web applications handling both frontend and backend development.",
        
        "typical_responsibilities": [
            "Develop end-to-end web applications",
            "Design database schemas and APIs",
            "Implement user interfaces and experiences",
            "Deploy and maintain applications",
            "Handle both client and server-side logic",
            "Troubleshoot across the entire stack"
        ],
        
        "core_skills": [
            "javascript", "typescript", "python", "nodejs",
            "react", "nextjs", "sql", "rest_api",
            "git", "deployment"
        ],
        
        "optional_skills": [
            "docker", "cicd", "aws", "testing",
            "graphql", "mongodb", "redis"
        ],
        
        "entry_requirements": [
            "Comfortable with both frontend and backend technologies",
            "Experience building complete applications",
            "Understanding of databases and APIs",
            "Portfolio with full-stack projects"
        ],
        
        "typical_salary_range": {"min": 75000, "max": 135000, "currency": "USD"},
        "growth_outlook": "High demand, especially in startups. 14% projected growth.",
        "work_environment": "Versatile role, often in startups or small teams",
        
        "example_projects": [
            "Social media platform with user auth and posts",
            "Project management tool with real-time updates",
            "E-commerce site with payment and admin panel"
        ],
        
        "learning_path_priority": ["frontend_basics", "backend_basics", "database_design", "full_stack_integration"],
        "related_roles": ["frontend_engineer", "backend_engineer"],
        
        "last_updated": "2024-01-15"
    },
    
    "data_analyst": {
        "id": generate_role_id("data_analyst"),
        "name": "Data Analyst",
        "family": "ai_and_data",
        "description": "Analyze data to extract insights and support business decision-making.",
        
        "typical_responsibilities": [
            "Collect and analyze data from various sources",
            "Create visualizations and dashboards",
            "Write SQL queries to extract insights",
            "Present findings to stakeholders",
            "Identify trends and patterns in data",
            "Support data-driven decision making"
        ],
        
        "core_skills": [
            "sql", "python", "r",
            "excel", "data_visualization",
            "statistics", "pandas", "numpy"
        ],
        
        "optional_skills": [
            "tableau", "power_bi", "looker",
            "machine_learning", "a_b_testing"
        ],
        
        "entry_requirements": [
            "Strong SQL and data manipulation skills",
            "Experience with Python or R for analysis",
            "Understanding of statistics basics",
            "Portfolio with analysis projects"
        ],
        
        "typical_salary_range": {"min": 65000, "max": 110000, "currency": "USD"},
        "growth_outlook": "Growing field with 11% projected growth. Data-driven decisions increasingly important.",
        "work_environment": "Office or remote, work closely with business teams",
        
        "example_projects": [
            "Customer behavior analysis with recommendations",
            "Sales dashboard with key metrics",
            "A/B test analysis and reporting"
        ],
        
        "learning_path_priority": ["sql_basics", "python_for_data", "statistics", "visualization"],
        "related_roles": ["data_scientist", "business_analyst"],
        
        "last_updated": "2024-01-15"
    },
    
    "data_scientist": {
        "id": generate_role_id("data_scientist"),
        "name": "Data Scientist",
        "family": "ai_and_data",
        "description": "Build predictive models and use advanced analytics to solve complex problems.",
        
        "typical_responsibilities": [
            "Develop machine learning models and algorithms",
            "Perform statistical analysis and hypothesis testing",
            "Clean and prepare data for modeling",
            "Evaluate model performance and iterate",
            "Communicate findings to technical and non-technical audiences",
            "Deploy models to production"
        ],
        
        "core_skills": [
            "python", "r", "sql",
            "machine_learning", "statistics",
            "pandas", "numpy", "scikit_learn"
        ],
        
        "optional_skills": [
            "deep_learning", "tensorflow", "pytorch",
            "spark", "aws", "docker",
            "natural_language_processing"
        ],
        
        "entry_requirements": [
            "Strong Python programming skills",
            "Understanding of machine learning fundamentals",
            "Statistics and probability knowledge",
            "Experience with real datasets and models"
        ],
        
        "typical_salary_range": {"min": 85000, "max": 150000, "currency": "USD"},
        "growth_outlook": "Excellent growth at 16%. High demand across industries.",
        "work_environment": "Office or remote, collaborate with engineering and business teams",
        
        "example_projects": [
            "Customer churn prediction model",
            "Recommendation system for products",
            "Time series forecasting for demand"
        ],
        
        "learning_path_priority": ["python_advanced", "machine_learning_fundamentals", "model_evaluation", "deployment"],
        "related_roles": ["machine_learning_engineer", "data_analyst"],
        
        "last_updated": "2024-01-15"
    },
    
    "machine_learning_engineer": {
        "id": generate_role_id("machine_learning_engineer"),
        "name": "Machine Learning Engineer",
        "family": "ai_and_data",
        "description": "Design, build, and deploy machine learning systems at scale.",
        
        "typical_responsibilities": [
            "Build and optimize ML pipelines",
            "Deploy models to production environments",
            "Monitor model performance and retrain as needed",
            "Design scalable ML infrastructure",
            "Collaborate with data scientists on model development",
            "Implement MLOps best practices"
        ],
        
        "core_skills": [
            "python", "machine_learning", "deep_learning",
            "tensorflow", "pytorch", "scikit_learn",
            "docker", "git", "linux"
        ],
        
        "optional_skills": [
            "kubernetes", "aws", "mlflow",
            "spark", "airflow", "mlops",
            "natural_language_processing", "computer_vision"
        ],
        
        "entry_requirements": [
            "Strong software engineering skills",
            "Experience with ML frameworks (TensorFlow/PyTorch)",
            "Understanding of ML model deployment",
            "Knowledge of cloud platforms"
        ],
        
        "typical_salary_range": {"min": 95000, "max": 170000, "currency": "USD"},
        "growth_outlook": "Explosive growth at 22%. Critical for AI adoption.",
        "work_environment": "Usually remote-friendly, work with data science and engineering teams",
        
        "example_projects": [
            "Real-time inference API for image classification",
            "Automated ML pipeline with monitoring",
            "Recommendation engine deployed at scale"
        ],
        
        "learning_path_priority": ["ml_fundamentals", "deep_learning", "model_deployment", "mlops"],
        "related_roles": ["data_scientist", "ai_engineer"],
        
        "last_updated": "2024-01-15"
    },
    
    "data_engineer": {
        "id": generate_role_id("data_engineer"),
        "name": "Data Engineer",
        "family": "ai_and_data",
        "description": "Build and maintain data infrastructure, pipelines, and systems.",
        
        "typical_responsibilities": [
            "Design and build data pipelines",
            "Maintain data warehouses and lakes",
            "Optimize data storage and retrieval",
            "Ensure data quality and integrity",
            "Implement ETL/ELT processes",
            "Support data scientists and analysts"
        ],
        
        "core_skills": [
            "python", "sql", "etl",
            "postgresql", "data_warehousing",
            "airflow", "spark", "git"
        ],
        
        "optional_skills": [
            "kafka", "snowflake", "redshift",
            "databricks", "dbt", "kubernetes"
        ],
        
        "entry_requirements": [
            "Strong SQL and database knowledge",
            "Experience with data pipeline tools",
            "Understanding of data modeling",
            "Knowledge of cloud data services"
        ],
        
        "typical_salary_range": {"min": 85000, "max": 145000, "currency": "USD"},
        "growth_outlook": "Strong growth at 13%. Essential for data-driven companies.",
        "work_environment": "Office or remote, support data science and analytics teams",
        
        "example_projects": [
            "ETL pipeline for data warehouse",
            "Real-time data streaming with Kafka",
            "Data quality monitoring system"
        ],
        
        "learning_path_priority": ["sql_advanced", "data_pipelines", "data_warehousing", "cloud_data"],
        "related_roles": ["backend_engineer", "data_scientist"],
        
        "last_updated": "2024-01-15"
    },
    
    "devops_engineer": {
        "id": generate_role_id("devops_engineer"),
        "name": "DevOps Engineer",
        "family": "security_infrastructure",
        "description": "Automate infrastructure, improve deployment processes, and ensure system reliability.",
        
        "typical_responsibilities": [
            "Build and maintain CI/CD pipelines",
            "Automate infrastructure provisioning",
            "Monitor system health and performance",
            "Implement security best practices",
            "Manage cloud infrastructure",
            "Support development teams with deployments"
        ],
        
        "core_skills": [
            "linux", "docker", "kubernetes",
            "cicd", "git", "bash",
            "aws", "terraform"
        ],
        
        "optional_skills": [
            "ansible", "jenkins", "prometheus",
            "grafana", "elk_stack", "security"
        ],
        
        "entry_requirements": [
            "Experience with Linux system administration",
            "Knowledge of containerization (Docker)",
            "Understanding of CI/CD concepts",
            "Familiarity with at least one cloud platform"
        ],
        
        "typical_salary_range": {"min": 80000, "max": 145000, "currency": "USD"},
        "growth_outlook": "High demand with 12% growth. Critical for modern infrastructure.",
        "work_environment": "Remote-friendly, work across all technical teams",
        
        "example_projects": [
            "Automated deployment pipeline with GitHub Actions",
            "Kubernetes cluster setup and management",
            "Infrastructure as code with Terraform"
        ],
        
        "learning_path_priority": ["linux_basics", "docker_kubernetes", "cicd", "cloud_infrastructure"],
        "related_roles": ["cloud_engineer", "site_reliability_engineer"],
        
        "last_updated": "2024-01-15"
    },
    
    "cloud_engineer": {
        "id": generate_role_id("cloud_engineer"),
        "name": "Cloud Engineer",
        "family": "security_infrastructure",
        "description": "Design, implement, and manage cloud infrastructure and services.",
        
        "typical_responsibilities": [
            "Design cloud architecture solutions",
            "Manage cloud resources and costs",
            "Implement security and compliance",
            "Optimize cloud performance",
            "Automate cloud operations",
            "Support application teams"
        ],
        
        "core_skills": [
            "aws", "azure", "gcp",
            "terraform", "cloud_architecture",
            "networking", "security"
        ],
        
        "optional_skills": [
            "kubernetes", "serverless", "cicd",
            "cost_optimization", "disaster_recovery"
        ],
        
        "entry_requirements": [
            "Experience with at least one major cloud platform",
            "Understanding of cloud services and architecture",
            "Knowledge of infrastructure as code",
            "Basic networking and security knowledge"
        ],
        
        "typical_salary_range": {"min": 85000, "max": 150000, "currency": "USD"},
        "growth_outlook": "Excellent growth at 15%. Cloud adoption accelerating.",
        "work_environment": "Usually remote-friendly, work with DevOps and development teams",
        
        "example_projects": [
            "Multi-region cloud deployment with failover",
            "Serverless application architecture",
            "Cloud migration from on-premise"
        ],
        
        "learning_path_priority": ["cloud_fundamentals", "aws_or_azure", "iac", "cloud_security"],
        "related_roles": ["devops_engineer", "solutions_architect"],
        
        "last_updated": "2024-01-15"
    },
    
    "cybersecurity_analyst": {
        "id": generate_role_id("cybersecurity_analyst"),
        "name": "Cybersecurity Analyst",
        "family": "security_infrastructure",
        "description": "Protect systems and data from security threats and vulnerabilities.",
        
        "typical_responsibilities": [
            "Monitor systems for security threats",
            "Investigate security incidents",
            "Implement security controls and policies",
            "Conduct vulnerability assessments",
            "Respond to security breaches",
            "Educate teams on security best practices"
        ],
        
        "core_skills": [
            "cybersecurity", "networking", "linux",
            "security_tools", "incident_response",
            "risk_assessment"
        ],
        
        "optional_skills": [
            "penetration_testing", "siem", "ids_ips",
            "forensics", "compliance", "scripting"
        ],
        
        "entry_requirements": [
            "Understanding of networking and security fundamentals",
            "Knowledge of common security threats and mitigations",
            "Familiarity with security tools",
            "Security certifications helpful (Security+, CEH)"
        ],
        
        "typical_salary_range": {"min": 75000, "max": 130000, "currency": "USD"},
        "growth_outlook": "Strong growth at 14%. Increasing importance with cyber threats.",
        "work_environment": "Office or remote, may require on-call rotation",
        
        "example_projects": [
            "Security audit and vulnerability assessment",
            "Incident response plan and simulation",
            "Security monitoring dashboard"
        ],
        
        "learning_path_priority": ["security_fundamentals", "networking", "security_tools", "incident_response"],
        "related_roles": ["security_engineer", "penetration_tester"],
        
        "last_updated": "2024-01-15"
    },
    
    "ui_ux_designer": {
        "id": generate_role_id("ui_ux_designer"),
        "name": "UI/UX Designer",
        "family": "product_design",
        "description": "Design user interfaces and experiences that are beautiful, intuitive, and effective.",
        
        "typical_responsibilities": [
            "Create wireframes, mockups, and prototypes",
            "Conduct user research and usability testing",
            "Design user interfaces and interactions",
            "Develop design systems and guidelines",
            "Collaborate with developers on implementation",
            "Iterate based on user feedback"
        ],
        
        "core_skills": [
            "ui_design", "ux_design", "figma",
            "user_research", "prototyping",
            "design_systems", "usability_testing"
        ],
        
        "optional_skills": [
            "html", "css", "javascript",
            "animation", "accessibility", "sketch"
        ],
        
        "entry_requirements": [
            "Portfolio showcasing design work",
            "Proficiency in design tools (Figma/Sketch)",
            "Understanding of UX principles",
            "Experience with user research methods"
        ],
        
        "typical_salary_range": {"min": 70000, "max": 125000, "currency": "USD"},
        "growth_outlook": "Good growth at 8%. User experience increasingly valued.",
        "work_environment": "Office or remote, collaborate with product and engineering teams",
        
        "example_projects": [
            "Mobile app redesign with user research",
            "Design system for web application",
            "E-commerce checkout flow optimization"
        ],
        
        "learning_path_priority": ["design_fundamentals", "ux_research", "prototyping", "design_systems"],
        "related_roles": ["product_designer", "frontend_engineer"],
        
        "last_updated": "2024-01-15"
    },
    
    "product_manager": {
        "id": generate_role_id("product_manager"),
        "name": "Product Manager",
        "family": "product_design",
        "description": "Define product vision, strategy, and roadmap while coordinating cross-functional teams.",
        
        "typical_responsibilities": [
            "Define product strategy and roadmap",
            "Gather and prioritize requirements",
            "Work with engineering and design teams",
            "Analyze user feedback and metrics",
            "Make data-driven decisions",
            "Communicate with stakeholders"
        ],
        
        "core_skills": [
            "product_strategy", "user_research",
            "data_analysis", "communication",
            "project_management", "prioritization"
        ],
        
        "optional_skills": [
            "technical_background", "sql", "agile",
            "a_b_testing", "analytics_tools"
        ],
        
        "entry_requirements": [
            "Strong analytical and communication skills",
            "Understanding of product development lifecycle",
            "Experience working with cross-functional teams",
            "Portfolio of product work or case studies",
            "Note: Often requires 2-3 years of experience in related role"
        ],
        
        "typical_salary_range": {"min": 85000, "max": 145000, "currency": "USD"},
        "growth_outlook": "Moderate growth at 7%. Important role in tech companies.",
        "work_environment": "Office or hybrid, central role coordinating multiple teams",
        
        "example_projects": [
            "Product launch from concept to delivery",
            "Feature prioritization and roadmap",
            "User research and product improvements"
        ],
        
        "learning_path_priority": ["product_fundamentals", "user_research", "data_analysis", "technical_literacy"],
        "related_roles": ["product_analyst", "product_designer"],
        
        "last_updated": "2024-01-15"
    }
}


def get_role_by_id(role_id: str) -> Optional[Dict]:
    """Get a role by its ID."""
    for role_key, role_data in CAREER_ROLES.items():
        if role_data["id"] == role_id:
            return role_data
    return None


def get_role_by_name(role_name: str) -> Optional[Dict]:
    """Get a role by its display name."""
    for role_key, role_data in CAREER_ROLES.items():
        if role_data["name"].lower() == role_name.lower():
            return role_data
    return None


def get_roles_by_family(family: str) -> List[Dict]:
    """Get all roles in a family."""
    return [
        role_data for role_data in CAREER_ROLES.values()
        if role_data["family"] == family
    ]


def get_all_roles() -> List[Dict]:
    """Get all career roles."""
    return list(CAREER_ROLES.values())


def search_roles(query: str) -> List[Dict]:
    """Search roles by name or description."""
    query_lower = query.lower()
    matches = []
    
    for role_data in CAREER_ROLES.values():
        if (query_lower in role_data["name"].lower() or
            query_lower in role_data["description"].lower()):
            matches.append(role_data)
    
    return matches
