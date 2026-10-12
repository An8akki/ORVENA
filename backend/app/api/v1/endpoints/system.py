"""API endpoints for system monitoring and health checks."""

from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional

from app.services.ai_fallback_monitor import ai_fallback_monitor, AIFeature

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "development"
    }


@router.get("/ai-stats")
async def get_ai_stats() -> Dict[str, Any]:
    """Get overall AI system statistics."""
    return {
        "overall": ai_fallback_monitor.get_overall_stats(),
        "by_feature": {
            feature.value: ai_fallback_monitor.get_feature_stats(feature)
            for feature in AIFeature
        }
    }


@router.get("/ai-stats/{feature}")
async def get_feature_stats(feature: str) -> Dict[str, Any]:
    """Get statistics for a specific AI feature."""
    try:
        ai_feature = AIFeature(feature)
        return ai_fallback_monitor.get_feature_stats(ai_feature)
    except ValueError:
        return {"error": f"Invalid feature: {feature}"}


@router.get("/fallback-analysis")
async def get_fallback_analysis() -> Dict[str, Any]:
    """Get analysis of fallback usage and recommendations."""
    return ai_fallback_monitor.get_fallback_analysis()


@router.get("/recent-events")
async def get_recent_events(
    limit: int = 50,
    feature: Optional[str] = None
) -> Dict[str, Any]:
    """Get recent AI events."""
    ai_feature = None
    if feature:
        try:
            ai_feature = AIFeature(feature)
        except ValueError:
            return {"error": f"Invalid feature: {feature}"}
    
    events = ai_fallback_monitor.get_recent_events(limit=limit, feature=ai_feature)
    return {
        "count": len(events),
        "events": events
    }
