"""
Unit & Integration Tests for Orvena Project Launchpad & Orvena Guide

Tests:
1. Project idea filtering and ranking with deterministic scores and explanations
2. Plan generation with phase breakdown and MVP scope bounds
3. 5-dimension project evaluation, scoring rubrics, unanswered questions handling
4. Project outcome intelligence across all 6 strategic pathways
5. Opportunities directory filtering, verification fields, and deadlines
6. Orvena Guide intent recognition, navigation actions, context-awareness, and fallback
"""
import pytest
from uuid import uuid4

from app.schemas.launchpad import (
    IdeaRecommendationRequest,
    PlanGenerationRequest,
    ProjectEvaluationRequest,
    DimensionAnswer,
)
from app.services.launchpad_ideas import project_ideas_service, PROJECT_IDEAS_CATALOGUE
from app.services.launchpad_planner import project_planner_service
from app.services.launchpad_evaluator import project_evaluator_service, DIMENSION_RUBRICS
from app.services.launchpad_outcomes import project_outcome_intelligence_service
from app.services.launchpad_opportunities import project_opportunities_service, CURATED_OPPORTUNITIES
from app.services.orvena_guide_engine import orvena_guide_engine
from app.schemas.guide import GuideChatRequest


# -------------------------------------------------------------
# 1. Project Ideas & Rule-Based Recommendation Tests
# -------------------------------------------------------------
def test_catalogue_contains_valid_ideas():
    ideas = project_ideas_service.list_ideas()
    assert len(ideas) >= 8
    for idea in ideas:
        assert idea.id
        assert idea.title
        assert idea.problem_statement
        assert idea.domain
        assert idea.difficulty in ["beginner", "intermediate", "advanced"]
        assert len(idea.prerequisites) > 0
        assert len(idea.recommended_technologies) > 0
        assert len(idea.suggested_milestones) >= 3


def test_idea_domain_and_difficulty_filtering():
    ai_ideas = project_ideas_service.list_ideas(domain="AI / Machine Learning")
    assert all("AI / Machine Learning" in i.domain for i in ai_ideas)

    adv_ideas = project_ideas_service.list_ideas(difficulty="advanced")
    assert all(i.difficulty == "advanced" for i in adv_ideas)


def test_career_aware_recommendation_scoring():
    request = IdeaRecommendationRequest(
        target_domain="AI / Machine Learning",
        difficulty_preference="intermediate",
        weekly_hours_available=10,
        primary_objective="portfolio",
        preferred_technologies=["Python", "FastAPI"],
        target_career_roles=["Machine Learning Engineer"],
        existing_skills=["Python", "Vector Databases", "React"]
    )
    results = project_ideas_service.recommend_ideas(
        request=request,
        career_interests=["Machine Learning Engineer", "Data Scientist"],
        student_skills=["Python", "FastAPI", "React"]
    )
    assert len(results) > 0
    top = results[0]
    assert top.match_score is not None
    assert top.match_score >= 70
    assert top.match_explanation is not None
    assert "known skills" in top.match_explanation.lower() or "target career" in top.match_explanation.lower()


# -------------------------------------------------------------
# 2. Structured Project Planning Tests
# -------------------------------------------------------------
def test_plan_generation_bounds_and_phases():
    req = PlanGenerationRequest(
        title="Automated Medical Triage Assistant",
        problem_statement="Emergency clinics face long queues and delayed triage categorization.",
        intended_users="Triage nurses and clinic patients",
        proposed_solution="Mobile-first questionnaire calculating emergency severity index.",
        domain="HealthTech & BioInformatics",
        technologies=["TypeScript", "Next.js", "PostgreSQL"],
        current_stage="idea",
        weekly_hours=10,
        target_duration_weeks=8,
        primary_goal="portfolio"
    )
    plan = project_planner_service.generate_plan(req)
    assert plan.title == req.title
    assert len(plan.minimum_viable_scope) >= 3
    assert len(plan.future_scope) >= 3
    assert len(plan.phases) == 4
    assert plan.phases[0].target_week_start == 1
    assert plan.phases[-1].target_week_end == 8
    assert len(plan.suggested_milestones) == 4
    assert len(plan.risks_and_dependencies) >= 3


# -------------------------------------------------------------
# 3. 5-Dimension Evaluation Tests
# -------------------------------------------------------------
def test_evaluation_scoring_and_unanswered_handling():
    project_id = uuid4()
    # Provide answers for 3 dimensions, leave 2 unassessed
    req = ProjectEvaluationRequest(
        answers=[
            DimensionAnswer(dimension_key="problem_clarity", selected_option_level=3, notes="Validated with 5 users"),
            DimensionAnswer(dimension_key="implementation_maturity", selected_option_level=2),
            DimensionAnswer(dimension_key="testing_validation", selected_option_level=1)
        ],
        repository_url="https://github.com/teststudent/sample-project"
    )
    res = project_evaluator_service.evaluate(project_id, req)
    assert res.project_id == project_id
    assert 0 <= res.overall_score <= 100
    assert len(res.dimension_scores) == 5
    
    # Check that answered dimension has evidence recorded
    assert res.dimension_scores["problem_clarity"].evidence_provided is True
    assert res.dimension_scores["problem_clarity"].score > 15

    # Check unassessed dimension is treated as neutral/unknown, NOT zero
    unassessed = res.dimension_scores["differentiation"]
    assert unassessed.status_label == "Unknown / Unassessed"
    assert unassessed.score == 10.0

    # Strengths and priorities populated
    assert len(res.strengths) > 0
    assert len(res.improvement_priorities) > 0
    assert res.recommended_milestone is not None


def test_repository_url_security_validation():
    # Valid GitHub
    v1 = project_evaluator_service.validate_repository_url("https://github.com/torvalds/linux")
    assert v1["is_valid"] is True
    assert v1["provider"] == "GitHub"

    # Valid GitLab
    v2 = project_evaluator_service.validate_repository_url("https://gitlab.com/gitlab-org/gitlab")
    assert v2["is_valid"] is True
    assert v2["provider"] == "GitLab"

    # Invalid / untrusted input format
    v3 = project_evaluator_service.validate_repository_url("ftp://malicious-server.com/script.sh")
    assert v3["is_valid"] is False


# -------------------------------------------------------------
# 4. Project Outcome Intelligence Tests
# -------------------------------------------------------------
def test_outcome_intelligence_pathways():
    project_id = uuid4()
    out = project_outcome_intelligence_service.analyze_outcomes(
        project_id=project_id,
        project_title="Distributed Key-Value Store",
        project_stage="validation",
        domain="Cloud & DevOps",
        primary_goal="research",
        technologies=["Go", "Raft", "gRPC", "Docker"],
        evaluation_scores={
            "dimension_scores": {
                "problem_clarity": {"score": 18.0},
                "implementation_maturity": {"score": 19.0},
                "testing_validation": {"score": 17.0},
                "differentiation": {"score": 18.0},
                "documentation_readiness": {"score": 16.0}
            }
        },
        has_repo=True,
        has_demo=True
    )
    assert out.project_id == project_id
    assert len(out.pathways) == 6
    pathway_keys = [p.pathway_key for p in out.pathways]
    assert "PRODUCT_DEVELOPMENT" in pathway_keys
    assert "RESEARCH_AND_PUBLICATION" in pathway_keys
    assert "STARTUP_AND_COMMERCIALISATION" in pathway_keys
    assert "COMPETITIONS_AND_HACKATHONS" in pathway_keys
    assert "CAREER_AND_PORTFOLIO" in pathway_keys

    # High maturity project should have Ready or Near-Ready tier
    top = out.pathways[0]
    assert top.tier in ["Ready", "Near-Ready"]
    assert top.score >= 70
    assert len(top.action_checklist) >= 3
    assert len(top.suggested_milestones) >= 2


# -------------------------------------------------------------
# 5. Opportunities Directory Tests
# -------------------------------------------------------------
def test_curated_opportunities_have_verified_sources():
    opps = project_opportunities_service.list_opportunities()
    assert len(opps) >= 6
    for opp in opps:
        assert opp.title
        assert opp.provider
        assert opp.official_url.startswith("http")
        assert opp.beneficiary_type in ["individual_student", "student_team", "institution", "registered_startup"]
        assert opp.is_verified is True
        assert opp.date_last_verified is not None


def test_opportunities_filtering():
    hackathons = project_opportunities_service.list_opportunities(opportunity_type="hackathon")
    assert all(h.opportunity_type == "hackathon" for h in hackathons)

    grants = project_opportunities_service.list_opportunities(opportunity_type="grant")
    assert all(g.opportunity_type == "grant" for g in grants)


# -------------------------------------------------------------
# 6. Orvena Guide Rule-Based Engine Tests
# -------------------------------------------------------------
def test_guide_getting_started_intent():
    req = GuideChatRequest(message="Hello, I'm new here. How does Orvena work?")
    res = orvena_guide_engine.process_query(req)
    assert res.matched_intent == "GETTING_STARTED"
    assert res.confidence >= 0.8
    assert len(res.suggested_actions) > 0
    # Must point to valid platform paths
    assert any(a.href == "/career/discovery" for a in res.suggested_actions)


def test_guide_resume_intent():
    req = GuideChatRequest(message="How do I get my resume checked for ATS?")
    res = orvena_guide_engine.process_query(req)
    assert res.matched_intent == "RESUME_ANALYSIS"
    assert any(a.href == "/resume" for a in res.suggested_actions)


def test_guide_project_launchpad_intent():
    req = GuideChatRequest(message="Can you suggest some project ideas for my portfolio?")
    res = orvena_guide_engine.process_query(req)
    assert res.matched_intent in ["PROJECT_IDEA_DISCOVERY", "PROJECT_LAUNCHPAD_OVERVIEW"]
    assert any("/projects" in a.href for a in res.suggested_actions)


def test_guide_competitions_and_funding_intent():
    req = GuideChatRequest(message="Where can I find student hackathons or grants for my project?")
    res = orvena_guide_engine.process_query(req)
    assert res.matched_intent == "OPPORTUNITIES_DIRECTORY"
    assert any(a.href == "/projects/opportunities" for a in res.suggested_actions)


def test_guide_unknown_query_fallback():
    req = GuideChatRequest(message="What is the weather on Mars today?")
    res = orvena_guide_engine.process_query(req)
    assert res.matched_intent == "UNKNOWN_FALLBACK"
    assert "Orvena Guide" in res.reply
    assert len(res.suggested_actions) > 0
    assert len(res.suggested_prompts) > 0
