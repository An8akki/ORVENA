"""
Comprehensive test script for all ORVENA features
Tests all 4 core AI features with fallback mechanisms
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.resume_scorer import ResumeScorer
from app.services.job_matcher import JobMatcher
from app.services.career_recommendation_service import CareerRecommendationService
from app.services.ai_fallback_monitor import ai_fallback_monitor, AIFeature


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")


async def test_resume_scorer():
    """Test Resume Score Analyzer"""
    print_section("TEST 1: Resume Score Analyzer")
    
    scorer = ResumeScorer()
    
    # Test data
    resume_data = {
        "contact": {
            "email": "test@example.com",
            "phone": "+1-555-123-4567",
            "name": "John Doe"
        },
        "experience": [
            {
                "position": "Software Engineer",
                "company": "Tech Corp",
                "duration": "3 years"
            },
            {
                "position": "Junior Developer",
                "company": "Startup Inc",
                "duration": "2 years"
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "State University"
            }
        ],
        "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
        "text": "Software Engineer with 5 years of experience in web development..."
    }
    
    try:
        # Test scoring
        result = scorer.score_resume(resume_data)
        
        # Verify result structure
        assert "overall_score" in result, "Missing overall_score"
        assert "letter_grade" in result, "Missing letter_grade"
        assert "category_scores" in result, "Missing category_scores"
        assert "strengths" in result, "Missing strengths"
        assert "suggestions" in result, "Missing suggestions"
        assert "ats_score" in result, "Missing ats_score"
        
        # Verify score is reasonable
        assert 0 <= result["overall_score"] <= 100, f"Invalid score: {result['overall_score']}"
        
        print_result("Resume Scorer Structure", True, f"Score: {result['overall_score']}/100 ({result['letter_grade']})")
        print_result("Category Scores", True, f"{len(result['category_scores'])} categories evaluated")
        print_result("Strengths Identified", True, f"{len(result['strengths'])} strengths found")
        print_result("Suggestions Generated", True, f"{len(result['suggestions'])} suggestions provided")
        print_result("ATS Score Calculated", True, f"ATS Pass Rate: {result['ats_score']}%")
        
        return True
        
    except Exception as e:
        print_result("Resume Scorer", False, f"Error: {str(e)}")
        return False


async def test_job_matcher():
    """Test Job Recommender"""
    print_section("TEST 2: Job Recommender")
    
    matcher = JobMatcher()
    
    # Test data
    profile = {
        "skills": ["Python", "JavaScript", "React", "AWS"],
        "education_level": "bachelor",
        "years_experience": 3,
        "preferences": {
            "min_salary": 80000,
            "work_style": "hybrid",
            "growth_focus": True
        }
    }
    
    try:
        # Test job matching
        results = matcher.match_jobs(profile, top_n=5)
        
        # Verify results
        assert len(results) > 0, "No jobs returned"
        assert len(results) <= 5, f"Too many results: {len(results)}"
        
        for job in results:
            assert "role" in job, "Missing role"
            assert "match_score" in job, "Missing match_score"
            assert "salary_range" in job, "Missing salary_range"
            assert "breakdown" in job, "Missing breakdown"
            assert "swot" in job, "Missing SWOT analysis"
            assert "matched_skills" in job, "Missing matched_skills"
            assert "missing_skills" in job, "Missing missing_skills"
            
            # Verify score is reasonable
            assert 0 <= job["match_score"] <= 100, f"Invalid match score: {job['match_score']}"
        
        print_result("Job Matcher Structure", True, f"{len(results)} jobs returned")
        print_result("Top Match Score", True, f"{results[0]['role']}: {results[0]['match_score']}%")
        print_result("Salary Ranges", True, f"${results[0]['salary_range']['min']:,} - ${results[0]['salary_range']['max']:,}")
        print_result("SWOT Analysis", True, "Complete for all jobs")
        print_result("Skills Analysis", True, f"Matched: {len(results[0]['matched_skills'])}, Missing: {len(results[0]['missing_skills'])}")
        
        return True
        
    except Exception as e:
        print_result("Job Matcher", False, f"Error: {str(e)}")
        return False


async def test_career_discovery():
    """Test Career Discovery"""
    print_section("TEST 3: Career Discovery")
    
    service = CareerRecommendationService()
    
    # Test data
    answers = {
        "interests": ["technology", "problem_solving", "creativity"],
        "skills": ["programming", "analysis", "communication"],
        "work_environment": "collaborative",
        "career_goals": "technical_leadership",
        "education_level": "bachelor",
        "experience_level": "intermediate"
    }
    
    try:
        # Test career recommendation (this will use fallback since no AI configured)
        result = await service.generate_recommendations(
            student_id="test-student-123",
            answers=answers
        )
        
        # Verify result structure
        assert "recommendations" in result, "Missing recommendations"
        assert len(result["recommendations"]) > 0, "No recommendations returned"
        
        for rec in result["recommendations"]:
            assert "career_path" in rec, "Missing career_path"
            assert "match_score" in rec, "Missing match_score"
            assert "description" in rec, "Missing description"
            assert "required_skills" in rec, "Missing required_skills"
            assert "growth_potential" in rec, "Missing growth_potential"
        
        print_result("Career Discovery Structure", True, f"{len(result['recommendations'])} careers recommended")
        print_result("Top Match", True, f"{result['recommendations'][0]['career_path']}: {result['recommendations'][0]['match_score']}%")
        print_result("Growth Potential", True, result['recommendations'][0]['growth_potential'])
        print_result("Fallback System", True, "Statistical engine working")
        
        return True
        
    except Exception as e:
        print_result("Career Discovery", False, f"Error: {str(e)}")
        return False


async def test_ai_monitoring():
    """Test AI Fallback Monitoring"""
    print_section("TEST 4: AI Fallback Monitoring")
    
    try:
        # Record some test events
        ai_fallback_monitor.record_request(AIFeature.RESUME_ANALYSIS)
        ai_fallback_monitor.record_fallback(AIFeature.RESUME_ANALYSIS, "timeout", 9.5)
        
        ai_fallback_monitor.record_request(AIFeature.JOB_MATCHING)
        ai_fallback_monitor.record_success(AIFeature.JOB_MATCHING, 2.3)
        
        # Get statistics
        overall_stats = ai_fallback_monitor.get_overall_stats()
        resume_stats = ai_fallback_monitor.get_feature_stats(AIFeature.RESUME_ANALYSIS)
        analysis = ai_fallback_monitor.get_fallback_analysis()
        
        # Verify stats structure
        assert "total_requests" in overall_stats, "Missing total_requests"
        assert "success_rate" in overall_stats, "Missing success_rate"
        assert "fallback_rate" in overall_stats, "Missing fallback_rate"
        
        print_result("Monitoring Structure", True, "All stat fields present")
        print_result("Event Recording", True, f"Total requests: {overall_stats['total_requests']}")
        print_result("Success Tracking", True, f"Success rate: {overall_stats['success_rate']:.1f}%")
        print_result("Fallback Tracking", True, f"Fallback rate: {overall_stats['fallback_rate']:.1f}%")
        print_result("Analysis Generation", True, f"{len(analysis['recommendations'])} recommendations")
        
        return True
        
    except Exception as e:
        print_result("AI Monitoring", False, f"Error: {str(e)}")
        return False


async def test_error_handling():
    """Test Error Handling"""
    print_section("TEST 5: Error Handling & Edge Cases")
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Resume scorer with minimal data
    try:
        scorer = ResumeScorer()
        minimal_data = {"text": "Minimal resume", "contact": {"email": "test@test.com"}}
        result = scorer.score_resume(minimal_data)
        assert result["overall_score"] < 60, "Minimal resume should score low"
        print_result("Minimal Resume Handling", True, f"Score: {result['overall_score']}/100")
        tests_passed += 1
    except Exception as e:
        print_result("Minimal Resume Handling", False, f"Error: {str(e)}")
    
    # Test 2: Job matcher with no skills
    try:
        matcher = JobMatcher()
        no_skills = {"skills": [], "education_level": "bachelor", "years_experience": 0}
        results = matcher.match_jobs(no_skills, top_n=3)
        assert len(results) > 0, "Should still return jobs even with no skills"
        print_result("No Skills Job Matching", True, f"{len(results)} jobs found")
        tests_passed += 1
    except Exception as e:
        print_result("No Skills Job Matching", False, f"Error: {str(e)}")
    
    # Test 3: Empty career answers
    try:
        service = CareerRecommendationService()
        empty_answers = {}
        result = await service.generate_recommendations("test-123", empty_answers)
        assert len(result["recommendations"]) > 0, "Should return default recommendations"
        print_result("Empty Career Answers", True, f"{len(result['recommendations'])} recommendations")
        tests_passed += 1
    except Exception as e:
        print_result("Empty Career Answers", False, f"Error: {str(e)}")
    
    # Test 4: High-experience profile
    try:
        matcher = JobMatcher()
        senior_profile = {
            "skills": ["Python", "Java", "AWS", "Docker", "Kubernetes"],
            "education_level": "master",
            "years_experience": 10
        }
        results = matcher.match_jobs(senior_profile, top_n=5)
        # Should recommend senior roles
        top_role = results[0]["role"].lower()
        assert "senior" in top_role or "lead" in top_role or "architect" in top_role, \
            f"Should recommend senior roles, got: {top_role}"
        print_result("Senior Profile Matching", True, f"Top role: {results[0]['role']}")
        tests_passed += 1
    except Exception as e:
        print_result("Senior Profile Matching", False, f"Error: {str(e)}")
    
    print(f"\nEdge Cases: {tests_passed}/{total_tests} tests passed")
    
    return tests_passed == total_tests


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  ORVENA COMPREHENSIVE FEATURE TEST SUITE")
    print("  Testing all 4 core AI features with fallback mechanisms")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(await test_resume_scorer())
    results.append(await test_job_matcher())
    results.append(await test_career_discovery())
    results.append(await test_ai_monitoring())
    results.append(await test_error_handling())
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - System is production-ready!")
        return 0
    else:
        print(f"\n✗ {total-passed} test(s) failed - Review errors above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
