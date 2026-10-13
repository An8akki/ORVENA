from app.services.job_matcher import job_matcher


def test_statistical_fallback_returns_ranked_roles_without_profile_data():
    recommendations = job_matcher.match_jobs(
        profile={},
        skills=[],
        education=[],
        experience=[],
    )

    assert recommendations
    assert len(recommendations) <= 8
    scores = [item["fit_score"] for item in recommendations]
    assert scores == sorted(scores, reverse=True)
    assert all(item["role_name"] and item["reasoning"] for item in recommendations)
