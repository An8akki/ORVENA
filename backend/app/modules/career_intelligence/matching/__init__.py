"""
Candidate-Role Matching Module

Integrates resume intelligence, skill assessment, and role classification
to match candidates to job roles with transparent, evidence-based scoring.
"""

from .candidate_matcher import CandidateMatcher, CandidateMatch, MatchReport

__all__ = [
    "CandidateMatcher",
    "CandidateMatch",
    "MatchReport",
]
