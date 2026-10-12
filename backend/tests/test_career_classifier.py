"""
Tests for Career Classifier

Tests the rule-based baseline classifier without requiring ML models.
"""
import pytest
from uuid import uuid4

from app.modules.career_intelligence.types import (
    StudentFeatures, SkillEvidence, EvidenceType, 
    EvidenceState, ProficiencyLevel
)
from app.modules.career_intelligence.classification.classifier import CareerClassifier
from app.modules.career_intelligence.classification.role_matcher import RoleFitScorer


class TestRoleFitScorer:
    """Test the role fit scoring logic."""
    
    def test_score_frontend_engineer_with_matching_skills(self):
        """Test scoring for frontend engineer with relevant skills."""
        scorer = RoleFitScorer()
        
        # Create student features with frontend skills
        features = StudentFeatures(
            interests=["programming"],
            skills=[
                SkillEvidence(
                    skill_name="javascript",
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.INTERMEDIATE,
                    source_description="Used in 2 projects",
                    confidence=0.9
                ),
                SkillEvidence(
                    skill_name="react",
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.BEGINNER,
                    source_description="Built portfolio site",
                    confidence=0.8
                ),
                SkillEvidence(
                    skill_name="html",
                    evidence_type=EvidenceType.EDUCATION,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.INTERMEDIATE,
                    source_description="Coursework",
                    confidence=0.7
                ),
            ],
            has_projects=True,
            project_count=2,
            education_level="Bachelor",
            field_of_study="Computer Science"
        )
        
        # Score all roles
        scores = scorer.score_all_roles(features)
        
        # Find frontend engineer
        frontend_score = next(
            (s for s in scores if s.role_name == "Frontend Engineer"),
            None
        )
        
        assert frontend_score is not None
        assert frontend_score.fit_score > 0.4  # Should have reasonable fit
        assert "javascript" in frontend_score.matching_skills
        assert len(frontend_score.strengths) > 0
        assert frontend_score.reasoning  # Should have explanation
    
    def test_score_data_scientist_with_ml_skills(self):
        """Test scoring for data scientist with ML background."""
        scorer = RoleFitScorer()
        
        features = StudentFeatures(
            interests=["data_analysis", "machine_learning"],
            skills=[
                SkillEvidence(
                    skill_name="python",
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.ADVANCED,
                    source_description="Multiple data science projects",
                    confidence=0.9
                ),
                SkillEvidence(
                    skill_name="pandas",
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.INTERMEDIATE,
                    source_description="Data analysis project",
                    confidence=0.8
                ),
                SkillEvidence(
                    skill_name="machine_learning",
                    evidence_type=EvidenceType.EDUCATION,
                    evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.BEGINNER,
                    source_description="ML course project",
                    confidence=0.7
                ),
            ],
            has_projects=True,
            project_count=3,
            education_level="Bachelor",
            field_of_study="Data Science"
        )
        
        scores = scorer.score_all_roles(features)
        
        # Data Scientist should score high
        ds_score = next(
            (s for s in scores if s.role_name == "Data Scientist"),
            None
        )
        
        assert ds_score is not None
        assert ds_score.fit_score > 0.5
        assert "python" in ds_score.matching_skills
    
    def test_score_with_minimal_information(self):
        """Test scoring when very little information is available."""
        scorer = RoleFitScorer()
        
        features = StudentFeatures(
            interests=[],
            skills=[],
            has_projects=False,
            project_count=0
        )
        
        scores = scorer.score_all_roles(features)
        
        # Should still return scores but all low
        assert len(scores) > 0
        assert all(s.fit_score < 0.5 for s in scores)
        
        # Should have gaps identified
        top_score = scores[0]
        assert len(top_score.gaps) > 0
        assert len(top_score.next_steps) > 0
    
    def test_confidence_levels(self):
        """Test confidence level determination."""
        scorer = RoleFitScorer()
        
        # High confidence case
        high_conf_features = StudentFeatures(
            interests=["programming"],
            skills=[
                SkillEvidence(
                    skill_name="python",
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.ADVANCED,
                    source_description="Strong Python skills",
                    confidence=1.0
                ),
                SkillEvidence(
                    skill_name="rest_api",
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.INTERMEDIATE,
                    source_description="Built APIs",
                    confidence=0.9
                ),
                SkillEvidence(
                    skill_name="sql",
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.INTERMEDIATE,
                    source_description="Database work",
                    confidence=0.8
                ),
            ],
            has_projects=True,
            project_count=5,
            education_level="Bachelor",
            field_of_study="Computer Science"
        )
        
        scores = scorer.score_all_roles(high_conf_features)
        backend_score = next(
            (s for s in scores if s.role_name == "Backend Engineer"),
            None
        )
        
        assert backend_score is not None
        assert backend_score.confidence.value in ["high", "medium"]
    
    def test_reasoning_generation(self):
        """Test that reasoning is clear and evidence-based."""
        scorer = RoleFitScorer()
        
        features = StudentFeatures(
            interests=["design"],
            skills=[
                SkillEvidence(
                    skill_name="figma",
                    evidence_type=EvidenceType.PROJECT,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.INTERMEDIATE,
                    source_description="Design projects",
                    confidence=0.9
                ),
                SkillEvidence(
                    skill_name="ui_design",
                    evidence_type=EvidenceType.EDUCATION,
                    evidence_state=EvidenceState.DEMONSTRATED,
                    proficiency_level=ProficiencyLevel.BEGINNER,
                    source_description="Design course",
                    confidence=0.7
                ),
            ],
            has_projects=True,
            project_count=2
        )
        
        scores = scorer.score_all_roles(features)
        designer_score = next(
            (s for s in scores if "Designer" in s.role_name),
            None
        )
        
        assert designer_score is not None
        assert len(designer_score.reasoning) > 50  # Should be substantial
        assert "figma" in designer_score.reasoning.lower() or "design" in designer_score.reasoning.lower()
        
        # Should not claim unverified skills
        assert "python" not in designer_score.reasoning.lower()


def test_classifier_version():
    """Test that classifier has version information."""
    classifier = CareerClassifier()
    assert classifier.version
    assert classifier.classifier_type == "rule_based"


def test_classifier_identifies_missing_information():
    """Test identification of missing information."""
    classifier = CareerClassifier()
    
    # Minimal features
    features = StudentFeatures(
        interests=[],
        skills=[],
        project_count=0
    )
    
    missing = classifier._identify_missing_information(features)
    
    assert len(missing) > 0
    assert any("interests" in m.lower() for m in missing)
    assert any("skills" in m.lower() for m in missing)


def test_classifier_generates_followup_questions():
    """Test generation of follow-up questions."""
    classifier = CareerClassifier()
    
    missing_info = [
        "Career interests",
        "Demonstrated skills"
    ]
    
    questions = classifier._generate_followup_questions([], missing_info)
    
    assert len(questions) > 0
    assert any("interest" in q.lower() or "work" in q.lower() for q in questions)


if __name__ == "__main__":
    # Run a simple test
    print("Testing Career Classifier...")
    
    scorer = RoleFitScorer()
    features = StudentFeatures(
        interests=["programming", "data_analysis"],
        skills=[
            SkillEvidence(
                skill_name="python",
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description="Built data analysis project",
                confidence=0.8
            )
        ],
        project_count=1,
        education_level="Bachelor",
        field_of_study="Computer Science"
    )
    
    scores = scorer.score_all_roles(features)
    
    print(f"\nTop 5 Career Matches:")
    for i, score in enumerate(scores[:5], 1):
        print(f"\n{i}. {score.role_name} (Score: {score.fit_score:.2f}, Confidence: {score.confidence.value})")
        print(f"   Matching Skills: {', '.join(score.matching_skills[:3])}")
        print(f"   Reasoning: {score.reasoning[:150]}...")
    
    print("\n[SUCCESS] Classifier test completed successfully!")
