"""
Tests for Skill Assessor

Tests the starting-level assessment engine with evidence states.
"""
from uuid import uuid4

from app.modules.career_intelligence.types import (
    StudentFeatures, SkillEvidence, EvidenceType, 
    EvidenceState, ProficiencyLevel
)
from app.modules.career_intelligence.evidence.skill_assessor import SkillAssessor


def test_assess_beginner_level():
    """Test assessment for beginner with minimal skills."""
    assessor = SkillAssessor()
    
    features = StudentFeatures(
        interests=["programming"],
        skills=[
            SkillEvidence(
                skill_name="python",
                evidence_type=EvidenceType.DECLARED,
                evidence_state=EvidenceState.DECLARED_UNVERIFIED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description="Self-reported",
                confidence=0.3
            )
        ],
        project_count=0,
        has_projects=False
    )
    
    assessment = assessor.assess_for_role(
        "backend_engineer",
        "Backend Engineer",
        features,
        uuid4()
    )
    
    assert assessment.starting_level == "beginner"
    assert assessment.readiness_score < 0.5
    assert len(assessment.prerequisite_gaps) > 0
    assert len(assessment.next_actions) > 0
    print(f"\n[PASS] Beginner assessment: {assessment.starting_level}, Score: {assessment.readiness_score:.2f}")


def test_assess_intermediate_level():
    """Test assessment for intermediate with some demonstrated skills."""
    assessor = SkillAssessor()
    
    features = StudentFeatures(
        interests=["programming"],
        skills=[
            SkillEvidence(
                skill_name="python",
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description="Built 2 web APIs",
                confidence=0.9
            ),
            SkillEvidence(
                skill_name="sql",
                evidence_type=EvidenceType.EDUCATION,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description="Database course project",
                confidence=0.8
            ),
            SkillEvidence(
                skill_name="rest_api",
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description="Simple REST API",
                confidence=0.6
            )
        ],
        project_count=2,
        has_projects=True
    )
    
    assessment = assessor.assess_for_role(
        "backend_engineer",
        "Backend Engineer",
        features,
        uuid4()
    )
    
    assert assessment.starting_level in ["intermediate", "beginner"]
    assert assessment.readiness_score >= 0.3
    assert len(assessment.demonstrated_skills) >= 2
    assert len(assessment.strengths) > 0
    print(f"\n[PASS] Intermediate assessment: {assessment.starting_level}, Score: {assessment.readiness_score:.2f}")


def test_assess_advanced_level():
    """Test assessment for advanced with strong evidence."""
    assessor = SkillAssessor()
    
    features = StudentFeatures(
        interests=["programming"],
        skills=[
            SkillEvidence(
                skill_name="python",
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.ADVANCED,
                source_description="6 months internship building APIs",
                confidence=1.0
            ),
            SkillEvidence(
                skill_name="sql",
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.ADVANCED,
                source_description="Database design and optimization",
                confidence=0.95
            ),
            SkillEvidence(
                skill_name="rest_api",
                evidence_type=EvidenceType.WORK_EXPERIENCE,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.ADVANCED,
                source_description="Built production APIs",
                confidence=0.95
            ),
            SkillEvidence(
                skill_name="postgresql",
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description="Multiple projects",
                confidence=0.9
            )
        ],
        project_count=5,
        has_projects=True,
        has_internship=True
    )
    
    assessment = assessor.assess_for_role(
        "backend_engineer",
        "Backend Engineer",
        features,
        uuid4()
    )
    
    assert assessment.starting_level in ["advanced", "intermediate"]
    assert assessment.readiness_score >= 0.6
    assert len(assessment.demonstrated_skills) >= 3
    print(f"\n[PASS] Advanced assessment: {assessment.starting_level}, Score: {assessment.readiness_score:.2f}")


def test_distinguish_declared_vs_demonstrated():
    """Test that assessor properly separates claimed from demonstrated skills."""
    assessor = SkillAssessor()
    
    features = StudentFeatures(
        interests=["programming"],
        skills=[
            # Demonstrated with evidence
            SkillEvidence(
                skill_name="python",
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description="Built 3 projects",
                confidence=0.9
            ),
            # Declared but no proof
            SkillEvidence(
                skill_name="javascript",
                evidence_type=EvidenceType.DECLARED,
                evidence_state=EvidenceState.DECLARED_UNVERIFIED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description="Self-reported",
                confidence=0.3
            ),
            # Partially demonstrated
            SkillEvidence(
                skill_name="react",
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description="Started but incomplete project",
                confidence=0.5
            )
        ],
        project_count=3,
        has_projects=True
    )
    
    assessment = assessor.assess_for_role(
        "frontend_engineer",
        "Frontend Engineer",
        features,
        uuid4()
    )
    
    # Should separate different evidence states
    assert len(assessment.declared_unverified_skills) > 0
    assert len(assessment.partially_demonstrated_skills) > 0
    
    # Should recommend verification
    assert len(assessment.recommended_assessments) > 0
    assert any("project" in rec.lower() for rec in assessment.recommended_assessments)
    
    print(f"\n[PASS] Evidence distinction test")
    print(f"  Demonstrated: {len(assessment.demonstrated_skills)}")
    print(f"  Partially: {len(assessment.partially_demonstrated_skills)}")
    print(f"  Unverified: {len(assessment.declared_unverified_skills)}")


def test_prerequisite_gap_identification():
    """Test identification of critical prerequisite gaps."""
    assessor = SkillAssessor()
    
    features = StudentFeatures(
        interests=["data_science"],
        skills=[
            # Has Python
            SkillEvidence(
                skill_name="python",
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description="Data analysis project",
                confidence=0.8
            ),
            # Missing machine_learning (required for Data Scientist)
            # Missing pandas (required)
            # Missing statistics (required)
        ],
        project_count=1,
        has_projects=True
    )
    
    assessment = assessor.assess_for_role(
        "data_scientist",
        "Data Scientist",
        features,
        uuid4()
    )
    
    # Should identify missing required skills
    assert len(assessment.prerequisite_gaps) > 0
    assert any("machine" in gap.lower() or "pandas" in gap.lower() for gap in assessment.prerequisite_gaps)
    
    print(f"\n[PASS] Gap identification test")
    print(f"  Gaps found: {len(assessment.prerequisite_gaps)}")


def test_learning_time_estimation():
    """Test learning time estimation."""
    assessor = SkillAssessor()
    
    features = StudentFeatures(
        interests=["programming"],
        skills=[
            SkillEvidence(
                skill_name="python",
                evidence_type=EvidenceType.EDUCATION,
                evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description="Intro course",
                confidence=0.5
            )
        ],
        project_count=0,
        has_projects=False
    )
    
    assessment = assessor.assess_for_role(
        "backend_engineer",
        "Backend Engineer",
        features,
        uuid4()
    )
    
    # Estimate with 10 hours per week
    time_estimate = assessor.estimate_learning_time(assessment, target_hours_per_week=10)
    
    assert time_estimate["total_hours"] > 0
    assert time_estimate["weeks_at_current_pace"] > 0
    assert time_estimate["skills_to_develop"] >= 0
    
    print(f"\n[PASS] Learning time estimation")
    print(f"  Total hours: {time_estimate['total_hours']}")
    print(f"  Weeks needed (10h/week): {time_estimate['weeks_at_current_pace']}")
    print(f"  Skills to develop: {time_estimate['skills_to_develop']}")


def test_assessment_summary_quality():
    """Test that summary provides useful, honest information."""
    assessor = SkillAssessor()
    
    features = StudentFeatures(
        interests=["design"],
        skills=[
            SkillEvidence(
                skill_name="figma",
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description="Created 5 design mockups",
                confidence=0.9
            ),
            # Claimed but not proven - using a skill from the role requirements
            SkillEvidence(
                skill_name="ux_design",
                evidence_type=EvidenceType.DECLARED,
                evidence_state=EvidenceState.DECLARED_UNVERIFIED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description="Self-reported",
                confidence=0.3
            )
        ],
        project_count=5,
        has_projects=True
    )
    
    assessment = assessor.assess_for_role(
        "ui_ux_designer",
        "UI/UX Designer",
        features,
        uuid4()
    )
    
    # Summary should exist and be substantial
    assert len(assessment.summary) > 50
    
    # Should mention demonstrated skills
    assert "figma" in assessment.summary.lower() or "demonstrated" in assessment.summary.lower()
    
    # Should mention unverified skills
    assert "verification" in assessment.summary.lower() or "claimed" in assessment.summary.lower()
    
    # Should not fabricate skills
    assert "python" not in assessment.summary.lower()
    
    print(f"\n[PASS] Summary quality test")
    print(f"  Summary: {assessment.summary[:150]}...")


if __name__ == "__main__":
    print("Testing Skill Assessor...\n")
    
    test_assess_beginner_level()
    test_assess_intermediate_level()
    test_assess_advanced_level()
    test_distinguish_declared_vs_demonstrated()
    test_prerequisite_gap_identification()
    test_learning_time_estimation()
    test_assessment_summary_quality()
    
    print("\n[SUCCESS] All skill assessor tests passed!")
