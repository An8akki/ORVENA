"""
Career Intelligence Module

ML-based career classification, evidence-based role matching,
starting-level assessment, and personalized roadmap generation.
"""

from .classification.classifier import CareerClassifier
from .classification.role_matcher import RoleFitScorer
from .evidence.evidence_collector import EvidenceCollector

__all__ = [
    "CareerClassifier",
    "RoleFitScorer",
    "EvidenceCollector",
]
