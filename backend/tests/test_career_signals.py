from app.services.career_recommendation_service import CareerRecommendationService
from app.services.career_signals import extract_skill_evidence, infer_preferred_roles


def test_everyday_discovery_answer_matches_multiple_role_paths():
    answer = (
        "I am a third-year IT student who wants to become a top AI and full stack developer. "
        "I enjoy programming, building web apps, training computer vision models, and solving technical problems."
    )
    roles = infer_preferred_roles(answer)

    assert "Full-Stack Developer" in roles
    assert "Machine Learning Engineer" in roles
    assert "Software Engineer" in roles


def test_resume_and_answers_expand_to_evidenced_skill_categories():
    evidence = extract_skill_evidence(
        "React, Django REST Framework, PostgreSQL, PyTorch for computer vision, Wireshark for network security, and I led a team."
    )

    assert {"react", "backend", "api design", "database", "computer vision", "networking", "security", "leadership"} <= set(evidence)


def test_fallback_roadmap_has_ordered_weeks_and_actionable_project_depth():
    plan = CareerRecommendationService()._parse_roadmap(
        "",
        "Software Engineer",
        12,
        ["python", "react", "sql"],
        "Q: What do you want to build?\nA: I want to combine AI and full stack development.",
    )

    assert len(plan["milestones"]) == 6
    assert "Weeks 1-2" in plan["milestones"][0]["description"]
    assert "Weeks 11-12" in plan["milestones"][5]["description"]
    assert "Project depth checklist" in plan["milestones"][4]["description"]
    assert "Machine Learning Engineer" in plan["milestones"][0]["description"]
    assert "full-stack" in plan["milestones"][4]["description"].lower()
