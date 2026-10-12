"""Service for AI-powered resume analysis and review."""

from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.resume import Resume, ResumeReview, ResumeReviewFinding
from app.services.llm import get_llm_provider
from app.core.exceptions import NotFoundError


class ResumeAnalysisService:
    """Service for analyzing resumes with AI."""

    ANALYSIS_PROMPT = """You are an expert resume reviewer. Analyze this resume and provide detailed feedback.

Evaluate the resume on these dimensions:
1. Content Quality (clarity, relevance, impact)
2. Structure & Format (organization, readability)
3. Keywords & ATS Optimization
4. Achievement Quantification
5. Grammar & Writing Quality

Return a JSON object with:
{
  "overall_score": 0.75,
  "overall_feedback": "Brief 2-3 sentence summary",
  "findings": [
    {
      "category": "content|format|keywords|achievements|grammar",
      "severity": "critical|major|minor|suggestion",
      "section": "summary|experience|education|skills",
      "current_text": "problematic text if applicable",
      "suggested_improvement": "specific actionable improvement",
      "reasoning": "why this matters"
    }
  ]
}

Provide 5-10 specific, actionable findings."""

    async def analyze_resume(
        self,
        db: AsyncSession,
        resume_id: UUID,
        resume_text: str,
        review_type: str = "general"
    ) -> ResumeReview:
        """Analyze resume and generate review."""
        llm = get_llm_provider()

        # Generate analysis
        response = await llm.generate_with_system(
            system_prompt=self.ANALYSIS_PROMPT,
            user_message=f"Resume to analyze:\n\n{resume_text[:3000]}",
            temperature=0.5,
            max_tokens=1500,
        )

        # Parse response
        import json, re
        analysis_data = {}
        try:
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
        except:
            analysis_data = {
                "overall_score": 0.7,
                "overall_feedback": "Resume analysis completed",
                "findings": []
            }

        # Create review
        review = ResumeReview(
            resume_id=resume_id,
            review_type=review_type,
            overall_score=analysis_data.get("overall_score", 0.7),
            overall_feedback=analysis_data.get("overall_feedback", "Analysis completed"),
        )
        db.add(review)
        await db.flush()

        # Create findings
        for finding_data in analysis_data.get("findings", [])[:10]:
            finding = ResumeReviewFinding(
                review_id=review.id,
                category=finding_data.get("category", "content"),
                severity=finding_data.get("severity", "minor"),
                section=finding_data.get("section"),
                current_text=finding_data.get("current_text"),
                suggested_improvement=finding_data.get("suggested_improvement", ""),
                reasoning=finding_data.get("reasoning"),
            )
            db.add(finding)

        await db.commit()
        await db.refresh(review)
        return review

    async def get_resume_reviews(
        self, db: AsyncSession, resume_id: UUID
    ) -> List[ResumeReview]:
        """Get all reviews for a resume."""
        result = await db.execute(
            select(ResumeReview)
            .where(ResumeReview.resume_id == resume_id)
            .order_by(ResumeReview.created_at.desc())
        )
        return list(result.scalars().all())


resume_analysis_service = ResumeAnalysisService()
