"""
Roadmap Template Library

Structured, maintainable roadmap templates for all supported career roles.
Each template provides a complete learning path from beginner to job-ready.

Templates are versioned and can work independently of AI services.
"""
from typing import Dict, List
from ..types import RoadmapPhase, RoadmapMilestoneData, MilestoneStatus


# Frontend Engineer Roadmap
FRONTEND_ENGINEER_TEMPLATE = {
    "role_key": "frontend_engineer",
    "template_name": "Frontend Engineer Learning Path",
    "version": "1.0.0",
    "starting_level": "beginner",
    "description": "Complete learning path to become a job-ready Frontend Engineer",
    "prerequisites": ["Basic computer literacy", "English proficiency"],
    "estimated_duration_weeks": 16,
    "phases": [
        {
            "phase_id": "fe_phase_1",
            "phase_number": 1,
            "title": "Web Fundamentals",
            "description": "Master HTML, CSS, and JavaScript basics",
            "objectives": [
                "Understand HTML structure and semantic markup",
                "Style web pages with CSS and responsive design",
                "Write JavaScript for interactive web pages"
            ],
            "estimated_hours": 80,
            "prerequisites": [],
            "milestones": [
                {
                    "milestone_id": "fe_m1_html",
                    "sequence_number": 1,
                    "title": "HTML & Semantic Markup",
                    "description": "Learn HTML tags, document structure, and semantic elements",
                    "learning_objectives": [
                        "Understand HTML document structure",
                        "Use semantic HTML5 elements correctly",
                        "Create accessible forms and tables"
                    ],
                    "topics": [
                        "HTML syntax and elements",
                        "Document structure (head, body)",
                        "Semantic elements (article, section, nav)",
                        "Forms and input types",
                        "Accessibility basics"
                    ],
                    "activities": [
                        "Build a personal profile page",
                        "Create a multi-page website structure",
                        "Build an accessible contact form"
                    ],
                    "deliverable": "Personal portfolio website with multiple pages",
                    "prerequisites": [],
                    "estimated_hours": 20,
                    "completion_criteria": [
                        "Website uses proper HTML5 structure",
                        "All pages pass HTML validator",
                        "Forms are accessible and functional"
                    ],
                    "assessment_method": "Code review and W3C validation",
                    "resources": [
                        {"type": "documentation", "title": "MDN HTML Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML"},
                        {"type": "course", "title": "HTML Basics", "url": "https://www.freecodecamp.org"}
                    ],
                    "status": MilestoneStatus.PENDING
                },
                {
                    "milestone_id": "fe_m1_css",
                    "sequence_number": 2,
                    "title": "CSS & Responsive Design",
                    "description": "Style web pages and make them responsive",
                    "learning_objectives": [
                        "Apply CSS styles effectively",
                        "Understand the box model and flexbox",
                        "Create responsive layouts"
                    ],
                    "topics": [
                        "CSS selectors and specificity",
                        "Box model and layout",
                        "Flexbox and Grid",
                        "Responsive design principles",
                        "Media queries"
                    ],
                    "activities": [
                        "Style the portfolio with modern CSS",
                        "Create a responsive navigation menu",
                        "Build a responsive photo gallery"
                    ],
                    "deliverable": "Fully styled, mobile-responsive portfolio",
                    "prerequisites": ["fe_m1_html"],
                    "estimated_hours": 30,
                    "completion_criteria": [
                        "Site looks good on mobile, tablet, and desktop",
                        "Uses modern CSS techniques (Flexbox/Grid)",
                        "No layout breaking at different screen sizes"
                    ],
                    "assessment_method": "Responsive testing across devices",
                    "resources": [
                        {"type": "documentation", "title": "MDN CSS Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS"}
                    ],
                    "status": MilestoneStatus.PENDING
                },
                {
                    "milestone_id": "fe_m1_javascript",
                    "sequence_number": 3,
                    "title": "JavaScript Fundamentals",
                    "description": "Learn JavaScript programming basics",
                    "learning_objectives": [
                        "Understand JavaScript syntax and data types",
                        "Work with DOM manipulation",
                        "Handle events and user interactions"
                    ],
                    "topics": [
                        "Variables, data types, operators",
                        "Functions and scope",
                        "Arrays and objects",
                        "DOM manipulation",
                        "Event handling"
                    ],
                    "activities": [
                        "Add interactive features to portfolio",
                        "Build a simple calculator",
                        "Create a to-do list app"
                    ],
                    "deliverable": "Interactive to-do list application",
                    "prerequisites": ["fe_m1_css"],
                    "estimated_hours": 30,
                    "completion_criteria": [
                        "Application handles user input correctly",
                        "DOM updates dynamically",
                        "Events are handled properly"
                    ],
                    "assessment_method": "Functional testing",
                    "resources": [
                        {"type": "documentation", "title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"}
                    ],
                    "status": MilestoneStatus.PENDING
                }
            ]
        },
        {
            "phase_id": "fe_phase_2",
            "phase_number": 2,
            "title": "React & Modern Frontend",
            "description": "Learn React and modern frontend development",
            "objectives": [
                "Build applications with React",
                "Manage state and props",
                "Work with React ecosystem"
            ],
            "estimated_hours": 60,
            "prerequisites": ["fe_phase_1"],
            "milestones": [
                {
                    "milestone_id": "fe_m2_react_basics",
                    "sequence_number": 4,
                    "title": "React Fundamentals",
                    "description": "Learn React components, props, and state",
                    "learning_objectives": [
                        "Create React components",
                        "Understand props and state",
                        "Handle events in React"
                    ],
                    "topics": [
                        "JSX syntax",
                        "Components and props",
                        "State management",
                        "Lifecycle methods / Hooks",
                        "Event handling"
                    ],
                    "activities": [
                        "Convert to-do app to React",
                        "Build a weather app with API",
                        "Create a movie search app"
                    ],
                    "deliverable": "React-based movie search application",
                    "prerequisites": ["fe_m1_javascript"],
                    "estimated_hours": 40,
                    "completion_criteria": [
                        "Uses functional components and hooks",
                        "Properly manages component state",
                        "Fetches data from external API"
                    ],
                    "assessment_method": "Code review",
                    "resources": [
                        {"type": "documentation", "title": "React Official Docs", "url": "https://react.dev"}
                    ],
                    "status": MilestoneStatus.PENDING
                },
                {
                    "milestone_id": "fe_m2_tools",
                    "sequence_number": 5,
                    "title": "Frontend Tools & Git",
                    "description": "Learn development tools and version control",
                    "learning_objectives": [
                        "Use Git for version control",
                        "Work with npm and build tools",
                        "Debug React applications"
                    ],
                    "topics": [
                        "Git basics (commit, branch, merge)",
                        "npm and package management",
                        "React DevTools",
                        "ESLint and code quality",
                        "Browser DevTools"
                    ],
                    "activities": [
                        "Initialize Git repository for projects",
                        "Push code to GitHub",
                        "Configure ESLint for React"
                    ],
                    "deliverable": "All projects on GitHub with proper commit history",
                    "prerequisites": ["fe_m2_react_basics"],
                    "estimated_hours": 20,
                    "completion_criteria": [
                        "Projects are version controlled",
                        "Clean commit history with meaningful messages",
                        "Code follows linting rules"
                    ],
                    "assessment_method": "Repository review",
                    "resources": [
                        {"type": "documentation", "title": "Git Documentation", "url": "https://git-scm.com/doc"}
                    ],
                    "status": MilestoneStatus.PENDING
                }
            ]
        },
        {
            "phase_id": "fe_phase_3",
            "phase_number": 3,
            "title": "Portfolio Projects",
            "description": "Build impressive portfolio projects",
            "objectives": [
                "Create professional-quality applications",
                "Apply best practices",
                "Build a strong portfolio"
            ],
            "estimated_hours": 80,
            "prerequisites": ["fe_phase_2"],
            "milestones": [
                {
                    "milestone_id": "fe_m3_capstone",
                    "sequence_number": 6,
                    "title": "Capstone Project",
                    "description": "Build a full-featured React application",
                    "learning_objectives": [
                        "Plan and build a complete application",
                        "Implement complex state management",
                        "Deploy to production"
                    ],
                    "topics": [
                        "Project planning",
                        "Component architecture",
                        "State management (Context/Redux)",
                        "API integration",
                        "Deployment"
                    ],
                    "activities": [
                        "Design application architecture",
                        "Build full-stack features",
                        "Write tests",
                        "Deploy to Vercel/Netlify"
                    ],
                    "deliverable": "Deployed, production-ready application",
                    "prerequisites": ["fe_m2_tools"],
                    "estimated_hours": 60,
                    "completion_criteria": [
                        "Application is fully functional",
                        "Deployed and accessible online",
                        "Professional README and documentation"
                    ],
                    "assessment_method": "Project review",
                    "resources": [],
                    "status": MilestoneStatus.PENDING
                },
                {
                    "milestone_id": "fe_m3_interview_prep",
                    "sequence_number": 7,
                    "title": "Interview Preparation",
                    "description": "Prepare for frontend interviews",
                    "learning_objectives": [
                        "Solve common frontend problems",
                        "Explain technical concepts",
                        "Prepare portfolio presentation"
                    ],
                    "topics": [
                        "Common interview questions",
                        "Coding challenges",
                        "System design basics",
                        "Behavioral questions"
                    ],
                    "activities": [
                        "Solve 20 JavaScript challenges",
                        "Practice explaining projects",
                        "Mock interviews"
                    ],
                    "deliverable": "Interview preparation document",
                    "prerequisites": ["fe_m3_capstone"],
                    "estimated_hours": 20,
                    "completion_criteria": [
                        "Can explain all portfolio projects",
                        "Solved common coding problems",
                        "Prepared answers for behavioral questions"
                    ],
                    "assessment_method": "Mock interview",
                    "resources": [],
                    "status": MilestoneStatus.PENDING
                }
            ]
        }
    ]
}

# Backend Engineer Roadmap
BACKEND_ENGINEER_TEMPLATE = {
    "role_key": "backend_engineer",
    "template_name": "Backend Engineer Learning Path",
    "version": "1.0.0",
    "starting_level": "beginner",
    "description": "Complete learning path to become a job-ready Backend Engineer",
    "prerequisites": ["Basic programming knowledge"],
    "estimated_duration_weeks": 18,
    "phases": [
        {
            "phase_id": "be_phase_1",
            "phase_number": 1,
            "title": "Python & Programming Fundamentals",
            "description": "Master Python programming and core concepts",
            "objectives": [
                "Write clean, efficient Python code",
                "Understand OOP principles",
                "Work with data structures and algorithms"
            ],
            "estimated_hours": 80,
            "prerequisites": [],
            "milestones": [
                {
                    "milestone_id": "be_m1_python",
                    "sequence_number": 1,
                    "title": "Python Fundamentals",
                    "description": "Learn Python syntax and core concepts",
                    "learning_objectives": [
                        "Write Python programs",
                        "Understand data types and structures",
                        "Work with functions and modules"
                    ],
                    "topics": [
                        "Python syntax and basics",
                        "Data types and operators",
                        "Control flow",
                        "Functions and modules",
                        "File I/O"
                    ],
                    "activities": [
                        "Solve 30 Python exercises",
                        "Build a command-line calculator",
                        "Create a file processing script"
                    ],
                    "deliverable": "Collection of Python programs on GitHub",
                    "prerequisites": [],
                    "estimated_hours": 40,
                    "completion_criteria": [
                        "Comfortable writing Python code",
                        "Programs follow Python conventions (PEP 8)",
                        "Code is well-documented"
                    ],
                    "assessment_method": "Code review",
                    "resources": [
                        {"type": "documentation", "title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/"}
                    ],
                    "status": MilestoneStatus.PENDING
                },
                {
                    "milestone_id": "be_m1_oop",
                    "sequence_number": 2,
                    "title": "Object-Oriented Programming",
                    "description": "Learn OOP concepts in Python",
                    "learning_objectives": [
                        "Design classes and objects",
                        "Understand inheritance and polymorphism",
                        "Apply OOP principles"
                    ],
                    "topics": [
                        "Classes and objects",
                        "Inheritance",
                        "Polymorphism",
                        "Encapsulation",
                        "Design patterns basics"
                    ],
                    "activities": [
                        "Design a library management system",
                        "Build a simple game with classes",
                        "Refactor previous projects using OOP"
                    ],
                    "deliverable": "OOP-based application",
                    "prerequisites": ["be_m1_python"],
                    "estimated_hours": 40,
                    "completion_criteria": [
                        "Application uses classes effectively",
                        "Follows OOP principles",
                        "Code is well-structured"
                    ],
                    "assessment_method": "Design review",
                    "resources": [],
                    "status": MilestoneStatus.PENDING
                }
            ]
        },
        {
            "phase_id": "be_phase_2",
            "phase_number": 2,
            "title": "Web APIs & Databases",
            "description": "Build RESTful APIs and work with databases",
            "objectives": [
                "Design and build REST APIs",
                "Work with SQL databases",
                "Implement authentication"
            ],
            "estimated_hours": 100,
            "prerequisites": ["be_phase_1"],
            "milestones": [
                {
                    "milestone_id": "be_m2_sql",
                    "sequence_number": 3,
                    "title": "SQL & Database Design",
                    "description": "Master SQL and database concepts",
                    "learning_objectives": [
                        "Write SQL queries",
                        "Design normalized databases",
                        "Understand indexes and optimization"
                    ],
                    "topics": [
                        "SQL basics (SELECT, INSERT, UPDATE, DELETE)",
                        "Joins and subqueries",
                        "Database normalization",
                        "Indexes and performance",
                        "PostgreSQL"
                    ],
                    "activities": [
                        "Design a database schema",
                        "Write complex queries",
                        "Optimize slow queries"
                    ],
                    "deliverable": "Database design for e-commerce system",
                    "prerequisites": ["be_m1_oop"],
                    "estimated_hours": 30,
                    "completion_criteria": [
                        "Schema is properly normalized",
                        "Queries are efficient",
                        "Understands indexing strategy"
                    ],
                    "assessment_method": "Database review",
                    "resources": [
                        {"type": "documentation", "title": "PostgreSQL Tutorial", "url": "https://www.postgresql.org/docs/"}
                    ],
                    "status": MilestoneStatus.PENDING
                },
                {
                    "milestone_id": "be_m2_api",
                    "sequence_number": 4,
                    "title": "RESTful API Development",
                    "description": "Build REST APIs with FastAPI/Flask",
                    "learning_objectives": [
                        "Design REST API endpoints",
                        "Handle HTTP methods correctly",
                        "Implement CRUD operations"
                    ],
                    "topics": [
                        "REST principles",
                        "HTTP methods and status codes",
                        "FastAPI/Flask framework",
                        "Request/response handling",
                        "API documentation"
                    ],
                    "activities": [
                        "Build a task management API",
                        "Implement user authentication",
                        "Add API documentation"
                    ],
                    "deliverable": "Fully functional REST API",
                    "prerequisites": ["be_m2_sql"],
                    "estimated_hours": 50,
                    "completion_criteria": [
                        "API follows REST principles",
                        "All CRUD operations work",
                        "Proper error handling",
                        "API is documented"
                    ],
                    "assessment_method": "API testing",
                    "resources": [
                        {"type": "documentation", "title": "FastAPI Docs", "url": "https://fastapi.tiangolo.com"}
                    ],
                    "status": MilestoneStatus.PENDING
                },
                {
                    "milestone_id": "be_m2_auth",
                    "sequence_number": 5,
                    "title": "Authentication & Security",
                    "description": "Implement secure authentication",
                    "learning_objectives": [
                        "Implement JWT authentication",
                        "Secure sensitive data",
                        "Follow security best practices"
                    ],
                    "topics": [
                        "Password hashing",
                        "JWT tokens",
                        "Authorization",
                        "CORS",
                        "Security best practices"
                    ],
                    "activities": [
                        "Add JWT auth to API",
                        "Implement role-based access",
                        "Security audit"
                    ],
                    "deliverable": "Secured API with authentication",
                    "prerequisites": ["be_m2_api"],
                    "estimated_hours": 20,
                    "completion_criteria": [
                        "Authentication works correctly",
                        "Passwords are securely hashed",
                        "Protected routes require auth"
                    ],
                    "assessment_method": "Security review",
                    "resources": [],
                    "status": MilestoneStatus.PENDING
                }
            ]
        },
        {
            "phase_id": "be_phase_3",
            "phase_number": 3,
            "title": "Production & Deployment",
            "description": "Deploy and maintain production applications",
            "objectives": [
                "Deploy applications to cloud",
                "Implement testing",
                "Monitor and debug production apps"
            ],
            "estimated_hours": 60,
            "prerequisites": ["be_phase_2"],
            "milestones": [
                {
                    "milestone_id": "be_m3_testing",
                    "sequence_number": 6,
                    "title": "Testing & Quality",
                    "description": "Write tests for backend code",
                    "learning_objectives": [
                        "Write unit tests",
                        "Implement integration tests",
                        "Achieve good test coverage"
                    ],
                    "topics": [
                        "pytest basics",
                        "Unit testing",
                        "Integration testing",
                        "Mocking",
                        "Test coverage"
                    ],
                    "activities": [
                        "Write tests for API endpoints",
                        "Test database operations",
                        "Achieve 80% coverage"
                    ],
                    "deliverable": "Test suite with good coverage",
                    "prerequisites": ["be_m2_auth"],
                    "estimated_hours": 30,
                    "completion_criteria": [
                        "All endpoints have tests",
                        "Tests pass consistently",
                        "Coverage above 80%"
                    ],
                    "assessment_method": "Test review",
                    "resources": [],
                    "status": MilestoneStatus.PENDING
                },
                {
                    "milestone_id": "be_m3_deploy",
                    "sequence_number": 7,
                    "title": "Deployment & DevOps",
                    "description": "Deploy application to production",
                    "learning_objectives": [
                        "Deploy to cloud platform",
                        "Set up CI/CD",
                        "Monitor production apps"
                    ],
                    "topics": [
                        "Docker basics",
                        "Cloud platforms (AWS/Heroku)",
                        "Environment variables",
                        "CI/CD basics",
                        "Logging and monitoring"
                    ],
                    "activities": [
                        "Containerize application",
                        "Deploy to cloud",
                        "Set up GitHub Actions"
                    ],
                    "deliverable": "Deployed, production-ready API",
                    "prerequisites": ["be_m3_testing"],
                    "estimated_hours": 30,
                    "completion_criteria": [
                        "Application is live and accessible",
                        "CI/CD pipeline works",
                        "Proper logging in place"
                    ],
                    "assessment_method": "Deployment review",
                    "resources": [],
                    "status": MilestoneStatus.PENDING
                }
            ]
        }
    ]
}

# Data Scientist Roadmap (abbreviated for space)
DATA_SCIENTIST_TEMPLATE = {
    "role_key": "data_scientist",
    "template_name": "Data Scientist Learning Path",
    "version": "1.0.0",
    "starting_level": "beginner",
    "description": "Complete learning path to become a job-ready Data Scientist",
    "prerequisites": ["Basic Python", "Math fundamentals"],
    "estimated_duration_weeks": 20,
    "phases": [
        {
            "phase_id": "ds_phase_1",
            "phase_number": 1,
            "title": "Data Analysis Foundations",
            "description": "Master data manipulation and analysis",
            "objectives": [
                "Work with Pandas and NumPy",
                "Perform data analysis",
                "Visualize data effectively"
            ],
            "estimated_hours": 80,
            "prerequisites": [],
            "milestones": []  # Abbreviated for space
        }
    ]
}

# Template Registry
ROADMAP_TEMPLATES: Dict[str, Dict] = {
    "frontend_engineer": FRONTEND_ENGINEER_TEMPLATE,
    "backend_engineer": BACKEND_ENGINEER_TEMPLATE,
    "data_scientist": DATA_SCIENTIST_TEMPLATE,
    # Add more as needed
}


def get_template(role_key: str) -> Dict:
    """Get roadmap template for a role."""
    return ROADMAP_TEMPLATES.get(role_key)


def get_all_templates() -> List[Dict]:
    """Get all available roadmap templates."""
    return list(ROADMAP_TEMPLATES.values())


def validate_template(template: Dict) -> bool:
    """Validate template structure."""
    required_fields = ["role_key", "template_name", "version", "phases"]
    return all(field in template for field in required_fields)
