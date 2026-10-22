"""
Orvena Project Launchpad: 5-Dimension Project Evaluation Engine

Implements a deterministic, rubric-based evaluation system for student projects
without requiring an LLM. Assesses projects across:
1. Problem Clarity & Relevance
2. Implementation Maturity
3. Testing & Evidence of Validation
4. Differentiation from Existing Approaches
5. Documentation, Usability & Readiness
"""
import re
from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime

from app.schemas.launchpad import (
    ProjectEvaluationRequest,
    ProjectEvaluationResponse,
    DimensionScoreResult,
    DimensionAnswer,
)

# Rubric definitions and weights for each of the 5 dimensions
DIMENSION_RUBRICS: Dict[str, Dict[str, Any]] = {
    "problem_clarity": {
        "name": "Problem Clarity & Relevance",
        "weight_max": 20.0,
        "levels": {
            0: {"score": 2.0, "status": "Vague / Unclear", "feedback": "Problem statement is undefined or generic; target users and pain points are ambiguous."},
            1: {"score": 7.0, "status": "Basic Identification", "feedback": "Identifies a broad problem area, but lacks concrete user personas or specific real-world consequences."},
            2: {"score": 13.0, "status": "Defined & Relevant", "feedback": "Clearly articulates the pain point, who suffers from it, and why existing informal workarounds fail."},
            3: {"score": 17.0, "status": "Well-Researched", "feedback": "Problem is backed by user interviews, domain metrics, or clear literature references establishing clear demand."},
            4: {"score": 20.0, "status": "Exemplary", "feedback": "Exceptional problem framing with quantified impact, target demographic boundaries, and clear success criteria."}
        }
    },
    "implementation_maturity": {
        "name": "Implementation Maturity",
        "weight_max": 20.0,
        "levels": {
            0: {"score": 3.0, "status": "Concept Only", "feedback": "Project exists primarily as an idea, wireframe, or non-functional mock."},
            1: {"score": 8.0, "status": "Early Prototype", "feedback": "Initial skeleton codebase with minimal functional user paths or placeholder responses."},
            2: {"score": 14.0, "status": "Working MVP", "feedback": "Functional core features execute end-to-end with persistent data storage and basic error handling."},
            3: {"score": 18.0, "status": "Hardened System", "feedback": "Robust architecture with modular layers, asynchronous handling, and defense against edge cases."},
            4: {"score": 20.0, "status": "Production-Grade", "feedback": "Fully deployed or packageable system with optimized queries, security controls, and clean configuration."}
        }
    },
    "testing_validation": {
        "name": "Testing & Evidence of Validation",
        "weight_max": 20.0,
        "levels": {
            0: {"score": 2.0, "status": "No Formal Verification", "feedback": "No automated tests or documented user feedback exist to verify system correctness."},
            1: {"score": 7.0, "status": "Manual Sanity Checks", "feedback": "Tested primarily via ad-hoc manual verification; edge cases remain largely unverified."},
            2: {"score": 12.0, "status": "Basic Unit Testing", "feedback": "Automated unit tests exist for critical functions, verifying standard success scenarios."},
            3: {"score": 16.0, "status": "Integration & Edge Coverage", "feedback": "Automated suite testing boundary conditions, network failures, and integration transactions with >70% coverage."},
            4: {"score": 20.0, "status": "Comprehensive Verification", "feedback": "Rigorous automated test suite, load benchmarks, and documented user trial feedback with metrics."}
        }
    },
    "differentiation": {
        "name": "Differentiation & Technical Substance",
        "weight_max": 20.0,
        "levels": {
            0: {"score": 3.0, "status": "Generic Clone", "feedback": "Direct tutorial replication with minimal original design decisions or domain adaptations."},
            1: {"score": 8.0, "status": "Minor Customization", "feedback": "Standard boilerplate application with customized styling or minor additional CRUD fields."},
            2: {"score": 13.0, "status": "Distinct Adaptation", "feedback": "Applies established tools to a tailored domain challenge with customized data workflows."},
            3: {"score": 17.0, "status": "Substantial Innovation", "feedback": "Features novel technical combinations, unique algorithms, or significantly superior UX compared to benchmarks."},
            4: {"score": 20.0, "status": "High Novelty", "feedback": "Exemplary technical innovation, potential publication candidate, or compelling proprietary competitive advantage."}
        }
    },
    "documentation_readiness": {
        "name": "Documentation, Usability & Readiness",
        "weight_max": 20.0,
        "levels": {
            0: {"score": 2.0, "status": "Minimal Documentation", "feedback": "No setup instructions, comments, or live demo; setup by external developers is difficult."},
            1: {"score": 7.0, "status": "Basic README", "feedback": "Contains simple setup steps, but lacks architecture diagrams, troubleshooting guides, or demo screenshots."},
            2: {"score": 13.0, "status": "Good Technical Overview", "feedback": "Clean README with clear installation guide, architecture overview, API schemas, and feature list."},
            3: {"score": 17.0, "status": "Showcase-Ready", "feedback": "Includes working live demo link, reproducible container configuration, and clear developer contribution guides."},
            4: {"score": 20.0, "status": "Exemplary Portfolio Standard", "feedback": "Comprehensive documentation, interactive API docs (Swagger/Postman), live demo, and video walkthrough."}
        }
    }
}


class ProjectEvaluatorService:
    """Evaluates student projects using 5 structured dimensions."""

    def validate_repository_url(self, repo_url: Optional[str]) -> Dict[str, Any]:
        """
        Validates repository URL format safely without downloading or executing external code.
        Supports GitHub, GitLab, and Bitbucket.
        """
        if not repo_url or not repo_url.strip():
            return {"is_valid": False, "provider": None, "reason": "No repository URL provided"}

        cleaned = repo_url.strip()
        github_pattern = r"^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9_\-\.]+\/[a-zA-Z0-9_\-\.]+\/?$"
        gitlab_pattern = r"^https?:\/\/(www\.)?gitlab\.com\/[a-zA-Z0-9_\-\.\/]+\/?$"
        bitbucket_pattern = r"^https?:\/\/(www\.)?bitbucket\.org\/[a-zA-Z0-9_\-\.]+\/[a-zA-Z0-9_\-\.]+\/?$"

        if re.match(github_pattern, cleaned):
            return {"is_valid": True, "provider": "GitHub", "url": cleaned}
        elif re.match(gitlab_pattern, cleaned):
            return {"is_valid": True, "provider": "GitLab", "url": cleaned}
        elif re.match(bitbucket_pattern, cleaned):
            return {"is_valid": True, "provider": "Bitbucket", "url": cleaned}
        else:
            return {
                "is_valid": False,
                "provider": "Unknown",
                "reason": "URL must be a public repository link (e.g., https://github.com/username/repo)"
            }

    def evaluate(
        self,
        project_id: Any,
        request: ProjectEvaluationRequest,
        project_data: Optional[Dict[str, Any]] = None,
        resume_project_snippet: Optional[str] = None
    ) -> ProjectEvaluationResponse:
        """
        Performs 5-dimension deterministic project evaluation.
        Handles missing answers as 'unknown' rather than zero-score failures.
        """
        dimension_results: Dict[str, DimensionScoreResult] = {}
        total_score = 0.0
        strengths: List[str] = []
        missing_evidence: List[str] = []
        improvement_priorities: List[str] = []

        # Index submitted answers by dimension_key
        submitted_answers: Dict[str, DimensionAnswer] = {
            ans.dimension_key: ans for ans in request.answers
        }

        # Validate external repo URL if provided
        repo_validation = self.validate_repository_url(request.repository_url)
        if request.repository_url and not repo_validation["is_valid"]:
            missing_evidence.append(f"Repository URL format issue: {repo_validation.get('reason')}")
        elif repo_validation["is_valid"]:
            strengths.append(f"Public code repository provided via {repo_validation['provider']}")

        # Evaluate each dimension
        for dim_key, rubric in DIMENSION_RUBRICS.items():
            dim_name = rubric["name"]
            ans = submitted_answers.get(dim_key)

            if ans is not None:
                level = max(0, min(4, ans.selected_option_level))
                level_info = rubric["levels"][level]
                score = level_info["score"]
                status_label = level_info["status"]
                feedback = level_info["feedback"]

                has_evidence = bool(ans.evidence_url or ans.notes)
                if has_evidence:
                    # Minor evidence bonus (+1.0 pt up to max 20)
                    score = min(rubric["weight_max"], score + 1.0)

                dimension_results[dim_key] = DimensionScoreResult(
                    dimension_name=dim_name,
                    score=score,
                    max_score=rubric["weight_max"],
                    status_label=status_label,
                    level=level,
                    feedback=feedback,
                    evidence_provided=has_evidence
                )
                total_score += score

                # Categorize strengths and priorities
                if level >= 3:
                    strengths.append(f"{dim_name}: {status_label} ({feedback})")
                elif level <= 1:
                    improvement_priorities.append(f"Priority: Elevate {dim_name} from '{status_label}' to working standard.")
                    missing_evidence.append(f"Missing verifiable evidence for {dim_name}")
            else:
                # Handle unanswered as Unknown (Neutral 10.0 points, flagged clearly)
                score = 10.0
                dimension_results[dim_key] = DimensionScoreResult(
                    dimension_name=dim_name,
                    score=score,
                    max_score=rubric["weight_max"],
                    status_label="Unknown / Unassessed",
                    level=2,
                    feedback="Dimension was not answered in the evaluation questionnaire; scored neutrally as unknown pending verification.",
                    evidence_provided=False
                )
                total_score += score
                missing_evidence.append(f"{dim_name} was left unassessed.")

        # Determine overall maturity rating
        total_score_clamped = round(min(100.0, max(10.0, total_score)), 1)
        if total_score_clamped >= 85:
            overall_rating = "Exemplary / Production Standard"
        elif total_score_clamped >= 70:
            overall_rating = "Functional & Validated Prototype"
        elif total_score_clamped >= 50:
            overall_rating = "Developing MVP"
        elif total_score_clamped >= 30:
            overall_rating = "Early Concept Prototype"
        else:
            overall_rating = "Preliminary Conceptual Scope"

        # Determine recommended next milestone
        if dimension_results.get("testing_validation", DimensionScoreResult(dimension_name="", score=0, max_score=20, status_label="", level=0, feedback="", evidence_provided=False)).level <= 1:
            recommended_milestone = "Implement automated test suite verifying core functional workflows and edge inputs."
        elif dimension_results.get("documentation_readiness", DimensionScoreResult(dimension_name="", score=0, max_score=20, status_label="", level=0, feedback="", evidence_provided=False)).level <= 1:
            recommended_milestone = "Author comprehensive technical README with architecture diagram, local setup, and demo GIF."
        elif dimension_results.get("implementation_maturity", DimensionScoreResult(dimension_name="", score=0, max_score=20, status_label="", level=0, feedback="", evidence_provided=False)).level <= 2:
            recommended_milestone = "Harden core implementation: add defensive input validation, transaction boundaries, and error recovery."
        else:
            recommended_milestone = "Deploy public demonstration instance and prepare portfolio showcase for career & competition review."

        reassessment_conditions = "Reassess this project after completing the next milestone or adding new verifiable evidence (e.g. unit tests, live URL, user feedback)."

        summary = (
            f"Overall Score: {total_score_clamped}/100 ({overall_rating}). "
            f"This preliminary rule-based evaluation evaluated the project across 5 engineering dimensions. "
            f"Identified {len(strengths)} key strengths and {len(improvement_priorities)} improvement opportunities. "
            "Note: This preliminary assessment cannot conclusively establish patentability, scientific peer-review publication novelty, or commercial viability."
        )

        return ProjectEvaluationResponse(
            id=uuid4(),
            project_id=project_id,
            overall_score=total_score_clamped,
            overall_rating=overall_rating,
            dimension_scores=dimension_results,
            strengths=strengths or ["Project initiated with defined title and baseline technical scope."],
            missing_evidence=missing_evidence or ["No critical evidence gaps identified."],
            improvement_priorities=improvement_priorities or ["Maintain automated testing standards as new features are added."],
            recommended_milestone=recommended_milestone,
            reassessment_conditions=reassessment_conditions,
            summary=summary,
            created_at=datetime.utcnow()
        )


project_evaluator_service = ProjectEvaluatorService()
