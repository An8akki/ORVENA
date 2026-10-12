"""
Skill Normalizer

Maps extracted resume skills to canonical skill taxonomy.
Handles synonyms, variations, and fuzzy matching.
"""
import logging
from typing import List, Dict, Optional, Tuple

from ...career_intelligence.taxonomy.skills import (
    CANONICAL_SKILLS,
    normalize_skill_name
)
from ...career_intelligence.types import EvidenceType, EvidenceState, ProficiencyLevel

logger = logging.getLogger(__name__)


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.
    
    Simple implementation without external dependencies.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


class SkillMatch:
    """Result of skill normalization."""
    
    def __init__(
        self,
        raw_skill: str,
        canonical_skill: Optional[str],
        match_confidence: float,
        match_type: str  # 'exact', 'synonym', 'fuzzy', 'none'
    ):
        self.raw_skill = raw_skill
        self.canonical_skill = canonical_skill
        self.match_confidence = match_confidence
        self.match_type = match_type
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'raw_skill': self.raw_skill,
            'canonical_skill': self.canonical_skill,
            'match_confidence': self.match_confidence,
            'match_type': self.match_type
        }


class SkillNormalizer:
    """
    Normalizes extracted skills to canonical taxonomy.
    
    Process:
    1. Try exact match with canonical skill names
    2. Try synonym matching
    3. Try fuzzy matching with threshold
    4. Return unmatched with low confidence
    """
    
    FUZZY_THRESHOLD = 0.8  # Minimum similarity for fuzzy match
    
    def __init__(self):
        # Build lookup maps for faster matching
        self._canonical_map = {}
        self._synonym_map = {}
        
        # CANONICAL_SKILLS is a dict with skill_name as key
        for skill_name, skill_data in CANONICAL_SKILLS.items():
            # Add canonical name (use skill_name as both key and value for consistency)
            self._canonical_map[skill_name.lower()] = skill_name
            
            # Add common synonyms (hardcoded for now - will be in taxonomy later)
            # These are common variations we want to handle
            synonyms = self._get_skill_synonyms(skill_name)
            for synonym in synonyms:
                self._synonym_map[synonym.lower()] = skill_name
    
    def normalize_skill(self, raw_skill: str) -> SkillMatch:
        """
        Normalize a single skill to canonical taxonomy.
        
        Args:
            raw_skill: Raw skill string from resume
            
        Returns:
            SkillMatch with canonical mapping
        """
        if not raw_skill or not raw_skill.strip():
            return SkillMatch(raw_skill, None, 0.0, 'none')
        
        raw_skill_clean = raw_skill.strip()
        raw_skill_lower = raw_skill_clean.lower()
        
        # 1. Try exact match
        if raw_skill_lower in self._canonical_map:
            canonical_name = self._get_skill_name(self._canonical_map[raw_skill_lower])
            return SkillMatch(raw_skill_clean, canonical_name, 1.0, 'exact')
        
        # 2. Try synonym match
        if raw_skill_lower in self._synonym_map:
            canonical_name = self._get_skill_name(self._synonym_map[raw_skill_lower])
            return SkillMatch(raw_skill_clean, canonical_name, 0.95, 'synonym')
        
        # 3. Try fuzzy match
        best_match = self._fuzzy_match(raw_skill_lower)
        if best_match:
            canonical_name, confidence = best_match
            return SkillMatch(raw_skill_clean, canonical_name, confidence, 'fuzzy')
        
        # 4. No match found
        return SkillMatch(raw_skill_clean, None, 0.0, 'none')
    
    def normalize_skills(self, raw_skills: List[str]) -> List[SkillMatch]:
        """
        Normalize multiple skills.
        
        Args:
            raw_skills: List of raw skill strings
            
        Returns:
            List of SkillMatch objects
        """
        return [self.normalize_skill(skill) for skill in raw_skills]
    
    def normalize_with_evidence(
        self,
        raw_skills: List[str],
        source_type: EvidenceType = EvidenceType.DECLARED,
        confidence_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Normalize skills and prepare evidence records.
        
        Args:
            raw_skills: List of raw skill strings
            source_type: Type of evidence source
            confidence_threshold: Minimum confidence to include
            
        Returns:
            List of skill evidence dictionaries
        """
        evidence_records = []
        
        for skill_match in self.normalize_skills(raw_skills):
            # Skip if no match or below threshold
            if not skill_match.canonical_skill or skill_match.match_confidence < confidence_threshold:
                logger.debug(f"Skipping skill '{skill_match.raw_skill}' - low confidence or no match")
                continue
            
            # Determine evidence state based on source and confidence
            if source_type == EvidenceType.DECLARED:
                evidence_state = EvidenceState.DECLARED_UNVERIFIED
            elif source_type in [EvidenceType.PROJECT, EvidenceType.WORK_EXPERIENCE]:
                if skill_match.match_confidence >= 0.9:
                    evidence_state = EvidenceState.DEMONSTRATED
                else:
                    evidence_state = EvidenceState.PARTIALLY_DEMONSTRATED
            elif source_type in [EvidenceType.EDUCATION, EvidenceType.CERTIFICATION]:
                evidence_state = EvidenceState.PARTIALLY_DEMONSTRATED
            else:
                evidence_state = EvidenceState.NOT_ASSESSED
            
            evidence_records.append({
                'skill_name': skill_match.canonical_skill,
                'evidence_type': source_type,
                'evidence_state': evidence_state,
                'proficiency_level': None,  # To be determined by assessor
                'source_description': f"Resume: {skill_match.raw_skill}",
                'confidence': skill_match.match_confidence,
                'raw_skill': skill_match.raw_skill,
                'match_type': skill_match.match_type
            })
        
        return evidence_records
    
    def _fuzzy_match(self, raw_skill: str) -> Optional[Tuple[str, float]]:
        """
        Find best fuzzy match for a skill.
        
        Args:
            raw_skill: Normalized raw skill string
            
        Returns:
            Tuple of (canonical_name, confidence) or None
        """
        best_match = None
        best_score = 0.0
        
        # Check against canonical names
        for canonical_lower, skill_id in self._canonical_map.items():
            similarity = self._calculate_similarity(raw_skill, canonical_lower)
            
            if similarity > best_score and similarity >= self.FUZZY_THRESHOLD:
                best_score = similarity
                best_match = self._get_skill_name(skill_id)
        
        # Check against synonyms
        for synonym_lower, skill_id in self._synonym_map.items():
            similarity = self._calculate_similarity(raw_skill, synonym_lower)
            
            if similarity > best_score and similarity >= self.FUZZY_THRESHOLD:
                best_score = similarity
                best_match = self._get_skill_name(skill_id)
        
        if best_match:
            return (best_match, best_score)
        
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings.
        
        Uses Levenshtein distance normalized by length.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if str1 == str2:
            return 1.0
        
        # Handle substring matches (e.g., "js" vs "javascript")
        if str1 in str2 or str2 in str1:
            shorter = min(len(str1), len(str2))
            longer = max(len(str1), len(str2))
            # Partial credit for substring matches
            return 0.85 + (0.15 * (shorter / longer))
        
        # Levenshtein distance
        distance = levenshtein_distance(str1, str2)
        max_len = max(len(str1), len(str2))
        
        if max_len == 0:
            return 0.0
        
        similarity = 1.0 - (distance / max_len)
        return max(0.0, similarity)
    
    def _get_skill_synonyms(self, skill_name: str) -> List[str]:
        """Get common synonyms for a skill."""
        # Hardcoded common synonyms
        # TODO: Move these to taxonomy data structure
        synonym_map = {
            'javascript': ['js', 'es6', 'es2015', 'ecmascript'],
            'typescript': ['ts'],
            'python': ['py'],
            'postgresql': ['postgres', 'pg'],
            'mongodb': ['mongo'],
            'kubernetes': ['k8s'],
            'csharp': ['c#'],
            'cpp': ['c++'],
            'react': ['reactjs', 'react.js'],
            'vue': ['vuejs', 'vue.js'],
            'angular': ['angularjs'],
            'nodejs': ['node.js', 'node'],
            'expressjs': ['express.js'],
            'docker': ['containers'],
            'git': ['github', 'gitlab', 'version control'],
        }
        
        return synonym_map.get(skill_name, [])
    
    def _get_skill_name(self, skill_key: str) -> str:
        """Get canonical skill name by key."""
        # In our structure, the key IS the canonical name
        return skill_key
    
    def get_unmatched_skills(
        self,
        skill_matches: List[SkillMatch],
        min_length: int = 3
    ) -> List[str]:
        """
        Get list of skills that couldn't be matched.
        
        Useful for identifying gaps in the taxonomy.
        
        Args:
            skill_matches: List of SkillMatch objects
            min_length: Minimum skill name length to include
            
        Returns:
            List of unmatched skill names
        """
        unmatched = []
        
        for match in skill_matches:
            if not match.canonical_skill and len(match.raw_skill) >= min_length:
                unmatched.append(match.raw_skill)
        
        return unmatched
    
    def get_statistics(self, skill_matches: List[SkillMatch]) -> Dict:
        """
        Calculate normalization statistics.
        
        Args:
            skill_matches: List of SkillMatch objects
            
        Returns:
            Dictionary with statistics
        """
        total = len(skill_matches)
        if total == 0:
            return {
                'total': 0,
                'matched': 0,
                'unmatched': 0,
                'match_rate': 0.0,
                'avg_confidence': 0.0,
                'match_types': {}
            }
        
        matched = sum(1 for m in skill_matches if m.canonical_skill)
        unmatched = total - matched
        
        match_types = {}
        for match in skill_matches:
            match_types[match.match_type] = match_types.get(match.match_type, 0) + 1
        
        avg_confidence = sum(m.match_confidence for m in skill_matches) / total
        
        return {
            'total': total,
            'matched': matched,
            'unmatched': unmatched,
            'match_rate': matched / total,
            'avg_confidence': avg_confidence,
            'match_types': match_types
        }
