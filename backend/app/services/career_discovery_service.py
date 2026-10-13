"""Service layer for career discovery functionality."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.student import StudentProfile, StudentSkill, EducationRecord, Project
from app.db.models.career import (
    CareerDiscoverySession,
    CareerDiscoveryResponse,
    CareerGoal,
    CareerRecommendation,
    CareerRole,
)
from app.schemas.career import (
    CareerDiscoverySessionCreate,
    CareerDiscoverySessionUpdate,
    CareerDiscoveryResponseCreate,
    CareerGoalCreate,
)
from app.services.llm import get_llm_provider, LLMMessage
from app.core.exceptions import NotFoundError, ValidationError


class CareerDiscoveryService:
    """Service for career discovery and recommendations."""

    DISCOVERY_SYSTEM_PROMPT = """You are an expert career advisor helping students discover their ideal career path. 
Your role is to:
1. Ask thoughtful, personalized questions to understand the student's interests, skills, values, and goals
2. Build on previous responses to go deeper
3. Be encouraging and supportive
4. Help students think about careers they might not have considered
5. Keep questions conversational and engaging
6. Mix question types: Multiple Choice Questions (MCQs) and Descriptive Questions

IMPORTANT: Generate a MIX of question types:
- Questions 1, 3, 5, 7, 9: Multiple Choice Questions (provide 4 options labeled A, B, C, D)
- Questions 2, 4, 6, 8, 10: Open-ended Descriptive Questions

For MCQ questions, format them as:
[Question text]

A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]

For descriptive questions, ask open-ended questions that require detailed responses.

Guidelines:
- Ask ONE question at a time
- Make questions specific and actionable
- Reference their previous answers to show you're listening
- Avoid jargon or overly formal language
- Help them explore both their strengths and interests
- Consider their background (education, skills, projects) when relevant
- Focus on HIGH-GROWTH industries (AI/ML, Cloud, Data Science, Cybersecurity, Full-Stack Development)

Current conversation context will be provided. Generate the next question to continue the discovery process."""

    # Discovery question categories
    QUESTION_CATEGORIES = [
        "interests",
        "strengths",
        "values",
        "work_style",
        "goals",
        "constraints",
    ]

    # Static MCQ questions - TWO PATHWAYS
    # Pathway 1: For students with NO clear career direction
    QUESTIONS_NO_IDEA = [
        {
            "number": 1,
            "type": "mcq",
            "question": "What subjects or activities did you enjoy most during your studies?",
            "options": {
                "A": "Mathematics, Statistics, and Data Analysis",
                "B": "Programming, Building Applications, and Software Development",
                "C": "Computer Networks, Systems, and Infrastructure",
                "D": "Problem-solving, Logic Puzzles, and Algorithms"
            }
        },
        {
            "number": 2,
            "type": "mcq",
            "question": "Which of these work environments appeals to you most?",
            "options": {
                "A": "Fast-paced startup with rapid innovation and learning",
                "B": "Established tech company with structured processes",
                "C": "Remote-first company with flexible work arrangements",
                "D": "Collaborative office environment with team interactions"
            }
        },
        {
            "number": 3,
            "type": "mcq",
            "question": "What type of problems do you find most interesting to solve?",
            "options": {
                "A": "Analyzing data patterns and extracting insights",
                "B": "Building user-facing applications and features",
                "C": "Optimizing system performance and scalability",
                "D": "Protecting systems and preventing security threats"
            }
        },
        {
            "number": 4,
            "type": "mcq",
            "question": "Which technology area excites you the most?",
            "options": {
                "A": "Artificial Intelligence and Machine Learning",
                "B": "Cloud Computing (AWS, Azure, GCP)",
                "C": "Mobile App Development (iOS, Android)",
                "D": "Web Development (React, Angular, Vue)"
            }
        },
        {
            "number": 5,
            "type": "mcq",
            "question": "What is your preferred learning style?",
            "options": {
                "A": "Reading documentation and technical articles",
                "B": "Watching video tutorials and online courses",
                "C": "Building projects and learning by doing",
                "D": "Collaborating with others and pair programming"
            }
        },
        {
            "number": 6,
            "type": "mcq",
            "question": "Which of these technical roles sounds most appealing?",
            "options": {
                "A": "Data Scientist - Analyzing data and building predictive models",
                "B": "Full-Stack Developer - Building complete web applications",
                "C": "DevOps Engineer - Managing infrastructure and deployments",
                "D": "Cybersecurity Analyst - Protecting systems from threats"
            }
        },
        {
            "number": 7,
            "type": "mcq",
            "question": "What motivates you most in your career?",
            "options": {
                "A": "High salary and financial growth ($100K+ annually)",
                "B": "Continuous learning and skill development",
                "C": "Making meaningful impact on users/society",
                "D": "Work-life balance and flexible schedule"
            }
        },
        {
            "number": 8,
            "type": "mcq",
            "question": "Which programming paradigm do you prefer or want to learn?",
            "options": {
                "A": "Data-focused (Python, R, SQL for analytics)",
                "B": "Web-focused (JavaScript, TypeScript, React)",
                "C": "Systems-focused (Go, Rust, C++ for infrastructure)",
                "D": "General purpose (Java, C#, Python for various uses)"
            }
        },
        {
            "number": 9,
            "type": "mcq",
            "question": "How do you prefer to work on projects?",
            "options": {
                "A": "Independently with full ownership",
                "B": "In small teams (2-4 people)",
                "C": "In larger teams with specialized roles",
                "D": "Mix of solo and collaborative work"
            }
        },
        {
            "number": 10,
            "type": "mcq",
            "question": "What type of company size interests you?",
            "options": {
                "A": "Startup (< 50 employees) - High growth, wear many hats",
                "B": "Mid-size (50-500 employees) - Balanced growth and structure",
                "C": "Large enterprise (500+ employees) - Stability and resources",
                "D": "No preference - Open to any size"
            }
        },
        {
            "number": 11,
            "type": "mcq",
            "question": "Which industry sector interests you most?",
            "options": {
                "A": "FinTech - Financial services and payments",
                "B": "HealthTech - Healthcare and medical technology",
                "C": "E-commerce - Online retail and marketplaces",
                "D": "Enterprise SaaS - Business software solutions"
            }
        },
        {
            "number": 12,
            "type": "mcq",
            "question": "What is your current skill level in programming?",
            "options": {
                "A": "Beginner - Just starting to learn",
                "B": "Intermediate - Built a few projects",
                "C": "Advanced - Built multiple complex projects",
                "D": "Expert - Professional experience or deep expertise"
            }
        },
        {
            "number": 13,
            "type": "mcq",
            "question": "How important is remote work to you?",
            "options": {
                "A": "Essential - Only interested in fully remote positions",
                "B": "Preferred - Would like remote but open to hybrid",
                "C": "Flexible - Open to remote, hybrid, or office",
                "D": "Prefer office - Like in-person collaboration"
            }
        },
        {
            "number": 14,
            "type": "mcq",
            "question": "What is your timeline to start your career?",
            "options": {
                "A": "Immediate - Ready to start now",
                "B": "3-6 months - Need some preparation time",
                "C": "6-12 months - Currently building skills",
                "D": "1+ years - Long-term planning"
            }
        },
        {
            "number": 15,
            "type": "mcq",
            "question": "What is most important to you in your first role?",
            "options": {
                "A": "Strong mentorship and learning opportunities",
                "B": "Competitive salary ($75K+ annually)",
                "C": "Modern tech stack and cutting-edge projects",
                "D": "Good work-life balance and company culture"
            }
        },
        {
            "number": 16,
            "type": "descriptive",
            "question": "Tell us about yourself - your background, interests, any projects you've worked on, and what you're looking for in your career. Be as detailed as you'd like.",
            "options": None
        }
    ]
    
    # Pathway 2: For students with CLEAR career direction
    QUESTIONS_HAS_IDEA = [
        {
            "number": 1,
            "type": "mcq",
            "question": "Which career path are you most interested in pursuing?",
            "options": {
                "A": "Software Engineering / Full-Stack Development",
                "B": "Data Science / Machine Learning Engineer",
                "C": "DevOps / Cloud Engineer",
                "D": "Cybersecurity / Security Engineer"
            }
        },
        {
            "number": 2,
            "type": "mcq",
            "question": "What is your current experience level in your chosen field?",
            "options": {
                "A": "No experience - Just starting to learn",
                "B": "Some coursework - Completed online courses or classes",
                "C": "Personal projects - Built 1-3 projects",
                "D": "Significant experience - Multiple projects or internships"
            }
        },
        {
            "number": 3,
            "type": "mcq",
            "question": "Which specific technology stack are you focusing on?",
            "options": {
                "A": "MERN/MEAN (MongoDB, Express, React/Angular, Node.js)",
                "B": "Python ecosystem (Django, Flask, FastAPI, Data Science)",
                "C": "Cloud platforms (AWS, Azure, GCP, Kubernetes)",
                "D": "Mobile development (React Native, Flutter, iOS, Android)"
            }
        },
        {
            "number": 4,
            "type": "mcq",
            "question": "What is your biggest challenge in pursuing this career?",
            "options": {
                "A": "Lack of real-world project experience",
                "B": "Not sure which specific skills to focus on",
                "C": "Building a strong portfolio to showcase skills",
                "D": "Finding the right job opportunities"
            }
        },
        {
            "number": 5,
            "type": "mcq",
            "question": "What type of projects have you worked on (or want to work on)?",
            "options": {
                "A": "Web applications (E-commerce, Social media, SaaS)",
                "B": "Data analysis and ML models (Predictions, Analytics)",
                "C": "Infrastructure and automation (CI/CD, Cloud deployment)",
                "D": "Mobile apps or APIs"
            }
        },
        {
            "number": 6,
            "type": "mcq",
            "question": "What is your target salary range for your first role?",
            "options": {
                "A": "$60K-$80K annually",
                "B": "$80K-$100K annually",
                "C": "$100K-$120K annually",
                "D": "$120K+ annually"
            }
        },
        {
            "number": 7,
            "type": "mcq",
            "question": "Which certifications are you planning to pursue (or have)?",
            "options": {
                "A": "AWS/Azure/GCP Cloud Certifications",
                "B": "None - Focusing on building projects",
                "C": "Data Science / ML certifications (Coursera, DataCamp)",
                "D": "Security certifications (CompTIA, CISSP)"
            }
        },
        {
            "number": 8,
            "type": "mcq",
            "question": "What is your preferred company type for this role?",
            "options": {
                "A": "Tech giants (Google, Microsoft, Amazon)",
                "B": "High-growth startups (Series A-C funded)",
                "C": "Established tech companies (Mid-size, profitable)",
                "D": "Remote-first companies (Any size, fully remote)"
            }
        },
        {
            "number": 9,
            "type": "mcq",
            "question": "How are you currently building your skills?",
            "options": {
                "A": "Online courses (Udemy, Coursera, Pluralsight)",
                "B": "Building personal projects and portfolio",
                "C": "Contributing to open source projects",
                "D": "Bootcamp or formal degree program"
            }
        },
        {
            "number": 10,
            "type": "mcq",
            "question": "What specific area do you want to specialize in?",
            "options": {
                "A": "Frontend (React, Vue, Angular, UI/UX)",
                "B": "Backend (APIs, Databases, Microservices)",
                "C": "Full-Stack (Both frontend and backend)",
                "D": "Specialized (ML, DevOps, Security, Mobile)"
            }
        },
        {
            "number": 11,
            "type": "mcq",
            "question": "Which programming languages are you most comfortable with?",
            "options": {
                "A": "JavaScript/TypeScript",
                "B": "Python",
                "C": "Java/C#/Go",
                "D": "Multiple languages (Polyglot developer)"
            }
        },
        {
            "number": 12,
            "type": "mcq",
            "question": "What is your approach to learning new technologies?",
            "options": {
                "A": "Build projects immediately and learn by doing",
                "B": "Take structured courses first, then build",
                "C": "Read documentation and tutorials thoroughly",
                "D": "Learn from others (mentorship, pair programming)"
            }
        },
        {
            "number": 13,
            "type": "mcq",
            "question": "What type of work environment do you prefer?",
            "options": {
                "A": "Fully remote - Work from anywhere",
                "B": "Hybrid - 2-3 days office, rest remote",
                "C": "Full-time office - Prefer in-person collaboration",
                "D": "Flexible - Open to any arrangement"
            }
        },
        {
            "number": 14,
            "type": "mcq",
            "question": "What is your plan for the next 3-6 months?",
            "options": {
                "A": "Actively applying for jobs now",
                "B": "Building portfolio projects before applying",
                "C": "Completing certifications or courses",
                "D": "Gaining more hands-on experience"
            }
        },
        {
            "number": 15,
            "type": "mcq",
            "question": "What resources do you need most to reach your goal?",
            "options": {
                "A": "Project ideas and technical guidance",
                "B": "Resume and interview preparation",
                "C": "Networking and job search strategies",
                "D": "Skill development roadmap"
            }
        },
        {
            "number": 16,
            "type": "descriptive",
            "question": "Tell us about yourself - your background, why you chose this career path, what you've learned so far, and what your specific career goals are. Be as detailed as you'd like.",
            "options": None
        }
    ]

    async def create_session(
        self, db: AsyncSession, profile_id: UUID, session_data: CareerDiscoverySessionCreate
    ) -> CareerDiscoverySession:
        """Create a session only when the student has no resumable session."""
        # Serialize creation per profile. This also protects against duplicate
        # initialization calls from browser development-mode effect replay.
        await db.execute(
            select(StudentProfile.id)
            .where(StudentProfile.id == profile_id)
            .with_for_update()
        )
        existing_result = await db.execute(
            select(CareerDiscoverySession).where(
                CareerDiscoverySession.student_profile_id == profile_id,
                CareerDiscoverySession.status == "in_progress",
            ).options(selectinload(CareerDiscoverySession.responses))
            .order_by(CareerDiscoverySession.created_at.desc())
            .limit(1)
        )
        existing_session = existing_result.scalars().first()
        if existing_session:
            return existing_session

        # Earlier versions abandoned active sessions during duplicate page
        # initialization. Recover the session that already contains answers
        # instead of making the student repeat them.
        abandoned_result = await db.execute(
            select(CareerDiscoverySession)
            .where(
                CareerDiscoverySession.student_profile_id == profile_id,
                CareerDiscoverySession.status == "abandoned",
            )
            .options(selectinload(CareerDiscoverySession.responses))
            .order_by(CareerDiscoverySession.created_at.desc())
        )
        resumable = max(
            abandoned_result.scalars().all(),
            key=lambda item: (len(item.responses), item.created_at),
            default=None,
        )
        if resumable and 0 < len(resumable.responses) < 10:
            resumable.status = "in_progress"
            resumable.updated_at = datetime.utcnow()
            await db.commit()
            return resumable

        session = CareerDiscoverySession(
            student_profile_id=profile_id,
            session_type=session_data.session_type,
            status="in_progress",
            current_phase="initial",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session, attribute_names=["responses"])  # Explicitly load responses
        return session

    async def get_session(
        self, db: AsyncSession, session_id: UUID, profile_id: UUID
    ) -> Optional[CareerDiscoverySession]:
        """Get a specific session."""
        result = await db.execute(
            select(CareerDiscoverySession)
            .where(
                CareerDiscoverySession.id == session_id,
                CareerDiscoverySession.student_profile_id == profile_id,
            )
            .options(selectinload(CareerDiscoverySession.responses))
        )
        return result.scalar_one_or_none()

    async def get_sessions(
        self, db: AsyncSession, profile_id: UUID
    ) -> List[CareerDiscoverySession]:
        """Get all sessions for a profile."""
        result = await db.execute(
            select(CareerDiscoverySession)
            .where(CareerDiscoverySession.student_profile_id == profile_id)
            # The response schema includes each session's answers. Load this
            # relationship in the async query instead of triggering lazy IO
            # during Pydantic serialization (which raises MissingGreenlet).
            .options(selectinload(CareerDiscoverySession.responses))
            .order_by(CareerDiscoverySession.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_session(
        self, db: AsyncSession, profile_id: UUID
    ) -> Optional[CareerDiscoverySession]:
        """Return the session with the most saved answers so progress is retained."""
        result = await db.execute(
            select(CareerDiscoverySession)
            .where(
                CareerDiscoverySession.student_profile_id == profile_id,
                CareerDiscoverySession.status.in_(["in_progress", "abandoned", "completed"]),
            )
            .options(selectinload(CareerDiscoverySession.responses))
            .order_by(CareerDiscoverySession.created_at.desc())
        )
        sessions = list(result.scalars().all())
        if not sessions:
            return None

        # Prefer the newest active session so answers from a new discovery
        # run supersede an older completed run for this account. If no active
        # run exists, reopen the most complete saved session/result.
        active_sessions = [item for item in sessions if item.status == "in_progress"]
        session = max(active_sessions, key=lambda item: item.created_at) if active_sessions else max(
            sessions,
            key=lambda item: (len(item.responses), item.created_at),
        )
        if session.status == "abandoned" and 0 < len(session.responses) < 10:
            session.status = "in_progress"
            session.updated_at = datetime.utcnow()
            await db.commit()
        return session

    async def get_student_context(
        self, db: AsyncSession, profile_id: UUID
    ) -> Dict[str, Any]:
        """Get student context for personalized questions."""
        # Get profile
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.id == profile_id)
        )
        profile = profile_result.scalar_one_or_none()

        # Get education
        education_result = await db.execute(
            select(EducationRecord)
            .where(EducationRecord.student_profile_id == profile_id)
            .order_by(EducationRecord.start_date.desc())
        )
        education = list(education_result.scalars().all())

        # Get skills
        skills_result = await db.execute(
            select(StudentSkill)
            .where(StudentSkill.student_profile_id == profile_id)
            .options(selectinload(StudentSkill.skill))
        )
        skills = list(skills_result.scalars().all())

        # Get projects
        projects_result = await db.execute(
            select(Project)
            .where(Project.student_profile_id == profile_id)
            .order_by(Project.start_date.desc())
        )
        projects = list(projects_result.scalars().all())

        return {
            "profile": profile,
            "education": education,
            "skills": skills,
            "projects": projects,
        }

    async def generate_next_question(
        self,
        db: AsyncSession,
        session: CareerDiscoverySession,
        profile_id: UUID,
    ) -> Dict[str, Any]:
        """Generate the next discovery question using STATIC questions (no LLM calls to save quota)."""
        
        # Count answers, not the question's old display index. The opening
        # pathway question is question 1 and is stored with sequence_number 1.
        question_number = len(session.responses) + 1
        
        # Determine which question set to use based on session type or first answer
        use_has_idea_questions = False
        
        # If first question, ask which pathway
        if question_number == 1:
            # Always start with pathway selection
            return {
                "question_number": 1,
                "question_text": "Do you have a clear idea of which career path you want to pursue?",
                "question_type": "pathway_selection",
                "options": {
                    "A": "Yes - I know which career I want (e.g., Software Engineer, Data Scientist)",
                    "B": "No - I'm exploring different options and need guidance"
                }
            }
        
        # Check first response to determine pathway
        if session.responses:
            first_response = session.responses[0]
            if "A)" in first_response.response_text or "yes" in first_response.response_text.lower():
                use_has_idea_questions = True
        
        # Select appropriate question set
        questions = self.QUESTIONS_HAS_IDEA if use_has_idea_questions else self.QUESTIONS_NO_IDEA
        
        # Get question (adjust for 0-indexed after pathway question)
        question_index = question_number - 2  # The first question selects a pathway.
        
        if question_index < 0 or question_index >= len(questions):
            # Return a generic final question if out of range
            return {
                "question_number": question_number,
                "question_text": "Is there anything else you'd like to share about your career goals or background?",
                "question_type": "descriptive",
                "options": None
            }
        
        question_data = questions[question_index]
        
        return {
            "question_number": question_number,
            "question_text": question_data["question"],
            "question_type": question_data["type"],
            "options": question_data.get("options")
        }

    async def add_response(
        self,
        db: AsyncSession,
        session_id: UUID,
        profile_id: UUID,
        response_data: CareerDiscoveryResponseCreate,
    ) -> CareerDiscoveryResponse:
        """Add a response to a discovery session."""
        session = await self.get_session(db, session_id, profile_id)
        if not session:
            raise NotFoundError("Discovery session not found")

        if session.status != "in_progress":
            raise ValidationError("Session is not active")

        # Create response
        response = CareerDiscoveryResponse(
            session_id=session_id,
            sequence_number=response_data.sequence_number,
            question_text=response_data.question_text,
            response_text=response_data.response_text,
            question_category=response_data.question_category,
            phase=response_data.phase,
        )
        db.add(response)

        # Update session
        session.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(response)
        return response

    async def complete_session(
        self,
        db: AsyncSession,
        session_id: UUID,
        profile_id: UUID,
    ) -> CareerDiscoverySession:
        """Mark a discovery session as completed."""
        session = await self.get_session(db, session_id, profile_id)
        if not session:
            raise NotFoundError("Discovery session not found")

        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(session)
        return session

    async def analyze_responses(
        self,
        db: AsyncSession,
        session_id: UUID,
        profile_id: UUID,
    ) -> Dict[str, Any]:
        """Analyze discovery session responses to generate detailed career report with industry analysis."""
        session = await self.get_session(db, session_id, profile_id)
        if not session:
            raise NotFoundError("Discovery session not found")

        if not session.responses:
            return {"insights": [], "themes": [], "summary": ""}

        llm = get_llm_provider()
        
        # Get student context for comprehensive analysis
        context = await self.get_student_context(db, profile_id)

        # Build conversation for analysis
        conversation = []
        for resp in session.responses:
            conversation.append(f"Q: {resp.question_text}")
            conversation.append(f"A: {resp.response_text}")

        conversation_text = "\n".join(conversation)
        
        # Build student profile summary
        profile_summary = ""
        if context["profile"]:
            profile_summary += f"Name: {context['profile'].full_name}\n"
            if context["profile"].bio:
                profile_summary += f"Bio: {context['profile'].bio}\n"
        
        if context["education"]:
            edu = context["education"][0]
            profile_summary += f"Education: {edu.degree} in {edu.field_of_study} from {edu.institution_name}\n"
        
        if context["skills"]:
            skill_names = [s.skill.name for s in context["skills"] if s.skill]
            profile_summary += f"Skills: {', '.join(skill_names)}\n"
        
        if context["projects"]:
            profile_summary += f"Projects: {len(context['projects'])} completed\n"

        # Try AI analysis first
        try:
            import asyncio
            # Comprehensive analysis prompt
            analysis_prompt = """You are a senior career advisor creating a DETAILED CAREER DISCOVERY REPORT with comprehensive industry analysis.

Analyze the student's profile and discovery conversation to create a professional career report that includes:

1. **Executive Summary** (2-3 paragraphs)
   - Overview of student's background, strengths, and career direction
   - Key findings from the discovery session
   
2. **Student Profile Analysis**
   - Core interests and passions
   - Technical strengths and skills
   - Values and work priorities
   - Preferred work style and environment
   
3. **Career Fit Assessment**
   - Top 3-5 recommended career paths
   - Fit score and reasoning for each
   - Required skills vs current skills gap analysis
   
4. **Industry Analysis & Market Trends** (DETAILED)
   - Current state of recommended industries (AI/ML, Cloud, Data Science, Cybersecurity, etc.)
   - Market growth projections and demand outlook
   - Emerging technologies and opportunities
   - Salary expectations and compensation trends ($75K+ focus)
   - Geographic hotspots and remote opportunities
   
5. **Development Roadmap**
   - Skills to develop in next 6 months
   - Recommended certifications and courses
   - Project ideas to build portfolio
   - Networking and community engagement strategies
   
6. **Career Goals & Timeline**
   - Short-term goals (0-12 months)
   - Medium-term goals (1-3 years)
   - Long-term vision (3-5 years)

Return the analysis as a structured JSON object with these keys:
{
  "executive_summary": "string",
  "interests": ["interest1", "interest2"],
  "strengths": ["strength1", "strength2"],
  "values": ["value1", "value2"],
  "work_style": "string description",
  "career_paths": [
    {
      "role": "Career Role Name",
      "fit_score": 0.85,
      "reasoning": "Why this is a good fit",
      "salary_range": "$80,000 - $150,000 annually",
      "growth_outlook": "15% annual growth through 2027"
    }
  ],
  "industry_analysis": {
    "current_trends": ["trend1", "trend2"],
    "emerging_technologies": ["tech1", "tech2"],
    "market_demand": "High demand description",
    "salary_trends": "Salary market analysis",
    "geographic_opportunities": ["location1", "location2"]
  },
  "skill_gaps": ["gap1", "gap2"],
  "development_plan": {
    "short_term": ["action1", "action2"],
    "certifications": ["cert1", "cert2"],
    "projects": ["project1", "project2"],
    "networking": ["strategy1", "strategy2"]
  },
  "goals": {
    "short_term": ["goal1", "goal2"],
    "medium_term": ["goal1", "goal2"],
    "long_term": ["goal1", "goal2"]
  },
  "summary": "Brief 2-3 sentence summary"
}

Focus on HIGH-PAYING ($75K+) roles in BOOMING industries (AI/ML, Cloud, Cybersecurity, Data Science, DevOps, Full-Stack)."""

            user_message = f"""Student Profile:
{profile_summary}

Discovery Conversation:
{conversation_text}

Generate a comprehensive career discovery report with detailed industry analysis."""

            response = await asyncio.wait_for(
                llm.generate_with_system(
                    system_prompt=analysis_prompt,
                    user_message=user_message,
                    temperature=0.6,
                    max_tokens=2500,
                ),
                timeout=12.0,
            )

            # Parse response
            import re
            import json
            
            try:
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    return {
                        "analysis": analysis_data,
                        "raw_analysis": response.content,
                        "conversation": conversation_text,
                    }
            except Exception as e:
                print(f"JSON parsing error in analyze_responses: {str(e)}")
                # Fallback: return raw analysis
                pass
            
            return {
                "raw_analysis": response.content,
                "conversation": conversation_text,
                "summary": "Career analysis completed. Review the detailed report above."
            }
        except Exception as e:
            print(f"AI analysis failed: {str(e)}. Using fallback analysis.")
            # Fallback: Basic statistical analysis
            return self._fallback_analysis(conversation_text, context)
    
    def _fallback_analysis(self, conversation_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic analysis when AI fails."""
        # Extract keywords and patterns from conversation
        interests = []
        skills = []
        
        # Get skills from context
        if context.get("skills"):
            skills = [s.skill.name for s in context["skills"]][:10]
        
        # Basic analysis based on conversation length and content
        words = conversation_text.lower().split()
        
        # Detect interests from common keywords
        tech_keywords = {"ai", "machine learning", "data", "cloud", "development", "coding", "programming"}
        business_keywords = {"management", "business", "strategy", "leadership"}
        creative_keywords = {"design", "creative", "user experience", "ui", "ux"}
        
        for keyword in tech_keywords:
            if keyword in words:
                interests.append("Technology & Engineering")
                break
        for keyword in business_keywords:
            if keyword in words:
                interests.append("Business & Management")
                break
        for keyword in creative_keywords:
            if keyword in words:
                interests.append("Design & Creativity")
                break
        
        # If no interests detected, use generic ones
        if not interests:
            interests = ["Technology", "Problem Solving", "Innovation"]
        
        return {
            "analysis": {
                "executive_summary": "Career discovery session completed successfully. Based on your responses, we've identified key areas of interest and potential career paths.",
                "interests": interests,
                "strengths": skills[:5] if skills else ["Analytical thinking", "Problem solving", "Communication"],
                "values": ["Growth", "Innovation", "Impact"],
                "work_style": "Collaborative and goal-oriented",
                "career_paths": [
                    {
                        "role": "Software Engineer",
                        "fit_score": 0.80,
                        "reasoning": "Strong technical background with interest in technology",
                        "salary_range": "$80,000 - $150,000",
                        "growth_outlook": "Strong growth expected"
                    },
                    {
                        "role": "Data Analyst",
                        "fit_score": 0.75,
                        "reasoning": "Analytical skills and interest in data-driven decisions",
                        "salary_range": "$70,000 - $130,000",
                        "growth_outlook": "High demand across industries"
                    }
                ],
                "skill_gaps": ["Cloud technologies", "Advanced analytics"],
                "development_plan": {
                    "short_term": ["Complete online courses", "Build portfolio projects"],
                    "certifications": ["AWS Solutions Architect", "Google Analytics"],
                    "projects": ["Personal portfolio website", "Data visualization dashboard"],
                    "networking": ["Join tech meetups", "Contribute to open source"]
                },
                "goals": {
                    "short_term": ["Enhance technical skills", "Build professional network"],
                    "medium_term": ["Land first role in target field", "Gain industry experience"],
                    "long_term": ["Become subject matter expert", "Lead technical teams"]
                },
                "summary": "You have strong potential in technology roles. Focus on building practical experience and expanding your technical toolkit."
            },
            "conversation": conversation_text,
            "fallback_used": True,
            "summary": "Career analysis completed using statistical methods."
        }


# Singleton instance
career_discovery_service = CareerDiscoveryService()
