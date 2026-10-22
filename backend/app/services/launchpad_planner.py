"""
Orvena Project Launchpad: Structured Project Planning Service

Transforms student project ideas into a structured, realistic engineering plan
complete with MVP scope boundaries, development phases, testing protocols,
risk registers, and milestone blueprints using deterministic domain rules.
"""
from typing import List, Dict, Any
from app.schemas.launchpad import PlanGenerationRequest, GeneratedProjectPlan, PlannedPhase, MilestoneTemplate


class ProjectPlannerService:
    """Deterministic, rule-based engineering project planning."""

    def generate_plan(self, request: PlanGenerationRequest) -> GeneratedProjectPlan:
        """Construct a structured project plan based on the student's idea specifications."""
        domain_clean = request.domain.strip()
        total_weeks = max(4, min(24, request.target_duration_weeks))
        
        # Calculate phase allocation proportional to total weeks
        phase1_weeks = max(1, round(total_weeks * 0.20))
        phase2_weeks = max(1, round(total_weeks * 0.45))
        phase3_weeks = max(1, round(total_weeks * 0.20))
        phase4_weeks = max(1, total_weeks - (phase1_weeks + phase2_weeks + phase3_weeks))

        w1_start, w1_end = 1, phase1_weeks
        w2_start, w2_end = w1_end + 1, w1_end + phase2_weeks
        w3_start, w3_end = w2_end + 1, w2_end + phase3_weeks
        w4_start, w4_end = w3_end + 1, total_weeks

        # 1. Minimum Viable Scope (MVP) vs Future Scope
        mvp_scope = [
            f"Core data models and persistence layer for {request.title}",
            f"Single primary user workflow solving: '{request.problem_statement[:120]}...'",
            f"Functional API or CLI interface built with {', '.join(request.technologies[:2])}",
            "Basic input validation and defensive error boundary handling",
            "Local environment setup reproducible via README or Docker script"
        ]

        future_scope = [
            "Advanced multi-tenant user authentication and granular access controls",
            "Distributed caching, background job queues, and asynchronous processing",
            "Comprehensive analytics telemetry and user interaction telemetry",
            "Multi-region cloud deployment and CI/CD automated release pipeline",
            "Native mobile client or external integration webhooks"
        ]

        # 2. Prerequisites
        prerequisites = [
            f"Working proficiency in {request.technologies[0]} core syntax and async idioms",
            f"Familiarity with {request.technologies[1] if len(request.technologies) > 1 else 'RESTful API protocols'}",
            "Version control hygiene with Git (branching, semantic commits, PR workflows)",
            "Basic database design and relational or document query indexing"
        ]

        # 3. Phased Plan
        phases: List[PlannedPhase] = [
            PlannedPhase(
                phase_name="Phase 1: Architecture, Scope & Foundations",
                target_week_start=w1_start,
                target_week_end=w1_end,
                objective="Formalize system architecture, define API schemas, and configure development toolchain.",
                tasks=[
                    f"Create git repository and initialize project workspace using {request.technologies[0]}",
                    "Draft entity relationship diagrams and data schema contracts",
                    "Set up linting, code formatting, and pre-commit checks",
                    "Establish reproducible local database or storage container"
                ],
                deliverables=[
                    "System Architecture Diagram & Data Dictionary",
                    "Initial skeleton codebase compiling cleanly with zero linter warnings",
                    "Local setup documentation in README.md"
                ],
                validation_criteria="All team members or peer reviewers can clone the repo and execute baseline tests with a single command."
            ),
            PlannedPhase(
                phase_name="Phase 2: Core Implementation (MVP)",
                target_week_start=w2_start,
                target_week_end=w2_end,
                objective="Build the critical functional backbone solving the primary user challenge.",
                tasks=[
                    f"Implement core domain logic addressing: {request.proposed_solution[:100]}",
                    f"Build primary interfaces using {', '.join(request.technologies[:3])}",
                    "Integrate data persistence layer with input validation and sanitization",
                    "Implement transactional boundary handling and informative error responses"
                ],
                deliverables=[
                    "Functional MVP demonstrating the end-to-end user path",
                    "Comprehensive unit tests for core computational and business logic",
                    "Seed data scripts generating realistic test datasets"
                ],
                validation_criteria="The primary user workflow executes successfully from start to finish without manual database tampering."
            ),
            PlannedPhase(
                phase_name="Phase 3: Testing, Verification & Hardening",
                target_week_start=w3_start,
                target_week_end=w3_end,
                objective="Verify reliability under edge cases, run integration tests, and optimize performance.",
                tasks=[
                    "Write integration and end-to-end user scenario tests",
                    "Test boundary cases: empty payloads, network timeouts, invalid inputs, and concurrency",
                    "Profile execution latency and database query indexing",
                    "Conduct security review against common OWASP vulnerabilities"
                ],
                deliverables=[
                    "Automated test suite achieving >75% test coverage on business logic",
                    "Performance benchmark report documenting response times under moderate load",
                    "Security and input sanitization audit checklist"
                ],
                validation_criteria="Automated CI test run passes with zero failures, zero unhandled promise rejections, and documented p95 latency <500ms."
            ),
            PlannedPhase(
                phase_name="Phase 4: Deployment, Documentation & Outcome Presentation",
                target_week_start=w4_start,
                target_week_end=w4_end,
                objective="Deploy a live demonstration, publish clean technical documentation, and package for portfolio presentation.",
                tasks=[
                    "Deploy live demo instance or publish installable release binary",
                    "Author comprehensive API documentation or interactive Swagger/Postman collection",
                    "Record a 2-minute architectural walk-through video or GIF showcase",
                    "Write technical retrospective documenting trade-offs, benchmarks, and future roadmap"
                ],
                deliverables=[
                    "Live, publicly accessible demo URL or release artifact",
                    "Polished GitHub repository with badged CI, architecture diagrams, and clear setup",
                    "Outcome portfolio summary ready for resume and LinkedIn publication"
                ],
                validation_criteria="An external engineer or recruiter can understand the problem, inspect the live demo, and review the code in <5 minutes."
            )
        ]

        # 4. Testing & Validation Plan
        testing_plan = [
            "Unit Tests: Automated verification of all standalone domain functions and calculators",
            "Integration Tests: Validating API endpoints, database transactions, and network fallbacks",
            "Data Validation: Schema enforcement preventing corrupted or malformed payloads",
            "User Experience Walkthrough: Guided testing session with at least 2 external target users",
            "Resilience Testing: Simulating offline state or database disconnection gracefully"
        ]

        # 5. Risks & Dependencies
        risks = [
            {
                "risk": "Scope Creep",
                "impact": "High",
                "mitigation": "Strictly adhere to Phase 2 MVP boundary before beginning non-essential aesthetic features."
            },
            {
                "risk": "Integration / Tooling Roadblock",
                "impact": "Medium",
                "mitigation": "Spike technical unknowns during Phase 1 with lightweight throwaway prototypes."
            },
            {
                "risk": "Inadequate Testing / Edge Bugs",
                "impact": "Medium",
                "mitigation": "Enforce automated test runs on every pull request and maintain seed fixtures."
            },
            {
                "risk": "Time Budget Shortfall",
                "impact": "High",
                "mitigation": f"Allocate {request.weekly_hours} dedicated weekly hours and schedule milestone check-ins every Sunday."
            }
        ]

        # 6. Suggested Milestones Blueprint
        suggested_milestones: List[MilestoneTemplate] = [
            MilestoneTemplate(
                title="Project Inception & Architecture Spec",
                phase="Architecture & Design",
                description="Finalize requirements, database schemas, and toolchain setup.",
                deliverables=["Architecture diagram", "Schema definitions", "Initial Git repo"]
            ),
            MilestoneTemplate(
                title="MVP Core Functionality Implemented",
                phase="Core Implementation",
                description="Complete the central user workflow and data persistence pipeline.",
                deliverables=["Working MVP branch", "Unit test suite", "Seed data script"]
            ),
            MilestoneTemplate(
                title="Test Coverage & Security Hardening",
                phase="Testing & Verification",
                description="Execute integration tests, boundary validations, and performance profiling.",
                deliverables=["Integration tests", "Benchmark results", "Error handling audit"]
            ),
            MilestoneTemplate(
                title="Live Deployment & Portfolio Showcase",
                phase="Documentation & Deployment",
                description="Deploy to public hosting, complete README documentation, and configure showcase link.",
                deliverables=["Live demo URL", "Clean technical README", "Project showcase profile"]
            )
        ]

        return GeneratedProjectPlan(
            title=request.title,
            problem_definition=f"Addressing the challenge where {request.intended_users} experience: {request.problem_statement}",
            minimum_viable_scope=mvp_scope,
            future_scope=future_scope,
            required_prerequisites=prerequisites,
            phases=phases,
            testing_and_validation_plan=testing_plan,
            risks_and_dependencies=risks,
            suggested_milestones=suggested_milestones,
            suggested_timeline_weeks=total_weeks
        )


project_planner_service = ProjectPlannerService()
