"""
Orvena Guide: Rule-Based Conversational Platform Assistant

Provides deterministic, intent-based guidance for students across
the Orvena platform without requiring any external LLM APIs.
Matches user queries to structured platform intents, provides rich
navigation actions to verified routes, and offers contextual suggestions.
"""
import re
from typing import List, Dict, Any, Optional
from app.schemas.guide import GuideChatRequest, GuideChatResponse, GuideNavigationAction


GUIDE_INTENTS: List[Dict[str, Any]] = [
    {
        "id": "GREETING",
        "keywords": ["hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "good evening", "howdy", "sup", "yo"],
        "patterns": [
            r"^(hi|hello|hey|hola|greetings|good morning|good afternoon|good evening|hey there|howdy|sup|yo)(\s+.*)?$",
            r"\b(i am|i'm|my name is|this is)\s+([a-zA-Z]+)\b",
            r"^who are you\??$",
            r"^how are you\??$",
        ],
        "confidence_base": 0.99,
        "reply": (
            "Hi {name}! 👋 Great to meet you! I'm **Orvena Guide**, your companion across the platform.\n\n"
            "Feel free to ask me any doubts about your engineering projects, how to choose an idea, milestone planning, "
            "project evaluation, or where to find student competitions and funding! What are you working on today?"
        ),
        "actions": [
            {"label": "Explore Project Ideas", "href": "/projects/discover", "description": "Curated engineering blueprints"},
            {"label": "Create Structured Plan", "href": "/projects/new", "description": "Turn your idea into milestones"},
            {"label": "Competitions & Grants", "href": "/projects/opportunities", "description": "Verified student opportunities"}
        ],
        "suggested_prompts": [
            "How do I choose the right project idea?",
            "How are project milestones tracked?",
            "Where can I find student hackathons?",
            "How does Project Outcome Intelligence work?"
        ]
    },
    {
        "id": "CHITCHAT",
        "keywords": ["thanks", "thank you", "cool", "awesome", "great", "nice", "appreciate it", "got it", "super", "ok", "okay", "alright"],
        "patterns": [
            r"^(thanks|thank you|cool|awesome|great|nice|perfect|got it|ok|okay|alright)(\s+.*)?$",
            r"\bthank(s| you)\b",
        ],
        "confidence_base": 0.96,
        "reply": (
            "You're very welcome, {name}! 🚀\n\n"
            "Remember, every milestone you complete in **Project Launchpad** builds tangible evidence for your portfolio and job matching. "
            "Let me know if you need any advice on your architecture, testing, or project outcomes!"
        ),
        "actions": [
            {"label": "My Projects", "href": "/projects", "description": "View active projects and milestones"},
            {"label": "Explore Opportunities", "href": "/projects/opportunities", "description": "Discover competitions & grants"}
        ],
        "suggested_prompts": [
            "How does Project Outcome Intelligence work?",
            "What makes a project stand out on a resume?",
            "How are projects evaluated?"
        ]
    },
    {
        "id": "PROJECT_DOUBTS",
        "keywords": ["doubt", "doubts", "confused", "which project", "what project", "how to choose", "stuck", "what should i build", "pick project", "beginner project", "best project", "help with project"],
        "patterns": [
            r"\b(doubt|doubts|confused|stuck|which project|what project|what should i (build|make|do)|how (to|do i) choose (a )?project)\b",
            r"\b(help with (my )?project|project idea doubts)\b",
        ],
        "confidence_base": 0.96,
        "reply": (
            "Having doubts about which project to build, {name}? Here is a proven way to choose:\n\n"
            "1. **Align with your target role:** If you want Backend/Cloud, build a distributed system with caching and queueing. If AI/ML, build an evaluated RAG or inference service with metrics.\n"
            "2. **Start with an MVP:** Pick 1 core problem and solve it deeply rather than building 10 shallow features.\n"
            "3. **Check Launchpad Ideas:** Our curated catalogue matches projects directly to your career interests and difficulty preferences.\n\n"
            "Would you like to browse project ideas matched to your skills?"
        ),
        "actions": [
            {"label": "Discover Project Ideas", "href": "/projects/discover", "description": "Browse role-aligned blueprints"},
            {"label": "Plan Your Own Idea", "href": "/projects/new", "description": "Generate an MVP plan"}
        ],
        "suggested_prompts": [
            "What makes a project stand out on a resume?",
            "How do project milestones work?",
            "What is an MVP scope?"
        ]
    },
    {
        "id": "GETTING_STARTED",
        "keywords": ["start", "begin", "getting started", "new here", "how does this work", "how does orvena work", "overview", "what is orvena", "help", "guide me", "tour"],
        "patterns": [r"\bhow (do|can) I start\b", r"\bwhere (should|do) I begin\b", r"\bwhat is orvena\b", r"\bhelp me get started\b", r"\bhow does (orvena|this) work\b", r"\bnew here\b"],
        "confidence_base": 0.95,
        "reply": (
            "Welcome to **ORVENA**! We help you build a high-trajectory career in tech through 4 integrated steps:\n\n"
            "1. **Career Discovery**: Complete a guided 5-stage assessment to uncover roles aligned with your natural strengths.\n"
            "2. **Project Launchpad**: Discover curated project ideas, plan MVPs, and evaluate your work across 5 engineering dimensions.\n"
            "3. **Resume Studio**: Score your resume with ATS compatibility checks and receive actionable bullet improvements.\n"
            "4. **Career Roadmap & Job Recommender**: Follow structured skill milestones and match with verified market opportunities."
        ),
        "actions": [
            {"label": "Start Career Discovery", "href": "/career/discovery", "description": "Find your best-fit career path"},
            {"label": "Explore Project Launchpad", "href": "/projects", "description": "Build high-impact projects"},
            {"label": "Analyze Resume", "href": "/resume", "description": "Check ATS and 6-factor score"}
        ],
        "suggested_prompts": [
            "How does Career Discovery work?",
            "What can I do in Project Launchpad?",
            "How do I analyze my resume?"
        ]
    },
    {
        "id": "CAREER_DISCOVERY",
        "keywords": ["career discovery", "pathfinder", "discover career", "career test", "career questionnaire", "ideal job", "interests assessment"],
        "patterns": [r"\bcareer discovery\b", r"\bfind my career\b", r"\bpathfinder\b", r"\bcareer quiz\b"],
        "confidence_base": 0.95,
        "reply": (
            "**Career Discovery (Pathfinder)** is an interactive assessment that evaluates your technical interests, "
            "core values, working preferences, and education background.\n\n"
            "• Generates tailored recommendations from over 50+ technology career profiles.\n"
            "• Provides realistic salary expectations and 5-year industry growth forecasts.\n"
            "• Powered by dual-layer AI with a guaranteed sub-8 second response and statistical fallback."
        ),
        "actions": [
            {"label": "Take Discovery Assessment", "href": "/career/discovery", "description": "Launch the interactive questionnaire"},
            {"label": "View Recommendations", "href": "/career/recommendations", "description": "Review generated career profiles"}
        ],
        "suggested_prompts": [
            "How are my career matches scored?",
            "Can I retake Career Discovery?",
            "How does this link to Project Launchpad?"
        ]
    },
    {
        "id": "RESUME_ANALYSIS",
        "keywords": ["resume", "cv", "ats", "resume score", "resume review", "upload resume", "format resume", "ats score"],
        "patterns": [r"\bresume\b", r"\bats\b", r"\bscore my cv\b", r"\bresume check\b"],
        "confidence_base": 0.95,
        "reply": (
            "**Resume Analyzer & ATS Scorer** examines your PDF/DOCX resume against 6 comprehensive engineering categories:\n\n"
            "1. **Completeness** (Contact info, summary, structure)\n"
            "2. **Work Experience** (Impact verbs, quantified metrics)\n"
            "3. **Education & Certifications**\n"
            "4. **Technical & Soft Skills**\n"
            "5. **Formatting & Hierarchy**\n"
            "6. **ATS Readability** (Applicant Tracking System parseability)\n\n"
            "You will receive an overall letter grade (A+ to F), identified strengths, and specific line-by-line recommendations."
        ),
        "actions": [
            {"label": "Upload Resume", "href": "/resume", "description": "Analyze a PDF or DOCX file"}
        ],
        "suggested_prompts": [
            "How can I improve my ATS score?",
            "Can I see past resume uploads?",
            "How do projects impact my resume score?"
        ]
    },
    {
        "id": "JOB_RECOMMENDATIONS",
        "keywords": ["jobs", "job openings", "job match", "job recommender", "swot", "salary", "hiring"],
        "patterns": [r"\bfind jobs\b", r"\bjob recommendations\b", r"\bswot analysis\b", r"\bmatched roles\b"],
        "confidence_base": 0.95,
        "reply": (
            "The **Job Recommender** utilizes a 5-factor deterministic matching algorithm:\n\n"
            "• **Skills Match** (40%)\n"
            "• **Education Alignment** (25%)\n"
            "• **Experience Level** (20%)\n"
            "• **Market Trend & Demand** (10%)\n"
            "• **Workplace Preferences** (5%)\n\n"
            "Every role includes a personalized **SWOT Analysis** highlighting your competitive Strengths, Weaknesses, Opportunities, and Threats."
        ),
        "actions": [
            {"label": "View Job Matches", "href": "/jobs", "description": "Explore personalized job matches and SWOT analysis"}
        ],
        "suggested_prompts": [
            "How is SWOT calculated for jobs?",
            "How do I bridge identified skill gaps?",
            "Show me roadmap recommendations"
        ]
    },
    {
        "id": "CAREER_ROADMAP",
        "keywords": ["roadmap", "milestone", "learning path", "timeline", "study plan", "goals", "skill milestones"],
        "patterns": [r"\broadmap\b", r"\bcareer plan\b", r"\blearning path\b", r"\bmilestones\b"],
        "confidence_base": 0.95,
        "reply": (
            "The **Career Roadmap** breaks your target role into actionable, step-by-step milestones:\n\n"
            "• **Short-Term (0-6 Months)**: Fundamental skill acquisition and hands-on projects.\n"
            "• **Long-Term (6-24 Months)**: System design, advanced domain architecture, and interview readiness.\n"
            "• Includes curated learning resources, project suggestions, and real-time completion tracking."
        ),
        "actions": [
            {"label": "Open Career Roadmap", "href": "/roadmap", "description": "Track active milestones and progress"}
        ],
        "suggested_prompts": [
            "How do I mark roadmap milestones completed?",
            "How do project milestones sync with my roadmap?"
        ]
    },
    {
        "id": "PROJECT_LAUNCHPAD_OVERVIEW",
        "keywords": ["launchpad", "project launchpad", "projects", "start a project", "build project", "portfolio project"],
        "patterns": [r"\bproject launchpad\b", r"\bprojects module\b", r"\bwhat is launchpad\b"],
        "confidence_base": 0.95,
        "reply": (
            "**Orvena Project Launchpad** is a project intelligence and development workspace:\n\n"
            "• **Journey A (Discover Ideas)**: Career-aware, rule-based recommendations tailored to your skills.\n"
            "• **Journey B (Develop & Track)**: Structured planning, phase boundaries, and milestone progress tracking.\n"
            "• **Journey C (5-Dimension Evaluation)**: Rigorous rubric scoring without an LLM.\n"
            "• **Outcome Intelligence**: Actionable next pathways (Product, Research, Startup, Competitions, Portfolio).\n"
            "• **Opportunities**: Source-backed directory of student hackathons, fellowships, and grants."
        ),
        "actions": [
            {"label": "Open Project Launchpad", "href": "/projects", "description": "Launchpad Central Hub"},
            {"label": "Discover Project Ideas", "href": "/projects/discover", "description": "Find career-aligned ideas"},
            {"label": "Plan a New Project", "href": "/projects/new", "description": "Structure your project plan"}
        ],
        "suggested_prompts": [
            "How do I evaluate my existing project?",
            "What is Project Outcome Intelligence?",
            "Where can I find student hackathons?"
        ]
    },
    {
        "id": "PROJECT_IDEA_DISCOVERY",
        "keywords": ["project ideas", "suggest project", "what project should I build", "idea discovery", "recommend project", "ideas"],
        "patterns": [r"\bproject ideas\b", r"\bwhat project\b", r"\brecommend an idea\b", r"\bfind an idea\b"],
        "confidence_base": 0.95,
        "reply": (
            "Project Launchpad includes a curated catalogue of 30+ real-world engineering project ideas across domains "
            "like AI/ML, Cloud & DevOps, HealthTech, ClimateTech, and Distributed Systems.\n\n"
            "• Each idea includes problem statements, prerequisites, expected deliverables, and learning outcomes.\n"
            "• Deterministically ranked based on your verified skills, target career roles, and weekly time budget."
        ),
        "actions": [
            {"label": "Discover Project Ideas", "href": "/projects/discover", "description": "Browse and filter tailored ideas"}
        ],
        "suggested_prompts": [
            "How does idea ranking work?",
            "Can I submit my own idea?",
            "Show me beginner project ideas"
        ]
    },
    {
        "id": "PROJECT_EVALUATION",
        "keywords": ["evaluate project", "project assessment", "project score", "review project", "rubric", "5 dimensions"],
        "patterns": [r"\bevaluate my project\b", r"\bproject evaluation\b", r"\bhow is project scored\b"],
        "confidence_base": 0.95,
        "reply": (
            "Projects are evaluated across **5 structured engineering dimensions** (0-20 points each, 100 max):\n\n"
            "1. **Problem Clarity & Relevance**: Defined personas, quantified friction.\n"
            "2. **Implementation Maturity**: Concept vs working MVP vs production standard.\n"
            "3. **Testing & Validation**: Unit tests, integration coverage, user trials.\n"
            "4. **Differentiation & Technical Substance**: Departure from tutorial boilerplate.\n"
            "5. **Documentation, Usability & Readiness**: Clean README, architecture diagram, demo link.\n\n"
            "Unanswered questions are handled as 'unknown' rather than failures, and you receive concrete improvement priorities."
        ),
        "actions": [
            {"label": "My Projects", "href": "/projects", "description": "Select a project to evaluate"}
        ],
        "suggested_prompts": [
            "What is Project Outcome Intelligence?",
            "How do I add a repository link safely?"
        ]
    },
    {
        "id": "PROJECT_OUTCOMES",
        "keywords": ["outcome intelligence", "what to do after project", "publish paper", "startup", "commercialize", "hackathon submission", "portfolio"],
        "patterns": [r"\boutcome intelligence\b", r"\bnext steps for my project\b", r"\bcan I publish my project\b", r"\bturn project into startup\b"],
        "confidence_base": 0.95,
        "reply": (
            "**Project Outcome Intelligence** analyzes mature projects to recommend one or more of 6 strategic pathways:\n\n"
            "• **Product Development**: Deployment, CI/CD, telemetry, and user onboarding.\n"
            "• **Research & Publication**: Related work, comparative baselines, and IEEE/ACM paper structure.\n"
            "• **Deep-Tech Innovation**: Unresolved scientific questions and faculty advisor consultations.\n"
            "• **Startup & Commercialisation**: Customer interviews, Lean Canvas, and incubator pitch deck.\n"
            "• **Competitions & Hackathons**: Pitch video, judging rubric alignment, and submission deadlines.\n"
            "• **Career & Portfolio**: STAR-format resume bullets and recruiter showcase packaging.\n\n"
            "You can convert any recommended pathway into active milestone tasks with a single click!"
        ),
        "actions": [
            {"label": "Go to Projects", "href": "/projects", "description": "View Outcome Intelligence on your project"}
        ],
        "suggested_prompts": [
            "Show me student competitions and grants",
            "How do I create a public showcase?"
        ]
    },
    {
        "id": "OPPORTUNITIES_DIRECTORY",
        "keywords": ["opportunities", "competitions", "hackathons", "grants", "funding", "incubators", "fellowships", "gsoc", "imagine cup"],
        "patterns": [r"\bopportunities\b", r"\bcompetitions\b", r"\bhackathons\b", r"\bgrants\b", r"\bfunding for students\b"],
        "confidence_base": 0.95,
        "reply": (
            "The **Orvena Opportunity Directory** tracks verified, source-backed programs for students:\n\n"
            "• **Global Competitions**: Microsoft Imagine Cup, Google Solution Challenge.\n"
            "• **Research Fellowships**: Google Summer of Code (GSoC), CERN Summer Student, MLH Fellowship.\n"
            "• **Student Grants**: 1517 Fund Medici Project ($1,000 non-dilutive maker grants).\n"
            "• **Incubators & Programs**: Y Combinator Startup School, collegiate hackathons.\n\n"
            "Every listing includes verified official URLs, real application deadlines, and clear eligibility criteria."
        ),
        "actions": [
            {"label": "Browse Opportunities", "href": "/projects/opportunities", "description": "Filter competitions, grants, and fellowships"}
        ],
        "suggested_prompts": [
            "Which opportunities have rolling deadlines?",
            "Are there non-monetary incubator programs?",
            "How do I track my applications?"
        ]
    },
    {
        "id": "PROFILE_MANAGEMENT",
        "keywords": ["profile", "skills", "education", "experience", "update skills", "add skills", "account info"],
        "patterns": [r"\bupdate profile\b", r"\badd skills\b", r"\bmy profile\b"],
        "confidence_base": 0.90,
        "reply": (
            "You can manage your academic background, verified technical skills, and career preferences in your **Student Profile**.\n\n"
            "Keeping your verified skills and education records up to date automatically sharpens your Job Matches and Project Launchpad recommendations!"
        ),
        "actions": [
            {"label": "View Profile", "href": "/profile", "description": "Manage skills, education, and credentials"},
            {"label": "Edit Profile", "href": "/profile/edit", "description": "Update profile details"}
        ],
        "suggested_prompts": [
            "Where do I see my overall career progress?",
            "How do I change account settings?"
        ]
    },
    {
        "id": "PROGRESS_TRACKING",
        "keywords": ["progress", "tracking", "readiness score", "analytics", "growth", "stats"],
        "patterns": [r"\bprogress\b", r"\btrack my progress\b", r"\bcareer readiness\b"],
        "confidence_base": 0.90,
        "reply": (
            "**Progress Tracking** aggregates your career journey into a unified view:\n\n"
            "• Overall Career Readiness Index\n"
            "• Resume scoring history and trajectory\n"
            "• Completed roadmap and project milestones\n"
            "• Active skill acquisitions over time"
        ),
        "actions": [
            {"label": "View Progress Dashboard", "href": "/progress", "description": "Inspect your career trajectory analytics"}
        ],
        "suggested_prompts": [
            "How do I increase my readiness score?",
            "Show me active roadmap milestones"
        ]
    },
    {
        "id": "ACCOUNT_SETTINGS",
        "keywords": ["settings", "account", "password", "theme", "dark mode", "email", "preferences"],
        "patterns": [r"\bsettings\b", r"\bchange password\b", r"\baccount settings\b"],
        "confidence_base": 0.90,
        "reply": (
            "You can configure your account settings, visual appearance, and notification preferences on the **Settings** page."
        ),
        "actions": [
            {"label": "Settings", "href": "/settings", "description": "Account and display preferences"}
        ],
        "suggested_prompts": [
            "How do I get help and support?",
            "Where can I find documentation?"
        ]
    }
]


class OrvenaGuideEngine:
    """Rule-based conversational assistant engine."""

    def __init__(self, intents: List[Dict[str, Any]] = None):
        self.intents = intents or GUIDE_INTENTS

    def process_query(self, request: GuideChatRequest) -> GuideChatResponse:
        """
        Processes student input deterministically:
        1. Normalizes input text
        2. Evaluates regex patterns and keyword density
        3. Considers current page context to break ties
        4. Returns structured response with verified navigation actions
        """
        user_text = request.message.strip().lower()
        current_path = (request.current_path or "").lower()

        best_intent: Optional[Dict[str, Any]] = None
        best_score = 0.0

        for intent in self.intents:
            score = 0.0

            # 1. Regex pattern match (high confidence)
            for pattern in intent.get("patterns", []):
                if re.search(pattern, user_text, re.IGNORECASE):
                    score += 0.60
                    break

            # 2. Keyword matching
            matched_keywords = 0
            for kw in intent.get("keywords", []):
                if kw.lower() in user_text:
                    matched_keywords += 1

            if matched_keywords > 0:
                score += min(0.40, matched_keywords * 0.15)

            # 3. Contextual boost if user is on the relevant page
            if "project" in intent["id"].lower() and "/project" in current_path:
                score += 0.10
            elif "resume" in intent["id"].lower() and "/resume" in current_path:
                score += 0.10
            elif "career" in intent["id"].lower() and "/career" in current_path:
                score += 0.10
            elif "job" in intent["id"].lower() and "/job" in current_path:
                score += 0.10

            if score > best_score:
                best_score = score
                best_intent = intent

        # Extract user's name if mentioned in text or passed in request
        name = "there"
        if request.user_name and request.user_name.strip():
            name = request.user_name.strip()
        
        name_match = re.search(r"\b(?:i am|i'm|my name is|this is)\s+([a-zA-Z]+)\b", user_text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).capitalize()

        # Decision threshold (0.25)
        if best_intent and best_score >= 0.25:
            confidence = min(1.0, round(best_score, 2))
            actions = [
                GuideNavigationAction(
                    label=a["label"],
                    href=a["href"],
                    description=a.get("description")
                )
                for a in best_intent.get("actions", [])
            ]
            formatted_reply = best_intent["reply"].replace("{name}", name)
            return GuideChatResponse(
                reply=formatted_reply,
                matched_intent=best_intent["id"],
                confidence=confidence,
                suggested_actions=actions,
                suggested_prompts=best_intent.get("suggested_prompts", []),
                context_hint=f"Matched: {best_intent['id']} (Confidence: {int(confidence*100)}%)"
            )

        # Fallback for unknown or ambiguous queries
        fallback_reply = (
            f"I'm **Orvena Guide**, your rule-based platform assistant, {name}. I couldn't find an exact match for your question, "
            "but I can help you navigate any part of Orvena! Here are the core areas you can explore:"
        )
        default_actions = [
            GuideNavigationAction(label="Career Discovery", href="/career/discovery", description="Take the assessment"),
            GuideNavigationAction(label="Project Launchpad", href="/projects", description="Explore ideas & track projects"),
            GuideNavigationAction(label="Resume Analyzer", href="/resume", description="Upload and score resume"),
            GuideNavigationAction(label="Job Recommender", href="/jobs", description="Personalized job matches")
        ]
        default_prompts = [
            "How do I start with Career Discovery?",
            "What project ideas are available?",
            "How does Resume scoring work?",
            "Where are student competitions and grants?"
        ]

        return GuideChatResponse(
            reply=fallback_reply,
            matched_intent="UNKNOWN_FALLBACK",
            confidence=0.10,
            suggested_actions=default_actions,
            suggested_prompts=default_prompts,
            context_hint="Query unrecognized. Displaying platform guide topics."
        )


orvena_guide_engine = OrvenaGuideEngine()
