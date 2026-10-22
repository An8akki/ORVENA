"""
Orvena Project Launchpad: Project Outcome Intelligence Engine

The core differentiator: evaluates completed and mature student projects across
6 strategic future development pathways using deterministic, rule-based reasoning:
1. Product Development
2. Research & Publication
3. Innovation & Further Discovery
4. Startup & Commercialisation
5. Competitions & Hackathons
6. Career & Portfolio
"""
from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime

from app.schemas.launchpad import (
    OutcomeIntelligenceResponse,
    PathwayResult,
    MilestoneTemplate,
)


class ProjectOutcomeIntelligenceService:
    """Evaluates student projects for multi-pathway strategic outcomes."""

    def analyze_outcomes(
        self,
        project_id: Any,
        project_title: str,
        project_stage: str,
        domain: str,
        primary_goal: str,
        technologies: List[str],
        evaluation_scores: Optional[Dict[str, Any]] = None,
        has_repo: bool = False,
        has_demo: bool = False,
        student_intent: Optional[str] = None
    ) -> OutcomeIntelligenceResponse:
        """
        Evaluates project against all 6 strategic outcome pathways deterministically.
        Calculates scores, identifies missing evidence, and suggests milestone conversion plans.
        """
        scores = evaluation_scores or {}
        dim_scores = scores.get("dimension_scores", {})

        prob_score = dim_scores.get("problem_clarity", {}).get("score", 12.0)
        impl_score = dim_scores.get("implementation_maturity", {}).get("score", 12.0)
        test_score = dim_scores.get("testing_validation", {}).get("score", 10.0)
        diff_score = dim_scores.get("differentiation", {}).get("score", 12.0)
        doc_score = dim_scores.get("documentation_readiness", {}).get("score", 10.0)

        pathways: List[PathwayResult] = []

        # -------------------------------------------------------------
        # Pathway A: Product Development
        # -------------------------------------------------------------
        prod_score = int(min(100, (impl_score * 2.2) + (doc_score * 1.5) + (test_score * 1.0) + (10 if has_demo else 0)))
        prod_tier = "Ready" if prod_score >= 75 else ("Near-Ready" if prod_score >= 50 else "Needs Foundational Work")
        pathways.append(PathwayResult(
            pathway_key="PRODUCT_DEVELOPMENT",
            title="Product Development & Production Engineering",
            score=prod_score,
            tier=prod_tier,
            summary_rationale=(
                f"Project demonstrates strong software foundations in {domain}. "
                "With robust error boundaries, automated deployments, and end-user onboarding, "
                "this can evolve into an accessible, continuously deployed software product."
            ),
            readiness_factors=[
                "Working core implementation with functional user path",
                f"Built using production-standard tech stack ({', '.join(technologies[:3])})",
                "Demonstrated understanding of user workflow requirements"
            ],
            missing_evidence=[
                "Continuous integration & automated deployment pipeline (GitHub Actions / Vercel)",
                "Telemetry, error logging (e.g. Sentry), and analytics instrumentation",
                "Accessibility (WCAG 2.1 AA) and cross-browser responsiveness audit"
            ],
            action_checklist=[
                "Deploy production instance with custom domain and SSL certificate",
                "Configure automated CI/CD pipeline running lint, test, and build checks",
                "Set up structured application logging and health check endpoints",
                "Conduct user onboarding trial with at least 5 representative users"
            ],
            suggested_milestones=[
                MilestoneTemplate(title="Production Infrastructure & CI/CD", phase="Product Development", description="Deploy containerized app with automated pipeline and SSL", deliverables=["Live URL", "CI/CD workflow"]),
                MilestoneTemplate(title="Telemetry & Observability", phase="Product Development", description="Instrument Sentry error tracking and performance metrics", deliverables=["Error dashboard", "Telemetry logs"]),
                MilestoneTemplate(title="User Feedback & Usability Iteration", phase="Product Development", description="Collect user session recordings and resolve critical onboarding UX blockers", deliverables=["UX audit", "Revision release"])
            ]
        ))

        # -------------------------------------------------------------
        # Pathway B: Research and Publication
        # -------------------------------------------------------------
        research_score = int(min(100, (diff_score * 2.5) + (test_score * 1.5) + (prob_score * 1.0)))
        research_tier = "Ready" if research_score >= 75 else ("Near-Ready" if research_score >= 50 else "Needs Foundational Work")
        pathways.append(PathwayResult(
            pathway_key="RESEARCH_AND_PUBLICATION",
            title="Research Paper & Academic Publication",
            score=research_score,
            tier=research_tier,
            summary_rationale=(
                f"Differentiation and technical methodology in {domain} exhibit potential research attributes. "
                "To prepare for workshop or conference publication (IEEE/ACM/ArXiv), the methodology requires "
                "formal baseline benchmarking and comparative statistical validation."
            ),
            readiness_factors=[
                "Distinct technical approach addressing an identified domain gap",
                "Clear mathematical, architectural, or algorithmic framing",
                "Reproducible software environment"
            ],
            missing_evidence=[
                "Comparative empirical evaluation against established baseline state-of-the-art methods",
                "Formal literature review covering 10-15 recent peer-reviewed publications",
                "Statistical significance testing (e.g., p-values, confidence intervals on benchmarks)",
                "Documented reproducibility artifact guidelines"
            ],
            action_checklist=[
                "Draft Related Work section citing recent 2024-2026 IEEE/ACM papers in the domain",
                "Define quantifiable benchmark metrics (e.g. latency, throughput, F1 score, memory overhead)",
                "Implement 1-2 baseline alternatives for empirical comparison",
                "Draft paper using IEEE/ACM LaTeX conference template"
            ],
            suggested_milestones=[
                MilestoneTemplate(title="Literature Survey & Related Work", phase="Research & Publication", description="Complete survey of 12 benchmark papers and position novelty", deliverables=["Literature matrix", "Related work section"]),
                MilestoneTemplate(title="Comparative Benchmark Experiments", phase="Research & Publication", description="Run controlled experiments comparing proposed system vs 2 baselines", deliverables=["Experimental dataset", "Benchmark plots"]),
                MilestoneTemplate(title="Draft Conference Paper Submission", phase="Research & Publication", description="Author full 6-8 page manuscript adhering to IEEE/ACM guidelines", deliverables=["LaTeX manuscript PDF", "Artifact repository"])
            ]
        ))

        # -------------------------------------------------------------
        # Pathway C: Innovation and Further Discovery
        # -------------------------------------------------------------
        inno_score = int(min(100, (diff_score * 2.0) + (prob_score * 1.5) + (impl_score * 1.2)))
        inno_tier = "Ready" if inno_score >= 75 else ("Near-Ready" if inno_score >= 50 else "Needs Foundational Work")
        pathways.append(PathwayResult(
            pathway_key="INNOVATION_AND_FURTHER_DISCOVERY",
            title="Deep-Tech Innovation & Experimental Discovery",
            score=inno_score,
            tier=inno_tier,
            summary_rationale=(
                "The project uncovers intriguing technical questions that warrant further exploratory engineering. "
                "Expanding beyond the initial scope can reveal novel algorithmic improvements or cross-disciplinary applications."
            ),
            readiness_factors=[
                "Creative problem formulation departing from standard textbook implementations",
                "Modular architecture allowing rapid testing of alternative hypotheses",
                "Opportunity for institutional mentorship and lab collaboration"
            ],
            missing_evidence=[
                "Systematic test matrix exploring boundary performance across unusual parameters",
                "Domain expert feedback from university faculty or senior specialists",
                "Formal documentation of unexpected failure modes or non-linear behaviors"
            ],
            action_checklist=[
                "Formulate 3 testable hypotheses regarding system scalability or algorithmic efficiency",
                "Conduct faculty / advisor consultation meeting to review methodology",
                "Explore applicability to adjacent domains (e.g. applying ML telemetry to IoT/energy)",
                "Prepare invention disclosure or institutional open-source release"
            ],
            suggested_milestones=[
                MilestoneTemplate(title="Hypothesis Formulation & Protocol", phase="Innovation & Discovery", description="Specify 3 experimental hypotheses and parameter matrix", deliverables=["Experimental protocol"]),
                MilestoneTemplate(title="Deep-Tech Parameter Exploration", phase="Innovation & Discovery", description="Execute stress benchmarks across non-standard data distributions", deliverables=["Findings analysis"]),
                MilestoneTemplate(title="Advisor Consultation & Institutional Filing", phase="Innovation & Discovery", description="Present discoveries to faculty advisors and evaluate disclosure", deliverables=["Presentation deck", "Disclosure draft"])
            ]
        ))

        # -------------------------------------------------------------
        # Pathway D: Startup and Commercialisation
        # -------------------------------------------------------------
        biz_score = int(min(100, (prob_score * 2.2) + (impl_score * 1.4) + (diff_score * 1.4) + (10 if has_demo else 0)))
        biz_tier = "Ready" if biz_score >= 75 else ("Near-Ready" if biz_score >= 50 else "Needs Foundational Work")
        pathways.append(PathwayResult(
            pathway_key="STARTUP_AND_COMMERCIALISATION",
            title="Startup, Incubator & Commercialisation Pathway",
            score=biz_score,
            tier=biz_tier,
            summary_rationale=(
                "Addresses a concrete, recognizable friction point with tangible value proposition. "
                "With customer discovery interviews, unit economics validation, and an incubator pitch, "
                "this has potential as a viable student-founded venture."
            ),
            readiness_factors=[
                "High problem relevance addressing real user friction",
                "Working prototype enabling immediate demonstration to potential users",
                "Clear domain applicability with identifiable customer personas"
            ],
            missing_evidence=[
                "15+ documented customer discovery interviews verifying willingness to adopt/pay",
                "Competitive matrix comparing direct and indirect alternative tools",
                "Basic unit economics model (hosting costs vs customer lifetime value assumptions)"
            ],
            action_checklist=[
                "Conduct 15 customer discovery interviews using The Mom Test methodology",
                "Create a 1-page Lean Canvas outlining customer segments, value proposition, and distribution channels",
                "Build a high-converting landing page with waitlist registration",
                "Prepare a 10-slide investor / incubator pitch deck"
            ],
            suggested_milestones=[
                MilestoneTemplate(title="Customer Discovery & Validation Interviews", phase="Commercialisation", description="Interview 15 target users and validate pain point severity", deliverables=["Interview synthesis", "Lean Canvas"]),
                MilestoneTemplate(title="Waitlist Landing Page & Early Adopters", phase="Commercialisation", description="Launch landing page and onboard first 10 pilot users", deliverables=["Landing page URL", "Pilot feedback log"]),
                MilestoneTemplate(title="Pitch Deck & Incubator Applications", phase="Commercialisation", description="Author 10-slide pitch deck and apply to 3 student accelerators", deliverables=["Pitch deck PDF", "Application tracker"])
            ]
        ))

        # -------------------------------------------------------------
        # Pathway E: Competitions and Hackathons
        # -------------------------------------------------------------
        comp_score = int(min(100, (impl_score * 2.0) + (diff_score * 1.5) + (doc_score * 1.5) + (10 if has_demo else 0)))
        comp_tier = "Ready" if comp_score >= 75 else ("Near-Ready" if comp_score >= 50 else "Needs Foundational Work")
        pathways.append(PathwayResult(
            pathway_key="COMPETITIONS_AND_HACKATHONS",
            title="Student Competitions, Hackathons & Innovation Awards",
            score=comp_score,
            tier=comp_tier,
            summary_rationale=(
                "The project features visually compelling interfaces and measurable technical impact. "
                "These attributes make it an outstanding candidate for student hackathons, innovation grants, "
                "and collegiate technology competitions."
            ),
            readiness_factors=[
                "High visual demonstration appeal with clear before/after problem contrast",
                "Novel combination of modern APIs and frameworks",
                "Applicability to social, sustainability, or developer productivity themes"
            ],
            missing_evidence=[
                "2-minute high-energy demonstration pitch video highlighting core value",
                "Executive 1-page project abstract articulating social or technical impact",
                "Submission checklist mapped to specific hackathon judging rubrics"
            ],
            action_checklist=[
                "Record a 2-minute demonstration video explaining problem, architecture, and live demo",
                "Package repository with clear license, quickstart instructions, and video link",
                "Map project outcomes to major student competition themes (e.g. Microsoft Imagine Cup, Google Solution Challenge)",
                "Submit to 2 curated upcoming events in the Orvena Opportunity Directory"
            ],
            suggested_milestones=[
                MilestoneTemplate(title="2-Minute Pitch Video & Slide Deck", phase="Competition Preparation", description="Record high-impact demo walkthrough and executive summary", deliverables=["Video link", "1-page summary"]),
                MilestoneTemplate(title="Rubric Alignment & Polish", phase="Competition Preparation", description="Audit repository against competition judging criteria", deliverables=["Submission checklist", "Clean release tag"]),
                MilestoneTemplate(title="Event Submission & Presentation", phase="Competition Preparation", description="Submit project to target competition and rehearse 5-minute Q&A", deliverables=["Submission confirmation", "Pitch notes"])
            ]
        ))

        # -------------------------------------------------------------
        # Pathway F: Career and Portfolio
        # -------------------------------------------------------------
        career_score = int(min(100, (impl_score * 2.0) + (doc_score * 2.0) + (test_score * 1.0)))
        career_tier = "Ready" if career_score >= 75 else ("Near-Ready" if career_score >= 50 else "Needs Foundational Work")
        pathways.append(PathwayResult(
            pathway_key="CAREER_AND_PORTFOLIO",
            title="Industry Portfolio, Resume Asset & Technical Interview Asset",
            score=career_score,
            tier=career_tier,
            summary_rationale=(
                "Demonstrates concrete engineering capability and architectural decision-making. "
                "Packaging this project into STAR-format resume bullet points, a pinned GitHub repository, "
                "and an Orvena Project Showcase will significantly elevate technical interview readiness."
            ),
            readiness_factors=[
                f"Practical application of in-demand industry technologies ({', '.join(technologies[:3])})",
                "Demonstrates end-to-end delivery capability beyond standard university coursework",
                "Clear architectural trade-offs to discuss in technical interviews"
            ],
            missing_evidence=[
                "STAR-format resume bullet points quantifying performance, scale, or user impact",
                "Pinned GitHub repository with professional README badges, architecture diagram, and license",
                "Public Orvena Project Showcase link enabled for recruiter review"
            ],
            action_checklist=[
                "Draft 3 STAR-format resume bullets: Situation, Task, Action (technologies), Result (metrics)",
                "Enable Public Visibility on your Orvena Project Showcase page",
                "Link project repository and live demo directly on LinkedIn and GitHub profile",
                "Prepare answers to standard interview prompts: 'What was your biggest architectural challenge?'"
            ],
            suggested_milestones=[
                MilestoneTemplate(title="STAR Resume Bullets & Metric Quantification", phase="Portfolio Packaging", description="Author 3 quantitative resume bullets reflecting project contributions", deliverables=["Resume bullet points"]),
                MilestoneTemplate(title="GitHub Repository & Showcase Polish", phase="Portfolio Packaging", description="Add architecture diagram, setup instructions, and enable public showcase", deliverables=["GitHub README", "Public showcase URL"]),
                MilestoneTemplate(title="Technical Interview Storyboard", phase="Portfolio Packaging", description="Document 3 engineering challenges, trade-offs made, and future improvements", deliverables=["Interview preparation storyboard"])
            ]
        ))

        # Sort pathways by score descending
        pathways.sort(key=lambda p: p.score, reverse=True)

        top_pathway = pathways[0].pathway_key
        readiness_summary = (
            f"Evaluated 6 strategic outcome pathways for '{project_title}'. "
            f"Highest alignment: {pathways[0].title} ({pathways[0].score}% readiness, {pathways[0].tier}). "
            f"Strong secondary pathway: {pathways[1].title} ({pathways[1].score}% readiness, {pathways[1].tier}). "
            "Transparent decision rules evaluated implementation maturity, documentation, testing, and differentiation. "
            "These signals provide structured recommendations and do not guarantee funding, publication acceptance, or commercial success."
        )

        return OutcomeIntelligenceResponse(
            id=uuid4(),
            project_id=project_id,
            selected_goal=student_intent,
            top_pathway=top_pathway,
            pathways=pathways,
            readiness_summary=readiness_summary,
            created_at=datetime.utcnow()
        )


project_outcome_intelligence_service = ProjectOutcomeIntelligenceService()
