"""LLM service module."""

from app.services.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.nvidia_provider import NVIDIAProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.multi_provider import MultiProviderLLM
from app.core.config import settings


def get_llm_provider() -> BaseLLMProvider:
    """
    Get configured LLM provider with automatic fallback chain.
    
    Returns a multi-provider manager that tries in order:
    1. Gemini Key 1 (primary)
    2. Gemini Key 2 (fallback)
    3. NVIDIA NIM (fallback)
    4. OpenAI (fallback)
    
    Falls back automatically on quota/rate limit errors.
    """
    # Get API keys from settings
    gemini_key = getattr(settings, 'LLM_API_KEY', None)
    gemini_key_2 = getattr(settings, 'GEMINI_API_KEY_2', None)
    nvidia_key = getattr(settings, 'NVIDIA_API_KEY', None)
    openai_key = getattr(settings, 'OPENAI_API_KEY', None)
    
    # Get models from settings
    gemini_model = getattr(settings, 'LLM_MODEL', 'gemini-3.6-flash')
    nvidia_model = getattr(settings, 'NVIDIA_MODEL', 'nvidia/nemotron-3.5-lightning-30b-a3b')
    openai_model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
    
    # Return multi-provider with full fallback chain
    return MultiProviderLLM(
        gemini_api_key=gemini_key,
        gemini_api_key_2=gemini_key_2,
        gemini_model=gemini_model,
        nvidia_api_key=nvidia_key,
        nvidia_model=nvidia_model,
        openai_api_key=openai_key,
        openai_model=openai_model
    )


__all__ = [
    "BaseLLMProvider",
    "LLMMessage",
    "LLMResponse",
    "GeminiProvider",
    "NVIDIAProvider",
    "OpenAIProvider",
    "MultiProviderLLM",
    "get_llm_provider",
]

