"""
AI Gateway

Lightweight wrapper for AI/LLM operations with fallbacks.
"""
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class AIOperation(str, Enum):
    """Types of AI operations."""
    RESUME_ENHANCEMENT = "resume_enhancement"
    SKILL_RECOMMENDATION = "skill_recommendation"
    ROADMAP_PERSONALIZATION = "roadmap_personalization"
    INTERVIEW_QUESTIONS = "interview_questions"
    CAREER_ADVICE = "career_advice"


@dataclass
class AIResponse:
    """
    Response from AI operation.
    
    Tracks whether AI was used or fallback, and includes metadata.
    """
    operation: AIOperation
    content: str
    used_ai: bool = False
    fallback_used: bool = False
    model_used: Optional[str] = None
    tokens_used: int = 0
    processing_time_ms: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation': self.operation,
            'content': self.content,
            'used_ai': self.used_ai,
            'fallback_used': self.fallback_used,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'processing_time_ms': self.processing_time_ms,
            'error': self.error,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class AIGateway:
    """
    Lightweight AI Gateway.
    
    Wraps LLM services with:
    - Typed operations
    - Automatic fallbacks
    - Usage tracking
    - Error handling
    
    Always provides a response - either AI-generated or rule-based fallback.
    """
    
    def __init__(
        self,
        llm_provider: Optional[Any] = None,
        enable_ai: bool = True,
        fallback_enabled: bool = True
    ):
        """
        Initialize AI Gateway.
        
        Args:
            llm_provider: Optional LLM provider instance
            enable_ai: Whether to attempt AI operations
            fallback_enabled: Whether to use fallbacks on AI failure
        """
        self.llm_provider = llm_provider
        self.enable_ai = enable_ai
        self.fallback_enabled = fallback_enabled
        
        # Usage tracking
        self.usage_stats = {
            'total_requests': 0,
            'ai_requests': 0,
            'fallback_requests': 0,
            'errors': 0
        }
    
    async def execute(
        self,
        operation: AIOperation,
        prompt: str,
        fallback_fn: Optional[Callable] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """
        Execute an AI operation with automatic fallback.
        
        Args:
            operation: Type of AI operation
            prompt: Prompt for LLM
            fallback_fn: Function to call if AI fails
            max_tokens: Max tokens for response
            temperature: LLM temperature
            **kwargs: Additional parameters for fallback
            
        Returns:
            AIResponse with content (from AI or fallback)
        """
        self.usage_stats['total_requests'] += 1
        start_time = datetime.utcnow()
        
        # Try AI if enabled
        if self.enable_ai and self.llm_provider:
            try:
                ai_response = await self._call_llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                self.usage_stats['ai_requests'] += 1
                
                return AIResponse(
                    operation=operation,
                    content=ai_response['content'],
                    used_ai=True,
                    fallback_used=False,
                    model_used=ai_response.get('model'),
                    tokens_used=ai_response.get('tokens', 0),
                    processing_time_ms=int(processing_time)
                )
                
            except Exception as e:
                logger.warning(f"AI operation {operation} failed: {e}")
                self.usage_stats['errors'] += 1
                
                # Fall through to fallback
        
        # Use fallback
        if self.fallback_enabled and fallback_fn:
            try:
                fallback_content = fallback_fn(**kwargs)
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                self.usage_stats['fallback_requests'] += 1
                
                return AIResponse(
                    operation=operation,
                    content=fallback_content,
                    used_ai=False,
                    fallback_used=True,
                    processing_time_ms=int(processing_time)
                )
                
            except Exception as e:
                logger.error(f"Fallback for {operation} failed: {e}")
                self.usage_stats['errors'] += 1
                
                return AIResponse(
                    operation=operation,
                    content="",
                    used_ai=False,
                    fallback_used=True,
                    error=str(e)
                )
        
        # No AI and no fallback
        return AIResponse(
            operation=operation,
            content="",
            used_ai=False,
            fallback_used=False,
            error="AI disabled and no fallback provided"
        )
    
    async def _call_llm(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Call LLM provider.
        
        Args:
            prompt: Prompt text
            max_tokens: Max response tokens
            temperature: Temperature for generation
            
        Returns:
            Dict with 'content', 'model', 'tokens'
        """
        if not self.llm_provider:
            raise RuntimeError("LLM provider not configured")
        
        # Call LLM provider
        # This assumes the provider has a generate() method
        # Adapt based on actual provider interface
        if hasattr(self.llm_provider, 'generate'):
            response = await self.llm_provider.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                'content': response.get('text', ''),
                'model': response.get('model', 'unknown'),
                'tokens': response.get('usage', {}).get('total_tokens', 0)
            }
        
        # Fallback for different provider interface
        elif hasattr(self.llm_provider, 'chat'):
            response = await self.llm_provider.chat(
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                'content': response.get('choices', [{}])[0].get('message', {}).get('content', ''),
                'model': response.get('model', 'unknown'),
                'tokens': response.get('usage', {}).get('total_tokens', 0)
            }
        
        raise RuntimeError("Unsupported LLM provider interface")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        total = self.usage_stats['total_requests']
        
        return {
            **self.usage_stats,
            'ai_rate': self.usage_stats['ai_requests'] / total if total > 0 else 0,
            'fallback_rate': self.usage_stats['fallback_requests'] / total if total > 0 else 0,
            'error_rate': self.usage_stats['errors'] / total if total > 0 else 0
        }
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            'total_requests': 0,
            'ai_requests': 0,
            'fallback_requests': 0,
            'errors': 0
        }
