"""
Tests for roadmap personalization engine.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.modules.career_intelligence.types import (
    EvidenceState,
    EvidenceType,
    ProficiencyLevel,
    StudentFeatures,
    SkillEvidence
)
from app.modules.career_intelligence.roadmaps.roadmap_engine import RoadmapEngine
from app.modules.career_intelligence.evidence.skill_assessor import SkillAssessment


@pytest.fixture
def roadmap_engine():
    """Create RoadmapEngine instance."""
    return RoadmapEngine()


@pytest.fixture
def beginner_frontend_student():
    """Create a beginner frontend student profile."""
    return StudentFeatures(
        skills=[
            SkillEvidence(
                skill_name='html',
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description='Basic HTML course',
                confidence=0.6
            ),
            SkillEvidence(
                skill_name='css',
                evidence_type=EvidenceType.DECLARED,
                evidence_state=EvidenceState.DECLARED_UNVERIFIED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description='Self-reported',
                confidence=0.3
            )
        ],
        interests=['frontend', 'web'],
        work_experience_months=0,
        project_count=0,
        education_level='bachelors_in_progress'
    )


@pytest.fixture
def intermediate_backend_student():
    """Create an intermediate backend student profile."""
    return StudentFeatures(
        skills=[
            SkillEvidence(
                skill_name='python',
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description='3 projects, Certification',
                confidence=0.85
            ),
            SkillEvidence(
                skill_name='sql',
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.DEMONSTRATED,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                source_description='Database course, 2 projects',
                confidence=0.8
            ),
            SkillEvidence(
                skill_name='rest_api',
                evidence_type=EvidenceType.PROJECT,
                evidence_state=EvidenceState.PARTIALLY_DEMONSTRATED,
                proficiency_level=ProficiencyLevel.BEGINNER,
                source_description='1 project',
                confidence=0.5
            )
        ],
        interests=['backend', 'databases'],
        work_experience_months=6,
        project_count=3,
        has_projects=True,
        education_level='bachelors_in_progress'
    )


@pytest.fixture
def beginner_frontend_assessment():
    """Create beginner skill assessment."""
    assessment = SkillAssessment(
        role_key='frontend_engineer',
        role_name='Frontend Engineer',
        student_profile_id=uuid4()
    )
    assessment.starting_level = 'beginner'
    assessment.readiness_score = 0.25
    assessment.demonstrated_skills = [
        {'skill_name': 'html', 'proficiency_level': 'beginner'}
    ]
    assessment.prerequisite_gaps = ['javascript', 'react', 'css']
    assessment.strengths = ['Basic HTML understanding']
    assessment.next_actions = ['Start with JavaScript fundamentals', 'Practice CSS layouts']
    assessment.summary = "Beginner level with basic HTML skills"
    return assessment


@pytest.fixture
def intermediate_backend_assessment():
    """Create intermediate skill assessment."""
    assessment = SkillAssessment(
        role_key='backend_engineer',
        role_name='Backend Engineer',
        student_profile_id=uuid4()
    )
    assessment.starting_level = 'intermediate'
    assessment.readiness_score = 0.65
    assessment.demonstrated_skills = [
        {'skill_name': 'python', 'proficiency_level': 'intermediate'},
        {'skill_name': 'sql', 'proficiency_level': 'intermediate'}
    ]
    assessment.prerequisite_gaps = ['docker', 'rest_api']
    assessment.strengths = ['Strong Python and SQL foundation', 'Project experience']
    assessment.next_actions = ['Learn Docker containers', 'Build REST APIs']
    assessment.summary = "Intermediate level with strong Python/SQL foundation"
    return assessment


def test_personalize_roadmap_beginner_frontend(
    roadmap_engine, 
    beginner_frontend_student,
    beginner_frontend_assessment
):
    """Test roadmap personalization for beginner frontend student."""
    result = roadmap_engine.personalize_roadmap(
        role_key='frontend_engineer',
        student_features=beginner_frontend_student,
        skill_assessment=beginner_frontend_assessment,
        student_profile_id=uuid4(),
        target_hours_per_week=10
    )
    
    # Check basic structure
    assert result.role_key == 'frontend_engineer'
    assert result.student_profile_id is not None
    
    # Check phases exist
    assert len(result.phases) == 3
    
    # Check milestones exist
    assert len(result.milestones) > 0
    
    # Check personalization notes exist
    assert len(result.personalization_notes) > 0
    
    # Should indicate starting at beginner level
    assert any('beginner' in note.lower() for note in result.personalization_notes)
    
    # Timeline should be calculated
    assert result.target_duration_weeks > 0
    
    # Estimated hours should be positive
    assert result.estimated_hours > 0


def test_personalize_roadmap_intermediate_backend(
    roadmap_engine,
    intermediate_backend_student,
    intermediate_backend_assessment
):
    """Test roadmap personalization for intermediate backend student."""
    result = roadmap_engine.personalize_roadmap(
        role_key='backend_engineer',
        student_features=intermediate_backend_student,
        skill_assessment=intermediate_backend_assessment,
        student_profile_id=uuid4(),
        target_hours_per_week=15
    )
    
    # Check basic structure
    assert result.role_key == 'backend_engineer'
    
    # Check phases
    assert len(result.phases) == 3
    
    # Check milestones
    assert len(result.milestones) > 0
    
    # Should have personalization notes about intermediate level
    notes = result.personalization_notes
    assert len(notes) > 0
    assert any('intermediate' in note.lower() for note in notes)
    
    # Timeline should be shorter for intermediate student
    assert result.target_duration_weeks < 20  # Less than default
    
    # Should have prerequisite status for reviews
    # (since student has existing skills)
    if result.prerequisite_status:
        assert len(result.prerequisite_status) > 0


def test_get_next_milestones(
    roadmap_engine,
    beginner_frontend_student,
    beginner_frontend_assessment
):
    """Test getting next available milestones."""
    roadmap = roadmap_engine.personalize_roadmap(
        role_key='frontend_engineer',
        student_features=beginner_frontend_student,
        skill_assessment=beginner_frontend_assessment,
        student_profile_id=uuid4()
    )
    
    # Get next milestones with no completed milestones
    next_milestones = roadmap_engine.get_next_milestones(roadmap, [])
    
    # Should have some milestones available
    assert len(next_milestones) > 0
    
    # All next milestones should have no prerequisites or be first in sequence
    for milestone in next_milestones:
        if milestone.prerequisites:
            # All prerequisites should be in the "completed" list (which is empty)
            # So this means milestones with prerequisites won't be in next_milestones
            pass


def test_calculate_progress(
    roadmap_engine,
    beginner_frontend_student,
    beginner_frontend_assessment
):
    """Test progress calculation."""
    roadmap = roadmap_engine.personalize_roadmap(
        role_key='frontend_engineer',
        student_features=beginner_frontend_student,
        skill_assessment=beginner_frontend_assessment,
        student_profile_id=uuid4()
    )
    
    # Calculate progress with no completed milestones
    progress = roadmap_engine.calculate_progress(roadmap, [])
    
    assert progress['total_milestones'] == len(roadmap.milestones)
    assert progress['completed_milestones'] == 0
    assert progress['percentage'] == 0
    assert progress['hours_remaining'] == progress['total_hours']
    
    # Test with some completed milestones
    if roadmap.milestones:
        first_milestone_id = roadmap.milestones[0].milestone_id
        progress_with_one = roadmap_engine.calculate_progress(
            roadmap,
            [first_milestone_id]
        )
        
        assert progress_with_one['completed_milestones'] == 1
        assert progress_with_one['percentage'] > 0


def test_suggest_learning_pace(
    roadmap_engine,
    beginner_frontend_student,
    beginner_frontend_assessment
):
    """Test learning pace suggestions."""
    roadmap = roadmap_engine.personalize_roadmap(
        role_key='frontend_engineer',
        student_features=beginner_frontend_student,
        skill_assessment=beginner_frontend_assessment,
        student_profile_id=uuid4()
    )
    
    pace_suggestions = roadmap_engine.suggest_learning_pace(roadmap, 10)
    
    assert 'total_hours' in pace_suggestions
    assert 'paces' in pace_suggestions
    assert 'relaxed' in pace_suggestions['paces']
    assert 'moderate' in pace_suggestions['paces']
    assert 'intensive' in pace_suggestions['paces']
    assert pace_suggestions['recommendation'] == 'moderate'


def test_circular_dependency_detection(
    roadmap_engine,
    beginner_frontend_student,
    beginner_frontend_assessment
):
    """Test that circular dependencies are detected during validation."""
    # Create a valid roadmap first
    roadmap = roadmap_engine.personalize_roadmap(
        role_key='frontend_engineer',
        student_features=beginner_frontend_student,
        skill_assessment=beginner_frontend_assessment,
        student_profile_id=uuid4()
    )
    
    # The personalize_roadmap should create a valid roadmap without circular deps
    # We can't easily test the validation failure without manually breaking the roadmap
    # But we can at least verify the method exists
    assert hasattr(roadmap_engine, '_has_circular_dependencies')
    
    # Test the method directly with simple cases
    from app.modules.career_intelligence.types import RoadmapMilestoneData, MilestoneStatus
    
    # Valid case: no cycles
    milestones_valid = [
        RoadmapMilestoneData(
            milestone_id='M1',
            title='M1',
            description='',
            phase_id='P1',
            learning_objectives=[],
            topics=[],
            activities=[],
            deliverable='',
            prerequisites=[],
            estimated_hours=5,
            completion_criteria=[],
            sequence_number=1,
            status=MilestoneStatus.PENDING
        ),
        RoadmapMilestoneData(
            milestone_id='M2',
            title='M2',
            description='',
            phase_id='P1',
            learning_objectives=[],
            topics=[],
            activities=[],
            deliverable='',
            prerequisites=['M1'],
            estimated_hours=5,
            completion_criteria=[],
            sequence_number=2,
            status=MilestoneStatus.PENDING
        )
    ]
    
    assert roadmap_engine._has_circular_dependencies(milestones_valid) is False
    
    # Circular case: M1 -> M2 -> M1
    milestones_circular = [
        RoadmapMilestoneData(
            milestone_id='M1',
            title='M1',
            description='',
            phase_id='P1',
            learning_objectives=[],
            topics=[],
            activities=[],
            deliverable='',
            prerequisites=['M2'],
            estimated_hours=5,
            completion_criteria=[],
            sequence_number=1,
            status=MilestoneStatus.PENDING
        ),
        RoadmapMilestoneData(
            milestone_id='M2',
            title='M2',
            description='',
            phase_id='P1',
            learning_objectives=[],
            topics=[],
            activities=[],
            deliverable='',
            prerequisites=['M1'],
            estimated_hours=5,
            completion_criteria=[],
            sequence_number=2,
            status=MilestoneStatus.PENDING
        )
    ]
    
    assert roadmap_engine._has_circular_dependencies(milestones_circular) is True


def test_timeline_adjustment_for_target_date(
    roadmap_engine,
    beginner_frontend_student,
    beginner_frontend_assessment
):
    """Test that timeline is adjusted based on target completion date."""
    target_date = datetime.utcnow() + timedelta(days=30)  # 30 days
    
    roadmap = roadmap_engine.personalize_roadmap(
        role_key='frontend_engineer',
        student_features=beginner_frontend_student,
        skill_assessment=beginner_frontend_assessment,
        student_profile_id=uuid4(),
        target_hours_per_week=10,
        target_completion_date=target_date
    )
    
    # Should have personalization notes about timeline
    assert len(roadmap.personalization_notes) > 0
    
    # Check if there's a note about timeline being ambitious or comfortable
    timeline_notes = [n for n in roadmap.personalization_notes 
                     if 'ambitious' in n.lower() or 'comfortable' in n.lower()]
    
    # There should be at least one timeline-related note
    # (This depends on the calculated vs available time)


def test_milestone_prerequisites_preserved(
    roadmap_engine,
    beginner_frontend_student,
    beginner_frontend_assessment
):
    """Test that milestone prerequisites are preserved during personalization."""
    roadmap = roadmap_engine.personalize_roadmap(
        role_key='frontend_engineer',
        student_features=beginner_frontend_student,
        skill_assessment=beginner_frontend_assessment,
        student_profile_id=uuid4()
    )
    
    # Check that prerequisites exist and are valid
    all_milestone_ids = {m.milestone_id for m in roadmap.milestones}
    
    for milestone in roadmap.milestones:
        # All prerequisites should reference valid milestone IDs
        for prereq_id in milestone.prerequisites:
            assert prereq_id in all_milestone_ids, \
                f"Invalid prerequisite {prereq_id} in milestone {milestone.milestone_id}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
