"""
AI Fallback System Monitor

Tracks AI usage, fallback events, and provides comprehensive reporting.
Ensures system reliability by monitoring all AI-dependent features.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import time


class AIFeature(str, Enum):
    """AI-powered features in the system."""
    RESUME_PARSING = "resume_parsing"
    RESUME_SCORING = "resume_scoring"
    CAREER_RECOMMENDATIONS = "career_recommendations"
    ROADMAP_GENERATION = "roadmap_generation"
    CAREER_DISCOVERY = "career_discovery"


class FallbackReason(str, Enum):
    """Reasons for fallback activation."""
    TIMEOUT = "timeout"
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"
    INVALID_RESPONSE = "invalid_response"
    SERVICE_UNAVAILABLE = "service_unavailable"


class AIFallbackMonitor:
    """Monitor and report on AI usage and fallback events."""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.max_events = 1000  # Keep last 1000 events
        self.feature_stats: Dict[str, Dict[str, int]] = {
            feature.value: {
                "total_requests": 0,
                "ai_success": 0,
                "fallback_used": 0,
                "total_errors": 0
            }
            for feature in AIFeature
        }
    
    def log_ai_attempt(
        self,
        feature: AIFeature,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an AI service attempt. Returns request_id for tracking."""
        request_id = f"{feature.value}_{int(time.time() * 1000)}"
        
        event = {
            "request_id": request_id,
            "feature": feature.value,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending",
            "context": context or {}
        }
        
        self._add_event(event)
        self.feature_stats[feature.value]["total_requests"] += 1
        
        return request_id
    
    def log_ai_success(
        self,
        request_id: str,
        response_time_ms: float,
        model_used: Optional[str] = None
    ):
        """Log successful AI response."""
        event = self._find_event(request_id)
        if event:
            event["status"] = "ai_success"
            event["response_time_ms"] = response_time_ms
            event["model_used"] = model_used
            event["completed_at"] = datetime.utcnow().isoformat()
            
            feature = event["feature"]
            self.feature_stats[feature]["ai_success"] += 1
    
    def log_fallback_used(
        self,
        request_id: str,
        reason: FallbackReason,
        fallback_method: str,
        response_time_ms: float,
        error_message: Optional[str] = None
    ):
        """Log fallback mechanism activation."""
        event = self._find_event(request_id)
        if event:
            event["status"] = "fallback_used"
            event["fallback_reason"] = reason.value
            event["fallback_method"] = fallback_method
            event["response_time_ms"] = response_time_ms
            event["error_message"] = error_message
            event["completed_at"] = datetime.utcnow().isoformat()
            
            feature = event["feature"]
            self.feature_stats[feature]["fallback_used"] += 1
    
    def log_total_failure(
        self,
        request_id: str,
        error_message: str
    ):
        """Log complete failure (both AI and fallback failed)."""
        event = self._find_event(request_id)
        if event:
            event["status"] = "failed"
            event["error_message"] = error_message
            event["completed_at"] = datetime.utcnow().isoformat()
            
            feature = event["feature"]
            self.feature_stats[feature]["total_errors"] += 1
    
    def get_feature_stats(self, feature: AIFeature) -> Dict[str, Any]:
        """Get statistics for a specific feature."""
        stats = self.feature_stats[feature.value].copy()
        
        # Calculate percentages
        total = stats["total_requests"]
        if total > 0:
            stats["ai_success_rate"] = round((stats["ai_success"] / total) * 100, 2)
            stats["fallback_rate"] = round((stats["fallback_used"] / total) * 100, 2)
            stats["error_rate"] = round((stats["total_errors"] / total) * 100, 2)
            stats["reliability"] = 100 - stats["error_rate"]
        else:
            stats["ai_success_rate"] = 0
            stats["fallback_rate"] = 0
            stats["error_rate"] = 0
            stats["reliability"] = 100
        
        return stats
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        total_requests = sum(s["total_requests"] for s in self.feature_stats.values())
        total_ai_success = sum(s["ai_success"] for s in self.feature_stats.values())
        total_fallback = sum(s["fallback_used"] for s in self.feature_stats.values())
        total_errors = sum(s["total_errors"] for s in self.feature_stats.values())
        
        return {
            "total_requests": total_requests,
            "ai_success": total_ai_success,
            "fallback_used": total_fallback,
            "total_errors": total_errors,
            "ai_success_rate": round((total_ai_success / total_requests) * 100, 2) if total_requests > 0 else 0,
            "fallback_rate": round((total_fallback / total_requests) * 100, 2) if total_requests > 0 else 0,
            "error_rate": round((total_errors / total_requests) * 100, 2) if total_requests > 0 else 0,
            "system_reliability": round((1 - (total_errors / total_requests)) * 100, 2) if total_requests > 0 else 100,
            "uptime_guarantee": "99.9%" if total_errors == 0 else f"{round((1 - (total_errors / total_requests)) * 100, 1)}%"
        }
    
    def get_recent_events(self, limit: int = 50, feature: Optional[AIFeature] = None) -> List[Dict[str, Any]]:
        """Get recent events, optionally filtered by feature."""
        events = self.events.copy()
        
        if feature:
            events = [e for e in events if e["feature"] == feature.value]
        
        # Sort by timestamp descending
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return events[:limit]
    
    def get_fallback_analysis(self) -> Dict[str, Any]:
        """Analyze fallback patterns and recommendations."""
        # Count fallback reasons
        reason_counts = {}
        for event in self.events:
            if event.get("status") == "fallback_used":
                reason = event.get("fallback_reason", "unknown")
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        # Generate recommendations
        recommendations = []
        
        timeout_count = reason_counts.get("timeout", 0)
        if timeout_count > 10:
            recommendations.append({
                "priority": "high",
                "issue": f"{timeout_count} timeout events detected",
                "action": "Consider increasing timeout thresholds or optimizing AI prompts"
            })
        
        rate_limit_count = reason_counts.get("rate_limit", 0)
        if rate_limit_count > 5:
            recommendations.append({
                "priority": "high",
                "issue": f"{rate_limit_count} rate limit events",
                "action": "Upgrade AI service plan or implement request queuing"
            })
        
        api_error_count = reason_counts.get("api_error", 0)
        if api_error_count > 10:
            recommendations.append({
                "priority": "medium",
                "issue": f"{api_error_count} API errors",
                "action": "Check AI service status and API credentials"
            })
        
        return {
            "fallback_reasons": reason_counts,
            "recommendations": recommendations,
            "fallback_health": "excellent" if sum(reason_counts.values()) < 5 else "good" if sum(reason_counts.values()) < 20 else "needs_attention"
        }
    
    def reset_stats(self):
        """Reset all statistics (use with caution)."""
        self.events.clear()
        for feature in AIFeature:
            self.feature_stats[feature.value] = {
                "total_requests": 0,
                "ai_success": 0,
                "fallback_used": 0,
                "total_errors": 0
            }
    
    def _add_event(self, event: Dict[str, Any]):
        """Add event to history, maintaining max size."""
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)  # Remove oldest
    
    def _find_event(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Find event by request ID."""
        for event in reversed(self.events):  # Search from most recent
            if event["request_id"] == request_id:
                return event
        return None


# Singleton instance
ai_fallback_monitor = AIFallbackMonitor()


# Decorator for automatic monitoring
def monitor_ai_fallback(feature: AIFeature):
    """Decorator to automatically monitor AI operations with fallback."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id if available in kwargs
            user_id = kwargs.get("user_id") or kwargs.get("profile_id")
            
            # Log attempt
            request_id = ai_fallback_monitor.log_ai_attempt(
                feature=feature,
                user_id=str(user_id) if user_id else None
            )
            
            start_time = time.time()
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Log success
                response_time = (time.time() - start_time) * 1000
                ai_fallback_monitor.log_ai_success(
                    request_id=request_id,
                    response_time_ms=response_time
                )
                
                return result
                
            except asyncio.TimeoutError:
                response_time = (time.time() - start_time) * 1000
                ai_fallback_monitor.log_fallback_used(
                    request_id=request_id,
                    reason=FallbackReason.TIMEOUT,
                    fallback_method="statistical_fallback",
                    response_time_ms=response_time,
                    error_message="AI request timed out"
                )
                raise
                
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                error_msg = str(e)
                
                if "rate limit" in error_msg.lower():
                    reason = FallbackReason.RATE_LIMIT
                elif "unavailable" in error_msg.lower():
                    reason = FallbackReason.SERVICE_UNAVAILABLE
                else:
                    reason = FallbackReason.API_ERROR
                
                ai_fallback_monitor.log_fallback_used(
                    request_id=request_id,
                    reason=reason,
                    fallback_method="statistical_fallback",
                    response_time_ms=response_time,
                    error_message=error_msg
                )
                raise
        
        return wrapper
    return decorator
