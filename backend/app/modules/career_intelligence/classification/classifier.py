"""
Career Classifier

Main classification engine that coordinates evidence collection,
role matching, and result generation. Works with or without ML models.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from ..types import ClassificationResult, ConfidenceLevel
from ..evidence.evidence_collector import EvidenceCollector
from .role_matcher import RoleFitScorer
from app.db.models.intelligence import CareerClassification


class CareerClassifier:
    """
    Main career classification engine.
    
    Uses rule-based baseline by default. Can be extended with ML models.
    """
    
    def __init__(self):
        """Initialize classifier components."""
        self.evidence_collector = EvidenceCollector()
        self.role_scorer = RoleFitScorer()
        self.classifier_type = "rule_based"
        self.version = "1.0.0"
    
    async def classify(
        self,
        db: AsyncSession,
        student_profile_id: UUID,
        session_id: Optional[UUID] = None,
        min_score_threshold: float = 0.2
    ) -> ClassificationResult:
        """
        Classify a student into suitable career roles.
        
        Args:
            db: Database session
            student_profile_id: Student profile UUID
            session_id: Optional discovery session UUID
            min_score_threshold: Minimum score to include role in results
            
        Returns:
            ClassificationResult with ranked candidate roles
        """
        # Step 1: Collect evidence
        student_features = await self.evidence_collector.collect_student_features(
            db, student_profile_id, session_id
        )
        
        # Step 2: Score all roles
        all_scores = self.role_scorer.score_all_roles(student_features)
        
        # Step 3: Filter by threshold
        candidate_roles = [
            score for score in all_scores
            if score.fit_score >= min_score_threshold
        ]
        
        # Step 4: Limit to top candidates
        top_candidates = candidate_roles[:10]
        
        # Step 5: Determine overall confidence
        overall_confidence = self._determine_overall_confidence(
            top_candidates,
            student_features
        )
        
        # Step 6: Identify missing information
        missing_info = self._identify_missing_information(student_features)
        
        # Step 7: Generate follow-up questions
        followup_questions = self._generate_followup_questions(
            top_candidates,
            missing_info
        )
        
        # Step 8: Generate summary
        summary = self._generate_summary(
            top_candidates,
            student_features,
            overall_confidence
        )
        
        # Step 9: Create result
        result = ClassificationResult(
            student_profile_id=student_profile_id,
            candidate_roles=top_candidates,
            confidence=overall_confidence,
            model_version=self.version,
            classifier_type=self.classifier_type,
            missing_information=missing_info,
            suggested_followup_questions=followup_questions,
            summary=summary,
            classified_at=datetime.utcnow()
        )
        
        return result
    
    async def save_classification(
        self,
        db: AsyncSession,
        result: ClassificationResult,
        session_id: Optional[UUID] = None
    ) -> CareerClassification:
        """
        Save classification result to database.
        
        Args:
            db: Database session
            result: Classification result
            session_id: Optional discovery session ID
            
        Returns:
            Saved CareerClassification record
        """
        # Convert candidate roles to JSON-serializable format
        candidate_roles_data = [
            {
                "role_id": str(role.role_id),
                "role_name": role.role_name,
                "role_category": role.role_category,
                "fit_score": float(role.fit_score),
                "confidence": role.confidence.value,
                "matching_skills": role.matching_skills,
                "missing_skills": role.missing_skills,
                "partially_matched_skills": role.partially_matched_skills,
                "strengths": role.strengths,
                "gaps": role.gaps,
                "reasoning": role.reasoning,
                "next_steps": role.next_steps
            }
            for role in result.candidate_roles
        ]
        
        # Create database record
        classification = CareerClassification(
            student_profile_id=result.student_profile_id,
            session_id=session_id,
            classifier_type=result.classifier_type,
            model_version=result.model_version,
            confidence_level=result.confidence.value,
            candidate_roles={"roles": candidate_roles_data},
            missing_information=result.missing_information,
            summary=result.summary,
            input_features={
                "interests": [],  # Would include from student_features
                "skills_count": len(result.candidate_roles[0].matching_skills) if result.candidate_roles else 0
            }
        )
        
        db.add(classification)
        await db.flush()
        
        # Update result with classification ID
        result.classification_id = classification.id
        
        return classification
    
    def _determine_overall_confidence(
        self,
        candidate_roles: List,
        student_features
    ) -> ConfidenceLevel:
        """Determine overall classification confidence."""
        if not candidate_roles:
            return ConfidenceLevel.UNCERTAIN
        
        top_score = candidate_roles[0].fit_score
        top_confidence = candidate_roles[0].confidence
        
        # High confidence: Clear top role with high score
        if top_score > 0.7 and top_confidence == ConfidenceLevel.HIGH:
            return ConfidenceLevel.HIGH
        
        # Medium confidence: Good score, multiple viable options
        if top_score > 0.5:
            # Check if multiple roles have similar scores
            similar_count = sum(
                1 for role in candidate_roles
                if abs(role.fit_score - top_score) < 0.1
            )
            if similar_count > 1:
                return ConfidenceLevel.MEDIUM
            return ConfidenceLevel.HIGH
        
        # Low confidence: Moderate scores
        if top_score > 0.3:
            return ConfidenceLevel.LOW
        
        # Uncertain: Low scores across the board
        return ConfidenceLevel.UNCERTAIN
    
    def _identify_missing_information(self, student_features) -> List[str]:
        """Identify what information is missing or incomplete."""
        missing = []
        
        if not student_features.interests:
            missing.append("Career interests and motivations")
        
        if not student_features.skills:
            missing.append("Demonstrated skills and experience")
        
        if not student_features.education_level:
            missing.append("Education background")
        
        if student_features.project_count == 0:
            missing.append("Portfolio projects or practical experience")
        
        if not student_features.work_preferences:
            missing.append("Work environment and style preferences")
        
        return missing
    
    def _generate_followup_questions(
        self,
        candidate_roles: List,
        missing_info: List[str]
    ) -> List[str]:
        """Generate targeted follow-up questions."""
        questions = []
        
        # Questions based on missing information
        if "Career interests" in " ".join(missing_info):
            questions.append(
                "What types of work activities do you find most engaging?"
            )
        
        if "skills" in " ".join(missing_info).lower():
            questions.append(
                "What programming languages or technologies have you worked with?"
            )
        
        if "projects" in " ".join(missing_info).lower():
            questions.append(
                "Have you built any personal or academic projects?"
            )
        
        # Questions to distinguish between top candidates
        if len(candidate_roles) >= 2:
            top_two = candidate_roles[:2]
            if abs(top_two[0].fit_score - top_two[1].fit_score) < 0.15:
                # Close scores, ask distinguishing question
                role1_name = top_two[0].role_name
                role2_name = top_two[1].role_name
                
                questions.append(
                    f"Are you more interested in {role1_name} or {role2_name} type of work?"
                )
        
        return questions[:3]  # Limit to 3 questions
    
    def _generate_summary(
        self,
        candidate_roles: List,
        student_features,
        confidence: ConfidenceLevel
    ) -> str:
        """Generate overall classification summary."""
        if not candidate_roles:
            return "Unable to identify suitable career roles with current information. Please provide more details about your interests, skills, and experience."
        
        top_role = candidate_roles[0]
        
        # Build summary parts
        parts = []
        
        # Confidence statement
        if confidence == ConfidenceLevel.HIGH:
            parts.append(
                f"Based on your profile, {top_role.role_name} is a strong match."
            )
        elif confidence == ConfidenceLevel.MEDIUM:
            parts.append(
                f"{top_role.role_name} appears to be a good fit, along with {len(candidate_roles) - 1} other potential roles."
            )
        elif confidence == ConfidenceLevel.LOW:
            parts.append(
                f"You may be suited for {top_role.role_name}, but more information would help confirm this."
            )
        else:
            parts.append(
                "Multiple career paths are possible. Additional information about your interests and skills would help identify the best fit."
            )
        
        # Skill summary
        if top_role.matching_skills:
            parts.append(
                f"You have demonstrated skills in {', '.join(top_role.matching_skills[:3])}."
            )
        
        # Gap summary
        if top_role.missing_skills:
            parts.append(
                f"To strengthen your candidacy, focus on developing {', '.join(top_role.missing_skills[:2])}."
            )
        
        # Alternative roles
        if len(candidate_roles) > 1:
            other_roles = [r.role_name for r in candidate_roles[1:3]]
            parts.append(
                f"Other suitable roles to consider: {', '.join(other_roles)}."
            )
        
        return " ".join(parts)
    
    async def get_classification_by_id(
        self,
        db: AsyncSession,
        classification_id: UUID
    ) -> Optional[CareerClassification]:
        """Retrieve a saved classification."""
        result = await db.get(CareerClassification, classification_id)
        return result
    
    async def get_latest_classification(
        self,
        db: AsyncSession,
        student_profile_id: UUID
    ) -> Optional[CareerClassification]:
        """Get the most recent classification for a student."""
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(CareerClassification)
            .where(CareerClassification.student_profile_id == student_profile_id)
            .order_by(desc(CareerClassification.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
