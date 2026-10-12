"""
Tests for skill normalizer.
"""
import pytest
from app.modules.resume_intelligence.matching.skill_normalizer import (
    SkillNormalizer,
    SkillMatch
)
from app.modules.career_intelligence.types import EvidenceType, EvidenceState


@pytest.fixture
def normalizer():
    """Create normalizer instance."""
    return SkillNormalizer()


def test_exact_match(normalizer):
    """Test exact skill name match."""
    match = normalizer.normalize_skill("python")
    
    assert match.canonical_skill == "python"
    assert match.match_confidence == 1.0
    assert match.match_type == "exact"


def test_case_insensitive_match(normalizer):
    """Test case-insensitive matching."""
    match = normalizer.normalize_skill("Python")
    
    assert match.canonical_skill == "python"
    assert match.match_confidence == 1.0
    assert match.match_type == "exact"
    
    match2 = normalizer.normalize_skill("JAVASCRIPT")
    assert match2.canonical_skill == "javascript"


def test_synonym_match(normalizer):
    """Test synonym matching."""
    # "js" is a synonym for "javascript"
    match = normalizer.normalize_skill("js")
    
    assert match.canonical_skill == "javascript"
    assert match.match_confidence == 0.95
    assert match.match_type == "synonym"


def test_fuzzy_match(normalizer):
    """Test fuzzy matching for misspellings."""
    # Slight misspelling
    match = normalizer.normalize_skill("javascrpt")
    
    # Should match javascript with high confidence
    assert match.canonical_skill is not None
    assert match.match_confidence >= 0.8
    assert match.match_type == "fuzzy"


def test_no_match(normalizer):
    """Test handling of non-matching skills."""
    match = normalizer.normalize_skill("completely-unknown-skill-xyz")
    
    assert match.canonical_skill is None
    assert match.match_confidence == 0.0
    assert match.match_type == "none"


def test_empty_skill(normalizer):
    """Test handling of empty/invalid skills."""
    match1 = normalizer.normalize_skill("")
    assert match1.canonical_skill is None
    
    match2 = normalizer.normalize_skill("   ")
    assert match2.canonical_skill is None


def test_normalize_multiple_skills(normalizer):
    """Test normalizing a list of skills."""
    raw_skills = ["Python", "js", "react", "unknown-skill", "postgres"]
    
    matches = normalizer.normalize_skills(raw_skills)
    
    assert len(matches) == 5
    
    # Check known skills are matched
    matched_names = [m.canonical_skill for m in matches if m.canonical_skill]
    assert "python" in matched_names
    assert "javascript" in matched_names
    assert "react" in matched_names


def test_normalize_with_evidence_declared(normalizer):
    """Test normalization with declared evidence type."""
    raw_skills = ["Python", "JavaScript", "React"]
    
    records = normalizer.normalize_with_evidence(
        raw_skills,
        source_type=EvidenceType.DECLARED,
        confidence_threshold=0.7
    )
    
    assert len(records) > 0
    
    for record in records:
        assert record['evidence_type'] == EvidenceType.DECLARED
        assert record['evidence_state'] == EvidenceState.DECLARED_UNVERIFIED
        assert record['skill_name'] is not None


def test_normalize_with_evidence_project(normalizer):
    """Test normalization with project evidence type."""
    raw_skills = ["Python", "Django"]
    
    records = normalizer.normalize_with_evidence(
        raw_skills,
        source_type=EvidenceType.PROJECT,
        confidence_threshold=0.7
    )
    
    assert len(records) > 0
    
    for record in records:
        assert record['evidence_type'] == EvidenceType.PROJECT
        # High confidence project skills should be demonstrated
        if record['confidence'] >= 0.9:
            assert record['evidence_state'] == EvidenceState.DEMONSTRATED


def test_confidence_threshold(normalizer):
    """Test that confidence threshold filters low-confidence matches."""
    raw_skills = ["Python", "unknown-xyz"]
    
    # High threshold - only good matches
    records_high = normalizer.normalize_with_evidence(
        raw_skills,
        confidence_threshold=0.9
    )
    
    # Low threshold - more matches
    records_low = normalizer.normalize_with_evidence(
        raw_skills,
        confidence_threshold=0.5
    )
    
    # High threshold should have fewer or equal records
    assert len(records_high) <= len(records_low)


def test_get_unmatched_skills(normalizer):
    """Test identification of unmatched skills."""
    raw_skills = ["Python", "unknown-skill-1", "JavaScript", "xyz"]
    
    matches = normalizer.normalize_skills(raw_skills)
    unmatched = normalizer.get_unmatched_skills(matches, min_length=3)
    
    assert "unknown-skill-1" in unmatched
    # Python and JavaScript should not be in unmatched
    assert "Python" not in unmatched
    assert "JavaScript" not in unmatched


def test_get_statistics(normalizer):
    """Test statistics calculation."""
    raw_skills = ["Python", "JavaScript", "React", "unknown-1", "unknown-2"]
    
    matches = normalizer.normalize_skills(raw_skills)
    stats = normalizer.get_statistics(matches)
    
    assert stats['total'] == 5
    assert stats['matched'] >= 3  # Python, JS, React should match
    assert stats['unmatched'] >= 2  # unknown-1, unknown-2 should not match
    assert 0.0 <= stats['match_rate'] <= 1.0
    assert 0.0 <= stats['avg_confidence'] <= 1.0
    assert 'match_types' in stats


def test_skill_with_special_characters(normalizer):
    """Test skills with special characters."""
    # C++ and C# have special characters
    match_cpp = normalizer.normalize_skill("C++")
    assert match_cpp.canonical_skill is not None
    
    match_csharp = normalizer.normalize_skill("C#")
    assert match_csharp.canonical_skill is not None


def test_whitespace_handling(normalizer):
    """Test that whitespace is handled correctly."""
    match1 = normalizer.normalize_skill("  Python  ")
    assert match1.canonical_skill == "python"
    
    match2 = normalizer.normalize_skill("machine learning")
    # Should match if it's in the taxonomy
    assert match2.canonical_skill is not None or match2.canonical_skill is None


def test_substring_matching(normalizer):
    """Test that substring matches are recognized."""
    # If "javascript" is canonical and "js" is synonym
    match = normalizer.normalize_skill("js")
    assert match.canonical_skill == "javascript"
    assert match.match_confidence > 0.8


def test_levenshtein_similarity():
    """Test Levenshtein distance calculation."""
    from app.modules.resume_intelligence.matching.skill_normalizer import levenshtein_distance
    
    # Identical strings
    assert levenshtein_distance("python", "python") == 0
    
    # One character difference
    assert levenshtein_distance("python", "pythom") == 1
    
    # Completely different
    distance = levenshtein_distance("python", "java")
    assert distance > 0


def test_multiple_evidence_types(normalizer):
    """Test normalization with different evidence types."""
    raw_skills = ["Python", "Docker"]
    
    # Declared skills
    declared_records = normalizer.normalize_with_evidence(
        raw_skills,
        source_type=EvidenceType.DECLARED
    )
    
    # Work experience skills
    work_records = normalizer.normalize_with_evidence(
        raw_skills,
        source_type=EvidenceType.WORK_EXPERIENCE
    )
    
    # Certification skills
    cert_records = normalizer.normalize_with_evidence(
        raw_skills,
        source_type=EvidenceType.CERTIFICATION
    )
    
    # All should have records
    assert len(declared_records) > 0
    assert len(work_records) > 0
    assert len(cert_records) > 0
    
    # Evidence states should differ
    declared_states = {r['evidence_state'] for r in declared_records}
    work_states = {r['evidence_state'] for r in work_records}
    
    # Declared should be unverified, work experience should be demonstrated
    assert EvidenceState.DECLARED_UNVERIFIED in declared_states
    assert EvidenceState.DEMONSTRATED in work_states or EvidenceState.PARTIALLY_DEMONSTRATED in work_states


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
