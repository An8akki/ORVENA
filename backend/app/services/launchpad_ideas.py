"""
Orvena Project Launchpad: Idea Catalogue & Recommendation Engine

Provides a curated, extensible catalogue of real-world project ideas
and deterministic, rule-based matching based on student skills,
career discovery results, time availability, and objectives.
"""
from typing import List, Dict, Any, Optional
from app.schemas.launchpad import ProjectIdea, MilestoneTemplate, IdeaRecommendationRequest


PROJECT_IDEAS_CATALOGUE: List[Dict[str, Any]] = [
    {
        "id": "fullstack-ai-search-engine",
        "title": "Semantic Document Search & Synthesis Platform",
        "problem_statement": "Students and researchers struggle to rapidly search through heterogeneous technical PDF papers and extract verifiable citations.",
        "intended_users": "University students, academic researchers, and domain analysts.",
        "domain": "AI / Machine Learning",
        "difficulty": "intermediate",
        "prerequisites": ["Python", "Basic Vector Math", "REST APIs", "Modern JavaScript / React"],
        "recommended_technologies": ["FastAPI", "Next.js", "PostgreSQL (pgvector)", "SentenceTransformers", "Tailwind CSS"],
        "estimated_duration_weeks": 8,
        "weekly_hours": 10,
        "expected_deliverables": [
            "Interactive web app with PDF upload and drag-and-drop parsing",
            "Vector-based semantic search with cosine similarity ranking",
            "Source attribution panel highlighting exact document snippets",
            "Automated test suite with >80% coverage and Docker deployment"
        ],
        "learning_outcomes": [
            "Embedding generation and chunking strategies",
            "High-throughput vector indexing and search queries",
            "Hybrid search combining keyword BM25 and dense vectors",
            "Asynchronous background file ingestion pipelines"
        ],
        "suggested_milestones": [
            {"title": "Architecture & Document Parsing Pipeline", "phase": "Design", "description": "Implement PDF text extraction and chunking pipeline with error recovery", "deliverables": ["Text extraction service", "Chunking benchmarks"]},
            {"title": "Vector Storage & Semantic Indexing", "phase": "Core Implementation", "description": "Set up pgvector extension, embedding generation, and cosine similarity queries", "deliverables": ["Vector DB schema", "Batch ingestion script"]},
            {"title": "Search Frontend & Source Highlighting", "phase": "Core Implementation", "description": "Build Next.js search UI with real-time filters and snippet previews", "deliverables": ["Responsive search UI", "Source card components"]},
            {"title": "Evaluation, Benchmarking & Deployment", "phase": "Validation & Polish", "description": "Measure search precision@5 against test document corpus and deploy on container", "deliverables": ["Benchmark report", "Docker compose setup"]}
        ],
        "validation_strategy": "Evaluate Retrieval Precision@k across 50 benchmark research queries and collect qualitative feedback from 5 peer students.",
        "possible_next_stage_pathways": ["RESEARCH_AND_PUBLICATION", "PRODUCT_DEVELOPMENT", "CAREER_AND_PORTFOLIO"],
        "relevant_career_skills": ["Machine Learning", "Python", "FastAPI", "Vector Databases", "Information Retrieval", "Next.js", "TypeScript"],
        "primary_goals": ["portfolio", "research", "learning"]
    },
    {
        "id": "distributed-task-orchestrator",
        "title": "Fault-Tolerant Distributed Task Scheduler & Worker Pool",
        "problem_statement": "Microservices need resilient, distributed job execution with retry policies, rate limiting, and dead-letter queues without proprietary cloud lock-in.",
        "intended_users": "Backend engineers and DevOps teams managing asynchronous workloads.",
        "domain": "Cloud & DevOps",
        "difficulty": "advanced",
        "prerequisites": ["Concurrent Programming", "Data Structures", "Networking & TCP", "Distributed Systems Concepts"],
        "recommended_technologies": ["Go or Python", "Redis", "gRPC", "Docker", "Prometheus", "Grafana"],
        "estimated_duration_weeks": 10,
        "weekly_hours": 12,
        "expected_deliverables": [
            "Master-worker architecture with heartbeat liveness detection",
            "Exponential backoff retry policy and dead-letter queue inspection CLI",
            "Real-time task observability metrics dashboard in Prometheus/Grafana",
            "Chaos engineering test suite verifying crash recovery under network partitions"
        ],
        "learning_outcomes": [
            "Distributed consensus and leader election fundamentals",
            "Idempotency tokens and at-least-once message delivery guarantees",
            "Backpressure management and worker concurrency tuning",
            "Production observability with structured metrics"
        ],
        "suggested_milestones": [
            {"title": "Protocol & State Engine Specification", "phase": "Design", "description": "Define protobuf specs for worker communication and Redis state machine", "deliverables": ["Protobuf definitions", "State transition diagram"]},
            {"title": "Master Scheduler & Queue Engine", "phase": "Core Implementation", "description": "Implement task queueing, priority queues, and delayed job dispatching", "deliverables": ["Scheduler service", "Unit test suite"]},
            {"title": "Resilient Worker Pool & Heartbeats", "phase": "Core Implementation", "description": "Build worker daemon with graceful shutdown, signal trapping, and heartbeats", "deliverables": ["Worker CLI", "Heartbeat monitor"]},
            {"title": "Partition Chaos Testing & Metrics", "phase": "Testing & Polish", "description": "Run automated chaos tests simulating node termination during execution", "deliverables": ["Chaos test scripts", "Grafana dashboard export"]}
        ],
        "validation_strategy": "Simulate 10,000 parallel tasks with 10% random worker terminations to confirm 0% task loss.",
        "possible_next_stage_pathways": ["CAREER_AND_PORTFOLIO", "PRODUCT_DEVELOPMENT", "INNOVATION_AND_FURTHER_DISCOVERY"],
        "relevant_career_skills": ["Distributed Systems", "Backend Engineering", "Concurrency", "Redis", "gRPC", "DevOps", "Prometheus"],
        "primary_goals": ["portfolio", "learning"]
    },
    {
        "id": "healthcare-vitals-anomaly-detector",
        "title": "Edge Health Telemetry & Cardiac Anomaly Detection System",
        "problem_statement": "Continuous patient vital streams from wearables are noisy, leading to alarm fatigue for clinicians unless anomalies are prioritized with temporal context.",
        "intended_users": "Healthcare professionals, remote patient monitoring coordinators, and patients.",
        "domain": "HealthTech & BioInformatics",
        "difficulty": "advanced",
        "prerequisites": ["Time Series Analysis", "Signal Processing", "Python", "Data Visualization"],
        "recommended_technologies": ["Python", "PyTorch / Scikit-Learn", "FastAPI", "InfluxDB / TimescaleDB", "React"],
        "estimated_duration_weeks": 10,
        "weekly_hours": 12,
        "expected_deliverables": [
            "ECG/PPG signal cleaning and baseline wander removal filter",
            "LSTM or Isolation Forest anomaly detection model on PhysioNet dataset",
            "Real-time streaming telemetry dashboard with triage urgency categorization",
            "Privacy-first data anonymization pipeline compliant with simulated HIPAA requirements"
        ],
        "learning_outcomes": [
            "Digital signal filtering (Butterworth filter, wavelet transforms)",
            "Time-series anomaly classification with high recall bounds",
            "Streaming time-series database architecture",
            "Medical software compliance and privacy best practices"
        ],
        "suggested_milestones": [
            {"title": "Data Pipeline & Signal Preprocessing", "phase": "Design", "description": "Clean MIT-BIH Arrhythmia benchmark dataset with digital filtering", "deliverables": ["Preprocessing pipeline", "Signal visualizer"]},
            {"title": "Anomaly Detection Model Training", "phase": "Core Implementation", "description": "Train and validate anomaly detector with ROC-AUC and F1 evaluation", "deliverables": ["Trained model weights", "Validation notebook"]},
            {"title": "Real-time Telemetry Service", "phase": "Core Implementation", "description": "Stream synthesized patient feeds through WebSocket and trigger triage alerts", "deliverables": ["Streaming API", "Alert dispatcher"]},
            {"title": "Clinical Dashboard & Paper Draft", "phase": "Validation & Showcase", "description": "Deploy React dashboard and document methodology for undergraduate research", "deliverables": ["Interactive UI", "Draft methodology paper"]}
        ],
        "validation_strategy": "Validate against PhysioNet MIT-BIH dataset aiming for >92% sensitivity on ventricular ectopic beats.",
        "possible_next_stage_pathways": ["RESEARCH_AND_PUBLICATION", "COMPETITIONS_AND_HACKATHONS", "PRODUCT_DEVELOPMENT"],
        "relevant_career_skills": ["Machine Learning", "Data Science", "Signal Processing", "Python", "Healthcare Analytics", "React"],
        "primary_goals": ["research", "portfolio", "competition"]
    },
    {
        "id": "developer-code-review-linter",
        "title": "AST-Based Static Security & Code Quality Assistant",
        "problem_statement": "Novice developers frequently commit API keys, SQL injections, and memory leaks before submitting pull requests.",
        "intended_users": "Student software developers, open-source contributors, and bootcamp educators.",
        "domain": "Cybersecurity & Developer Tools",
        "difficulty": "intermediate",
        "prerequisites": ["Abstract Syntax Trees (AST)", "Regex", "Git Internals", "Python or TypeScript"],
        "recommended_technologies": ["Python (ast module) or TypeScript (compiler API)", "GitHub Actions", "FastAPI", "CLI tool"],
        "estimated_duration_weeks": 6,
        "weekly_hours": 8,
        "expected_deliverables": [
            "CLI tool analyzing Python/JavaScript files for 15+ security anti-patterns",
            "Pre-commit git hook preventing commits with hardcoded secrets",
            "GitHub Action publishing annotated inline PR review comments",
            "Rule authoring guide allowing community-contributed custom checks"
        ],
        "learning_outcomes": [
            "Parsing and traversing Abstract Syntax Trees",
            "Static analysis and taint tracking fundamentals",
            "GitHub Marketplace Action packaging and automated CI",
            "Developer UX and actionable lint error reporting"
        ],
        "suggested_milestones": [
            {"title": "AST Rule Engine Core", "phase": "Design", "description": "Design visitor pattern AST traversal engine with initial 5 security checks", "deliverables": ["Visitor parser", "Secret detector module"]},
            {"title": "Rule Expansion & CLI UX", "phase": "Core Implementation", "description": "Add 10 syntax checks, colored terminal formatter, and JSON output mode", "deliverables": ["Executable CLI", "Rule test suite"]},
            {"title": "Git Pre-commit Hook & GitHub Action", "phase": "Integration", "description": "Package as installable pip/npm package and create GitHub Action workflow", "deliverables": ["Pre-commit config", "Action definition"]},
            {"title": "Benchmark on Vulnerable Repos", "phase": "Validation", "description": "Benchmark detection rate against OWASP NodeGoat and JuiceShop sample code", "deliverables": ["Benchmark audit report", "Public demo repo"]}
        ],
        "validation_strategy": "Run against OWASP vulnerable repository corpus achieving 100% detection on specified test cases with 0 false crashes.",
        "possible_next_stage_pathways": ["CAREER_AND_PORTFOLIO", "PRODUCT_DEVELOPMENT", "COMPETITIONS_AND_HACKATHONS"],
        "relevant_career_skills": ["Cybersecurity", "Static Analysis", "Compilers / AST", "Python", "DevSecOps", "GitHub Actions"],
        "primary_goals": ["portfolio", "learning", "competition"]
    },
    {
        "id": "sustainable-smart-campus-energy",
        "title": "IoT Campus Micro-Grid Energy Prediction & Optimization",
        "problem_statement": "Educational and commercial campuses overconsume electricity during peak pricing hours due to uncoordinated HVAC and lighting schedules.",
        "intended_users": "Facility energy managers, sustainability directors, and smart building operators.",
        "domain": "ClimateTech & IoT",
        "difficulty": "intermediate",
        "prerequisites": ["Linear Regression / XGBoost", "IoT Protocols (MQTT/HTTP)", "Database Modeling", "Web Dashboards"],
        "recommended_technologies": ["Python", "XGBoost", "PostgreSQL", "MQTT / Mosquitto", "React", "Chart.js"],
        "estimated_duration_weeks": 8,
        "weekly_hours": 10,
        "expected_deliverables": [
            "Synthetic campus sensor simulator generating weather, occupancy, and kWh data",
            "Energy consumption forecast model with 24-hour horizon",
            "Automated cost-reduction dispatch recommendation engine",
            "Interactive campus energy dashboard with heatmaps and savings analytics"
        ],
        "learning_outcomes": [
            "Predictive modeling on tabular and IoT sensor datasets",
            "Feature engineering for meteorological and calendar cyclical variables",
            "Constrained optimization for peak load shaving",
            "Green computing and sustainable tech metrics"
        ],
        "suggested_milestones": [
            {"title": "Synthetic Data & Weather Integration", "phase": "Design", "description": "Build realistic sensor data generator combined with Open-Meteo weather API", "deliverables": ["Sensor simulator", "Data loader"]},
            {"title": "Forecast Model Training & Validation", "phase": "Core Implementation", "description": "Train XGBoost regressor predicting building energy demand 24 hours ahead", "deliverables": ["Model evaluation script", "Feature importance plots"]},
            {"title": "Load Shaving Optimizer & Backend API", "phase": "Core Implementation", "description": "Create dispatch optimizer suggesting schedule shifts to minimize peak charges", "deliverables": ["Optimization service", "REST endpoints"]},
            {"title": "Sustainability Dashboard & Case Study", "phase": "Showcase", "description": "Assemble React dashboard and write simulated 1-year ROI case study", "deliverables": ["Dashboard UI", "ROI analysis report"]}
        ],
        "validation_strategy": "Validate Mean Absolute Percentage Error (MAPE) < 8% on 6 months of historical building load test data.",
        "possible_next_stage_pathways": ["COMPETITIONS_AND_HACKATHONS", "STARTUP_AND_COMMERCIALISATION", "CAREER_AND_PORTFOLIO"],
        "relevant_career_skills": ["Data Science", "Python", "IoT", "XGBoost", "PostgreSQL", "Sustainability Tech", "React"],
        "primary_goals": ["competition", "portfolio", "entrepreneurship"]
    },
    {
        "id": "decentralized-credential-verifier",
        "title": "Cryptographically Verifiable Academic Credential Ledger",
        "problem_statement": "Academic credential fraud and slow paper transcript verification burden universities and hiring managers.",
        "intended_users": "University registrar offices, student graduates, and employer HR departments.",
        "domain": "Fintech & Cryptography",
        "difficulty": "intermediate",
        "prerequisites": ["Public Key Cryptography (ED25519/ECDSA)", "Digital Signatures", "Web APIs", "TypeScript"],
        "recommended_technologies": ["Node.js / TypeScript", "PostgreSQL", "WebCrypto API / Libsodium", "React", "Tailwind CSS"],
        "estimated_duration_weeks": 7,
        "weekly_hours": 8,
        "expected_deliverables": [
            "Cryptographic issuance service signing transcripts with institution keypair",
            "Tamper-proof verifiable credential format (W3C standard JSON-LD aligned)",
            "Instant QR-code verification portal verifying signature validity in <500ms",
            "Revocation registry supporting immediate transcript invalidation"
        ],
        "learning_outcomes": [
            "Asymmetric key generation, certificate signing, and verification",
            "Self-sovereign identity and W3C Verifiable Credentials standards",
            "Zero-knowledge selective disclosure proof concepts",
            "Cryptographic tamper-evidence in enterprise systems"
        ],
        "suggested_milestones": [
            {"title": "Cryptographic Specification & Key Management", "phase": "Design", "description": "Design keypair lifecycle and JSON credential schema conforming to W3C VC", "deliverables": ["Schema spec", "Key generation utilities"]},
            {"title": "Issuer Service & Transcript Builder", "phase": "Core Implementation", "description": "Build registrar portal to issue and cryptographically sign academic degrees", "deliverables": ["Issuer dashboard", "Signing endpoint"]},
            {"title": "Public Verification Engine & QR Scanner", "phase": "Core Implementation", "description": "Implement browser-based verifier that validates signatures without backend dependence", "deliverables": ["Verifier page", "Camera QR scanner"]},
            {"title": "Revocation Mechanism & Security Audit", "phase": "Validation & Polish", "description": "Add cryptographic accumulator or status list for revocation, and run threat model audit", "deliverables": ["Revocation registry", "Threat model document"]}
        ],
        "validation_strategy": "Demonstrate instant verification of 100 test transcripts with 100% rejection of altered grades or revoked credentials.",
        "possible_next_stage_pathways": ["PRODUCT_DEVELOPMENT", "CAREER_AND_PORTFOLIO", "STARTUP_AND_COMMERCIALISATION"],
        "relevant_career_skills": ["Applied Cryptography", "TypeScript", "Node.js", "Web Security", "React", "Fintech / Identity"],
        "primary_goals": ["portfolio", "product", "entrepreneurship"]
    },
    {
        "id": "collaborative-markdown-knowledge-base",
        "title": "Real-Time Collaborative Markdown Documentation Engine",
        "problem_statement": "Engineering teams need lightweight, self-hosted documentation with real-time peer editing and version branching like Git.",
        "intended_users": "Engineering teams, university group projects, and open-source documentation maintainers.",
        "domain": "Full Stack Web",
        "difficulty": "intermediate",
        "prerequisites": ["WebSockets", "Conflict Resolution (CRDTs or Operational Transformation)", "React", "Node.js or Python"],
        "recommended_technologies": ["Next.js", "FastAPI / Node.js", "Yjs / Automerge CRDT", "PostgreSQL", "Tailwind CSS"],
        "estimated_duration_weeks": 8,
        "weekly_hours": 10,
        "expected_deliverables": [
            "Multi-user concurrent markdown editor with cursor presence indicators",
            "CRDT-based conflict-free document synchronization over WebSockets",
            "Hierarchical document tree with tags, search, and export to PDF/HTML",
            "Revision history timeline with visual character-level diffs"
        ],
        "learning_outcomes": [
            "Conflict-free Replicated Data Types (CRDTs) implementation",
            "Stateful WebSocket connection management and reconnect handling",
            "Rich-text editor abstractions and virtualized rendering",
            "High-performance client-side state synchronization"
        ],
        "suggested_milestones": [
            {"title": "CRDT & WebSocket Sync Core", "phase": "Design & Prototype", "description": "Set up Yjs CRDT room provider over WebSockets with 2-client test harness", "deliverables": ["Sync server", "Harness test"]},
            {"title": "Markdown Editor & Live Cursors", "phase": "Core Implementation", "description": "Build responsive editor with split-screen preview and live peer cursor badges", "deliverables": ["Editor component", "Presence badge module"]},
            {"title": "Folder Hierarchy & Full-Text Search", "phase": "Feature Development", "description": "Implement nested workspaces, permissions, and client-side instant search", "deliverables": ["Workspace sidebar", "Search index"]},
            {"title": "Diff History & Offline Support", "phase": "Validation & Polish", "description": "Add local IndexedDB caching for offline edits and commit history playback", "deliverables": ["Offline sync manager", "Diff viewer"]}
        ],
        "validation_strategy": "Simulate 5 concurrent users typing simultaneously without split-brain state desynchronization.",
        "possible_next_stage_pathways": ["PRODUCT_DEVELOPMENT", "CAREER_AND_PORTFOLIO"],
        "relevant_career_skills": ["Full Stack Web", "WebSockets", "CRDTs", "Next.js", "React", "TypeScript", "Node.js"],
        "primary_goals": ["portfolio", "learning", "product"]
    },
    {
        "id": "micro-climate-sensor-network",
        "title": "Urban Heat Island Microclimate Mapping & Forecasting",
        "problem_statement": "Municipal urban planners lack street-level temperature and air quality granularity required to combat urban heat islands.",
        "intended_users": "Urban researchers, environmental advocacy groups, and municipal sustainability teams.",
        "domain": "ClimateTech & IoT",
        "difficulty": "advanced",
        "prerequisites": ["Geospatial Analysis (GIS / GeoJSON)", "Python", "Spatial Interpolation (Kriging)", "Data Visualization"],
        "recommended_technologies": ["Python", "GeoPandas / Folium / Mapbox", "FastAPI", "PostGIS", "React"],
        "estimated_duration_weeks": 9,
        "weekly_hours": 10,
        "expected_deliverables": [
            "PostGIS spatial database storing geo-tagged environmental sensor readings",
            "Spatial interpolation pipeline (Ordinary Kriging) generating heat raster surfaces",
            "Interactive WebGIS map with polygon neighborhood vulnerability heatmaps",
            "Automated policy recommendation report generator for urban canopy intervention"
        ],
        "learning_outcomes": [
            "Geospatial databases and PostGIS indexing (ST_Contains, ST_DWithin)",
            "Spatial statistics and spatial interpolation algorithms",
            "Interactive web mapping with Mapbox GL / Deck.gl vector tiles",
            "Environmental data communication for civic stakeholders"
        ],
        "suggested_milestones": [
            {"title": "Spatial Database & Open Data Ingestion", "phase": "Design", "description": "Collect public municipal sensor data (OpenAQ / NOAA) into PostGIS schema", "deliverables": ["PostGIS schema", "Ingestion ETL script"]},
            {"title": "Kriging Interpolation Engine", "phase": "Core Implementation", "description": "Develop spatial interpolation model generating 50m resolution temperature grids", "deliverables": ["Kriging module", "Raster generator"]},
            {"title": "Interactive WebGIS Visualizer", "phase": "Core Implementation", "description": "Build high-performance Mapbox GL choropleth and isoline visualization", "deliverables": ["Map component", "Layer switcher"]},
            {"title": "Intervention Scenario Simulator & Showcase", "phase": "Validation & Showcase", "description": "Simulate 20% tree canopy addition and publish civic research case study", "deliverables": ["Simulation module", "Published case study"]}
        ],
        "validation_strategy": "Cross-validate spatial prediction against withheld sensor stations with Root Mean Square Error (RMSE) < 1.2 degrees Celsius.",
        "possible_next_stage_pathways": ["RESEARCH_AND_PUBLICATION", "COMPETITIONS_AND_HACKATHONS", "CAREER_AND_PORTFOLIO"],
        "relevant_career_skills": ["Geospatial Analytics", "PostGIS", "Python", "Data Science", "Mapbox", "Environmental Tech"],
        "primary_goals": ["research", "competition", "portfolio"]
    }
]


class ProjectIdeasService:
    """Service providing curated project ideas and deterministic recommendations."""

    def __init__(self, catalogue: List[Dict[str, Any]] = None):
        self.catalogue = catalogue or PROJECT_IDEAS_CATALOGUE

    def list_ideas(
        self,
        domain: Optional[str] = None,
        difficulty: Optional[str] = None,
        max_duration_weeks: Optional[int] = None,
        goal: Optional[str] = None,
        technology: Optional[str] = None,
    ) -> List[ProjectIdea]:
        """Filter ideas deterministically according to criteria."""
        results = []
        for raw in self.catalogue:
            if domain and domain.lower() not in raw["domain"].lower():
                continue
            if difficulty and difficulty.lower() != "any" and raw["difficulty"].lower() != difficulty.lower():
                continue
            if max_duration_weeks and raw["estimated_duration_weeks"] > max_duration_weeks:
                continue
            if goal and goal.lower() not in [g.lower() for g in raw.get("primary_goals", [])]:
                continue
            if technology:
                tech_match = any(
                    technology.lower() in t.lower()
                    for t in raw.get("recommended_technologies", []) + raw.get("relevant_career_skills", [])
                )
                if not tech_match:
                    continue
            results.append(self._to_schema(raw))
        return results

    def get_idea_by_id(self, idea_id: str) -> Optional[ProjectIdea]:
        """Fetch a single project idea by identifier."""
        for raw in self.catalogue:
            if raw["id"] == idea_id:
                return self._to_schema(raw)
        return None

    def recommend_ideas(
        self,
        request: IdeaRecommendationRequest,
        career_interests: Optional[List[str]] = None,
        student_skills: Optional[List[str]] = None,
    ) -> List[ProjectIdea]:
        """
        Deterministic, rule-based ranking of ideas.
        
        Scoring Rubric (Total 100 points):
        - Skill Overlap (0-35 pts): Ratio of student skills matching idea prerequisites/technologies
        - Career Role Alignment (0-25 pts): Overlap between student's career target and idea domain/skills
        - Difficulty Fit (0-15 pts): Match between user availability/preference and idea difficulty
        - Weekly Time Availability (0-15 pts): Difference between student weekly hours and idea requirement
        - Primary Objective Fit (0-10 pts): Whether idea supports student's learning, portfolio, or research goal
        """
        combined_skills = set(s.lower().strip() for s in (student_skills or []) + (request.existing_skills or []))
        combined_roles = set(r.lower().strip() for r in (career_interests or []) + (request.target_career_roles or []))
        preferred_techs = set(t.lower().strip() for t in (request.preferred_technologies or []))

        scored_ideas = []

        for raw in self.catalogue:
            score = 0
            explanations = []

            # 1. Skill Overlap (0-35 points)
            idea_tech_skill_pool = set(
                t.lower().strip() for t in raw["recommended_technologies"] + raw["relevant_career_skills"] + raw["prerequisites"]
            )
            matching_skills = [
                s for s in combined_skills
                if any(s in item or item in s for item in idea_tech_skill_pool)
            ]
            matching_preferred = [
                t for t in preferred_techs
                if any(t in item or item in t for item in idea_tech_skill_pool)
            ]

            all_matched = list(set(matching_skills + matching_preferred))
            if all_matched:
                skill_points = min(35, len(all_matched) * 10)
                score += skill_points
                explanations.append(f"Directly leverages {len(all_matched)} of your known skills: {', '.join(all_matched[:4])}")
            else:
                score += 10  # Baseline discovery allowance for learning
                explanations.append("Introduces modern industry tools aligned with current hiring demand")

            # 2. Career Role Alignment (0-25 points)
            role_match = False
            for role in combined_roles:
                if any(word in raw["domain"].lower() or any(word in s.lower() for s in raw["relevant_career_skills"]) for word in role.split()):
                    score += 25
                    role_match = True
                    explanations.append(f"Highly relevant for your target career direction in {role.title()}")
                    break
            if not role_match and request.target_domain:
                if request.target_domain.lower() in raw["domain"].lower():
                    score += 20
                    explanations.append(f"Matches your specified domain of interest ({raw['domain']})")

            # 3. Difficulty Fit (0-15 points)
            diff_pref = (request.difficulty_preference or "any").lower()
            if diff_pref == "any" or diff_pref == raw["difficulty"].lower():
                score += 15
                explanations.append(f"Matches your preferred {raw['difficulty']} difficulty level")
            elif diff_pref == "beginner" and raw["difficulty"] == "intermediate":
                score += 8
            elif diff_pref == "advanced" and raw["difficulty"] == "intermediate":
                score += 10

            # 4. Weekly Time Availability (0-15 points)
            student_hours = request.weekly_hours_available or 10
            idea_hours = raw["weekly_hours"]
            hour_diff = abs(student_hours - idea_hours)
            if hour_diff <= 2:
                score += 15
                explanations.append(f"Fits your {student_hours} hrs/week availability ({idea_hours} hrs/week required)")
            elif hour_diff <= 5:
                score += 10
                explanations.append(f"Manageable workload ({idea_hours} hrs/week vs your {student_hours} hrs/week)")
            else:
                score += 5

            # 5. Primary Objective (0-10 points)
            target_goal = (request.primary_objective or "portfolio").lower()
            if any(target_goal in g.lower() for g in raw.get("primary_goals", [])):
                score += 10
                explanations.append(f"Explicitly structured for {target_goal.title()} outcomes")

            # Clamp score 0 - 100
            final_score = min(99, max(25, score))

            idea_copy = dict(raw)
            idea_copy["match_score"] = final_score
            idea_copy["match_explanation"] = " • ".join(explanations)
            scored_ideas.append(self._to_schema(idea_copy))

        # Sort descending by match score
        scored_ideas.sort(key=lambda x: x.match_score or 0, reverse=True)
        return scored_ideas

    def _to_schema(self, raw: Dict[str, Any]) -> ProjectIdea:
        milestones = [
            MilestoneTemplate(
                title=m["title"],
                phase=m["phase"],
                description=m["description"],
                deliverables=m.get("deliverables", [])
            )
            for m in raw.get("suggested_milestones", [])
        ]
        return ProjectIdea(
            id=raw["id"],
            title=raw["title"],
            problem_statement=raw["problem_statement"],
            intended_users=raw["intended_users"],
            domain=raw["domain"],
            difficulty=raw["difficulty"],
            prerequisites=raw["prerequisites"],
            recommended_technologies=raw["recommended_technologies"],
            estimated_duration_weeks=raw["estimated_duration_weeks"],
            weekly_hours=raw["weekly_hours"],
            expected_deliverables=raw["expected_deliverables"],
            learning_outcomes=raw["learning_outcomes"],
            suggested_milestones=milestones,
            validation_strategy=raw["validation_strategy"],
            possible_next_stage_pathways=raw["possible_next_stage_pathways"],
            relevant_career_skills=raw["relevant_career_skills"],
            primary_goals=raw.get("primary_goals", ["portfolio", "learning"]),
            match_score=raw.get("match_score"),
            match_explanation=raw.get("match_explanation")
        )


project_ideas_service = ProjectIdeasService()
