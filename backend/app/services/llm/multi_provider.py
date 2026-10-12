"""Multi-provider LLM manager with automatic fallback."""

from typing import List, Optional
import logging
from app.services.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.nvidia_provider import NVIDIAProvider
from app.services.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class MultiProviderLLM:
    """
    Multi-provider LLM manager with automatic fallback.
    
    Tries providers in order until one succeeds:
    1. Gemini Key 1 (primary)
    2. Gemini Key 2 (fallback)
    3. NVIDIA NIM (fallback)
    4. OpenAI (fallback)
    """
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        gemini_api_key_2: Optional[str] = None,
        gemini_model: str = "gemini-3.6-flash",
        nvidia_api_key: Optional[str] = None,
        nvidia_model: str = "nvidia/nemotron-3.5-lightning-30b-a3b",
        openai_api_key: Optional[str] = None,
        openai_model: str = "gpt-4o-mini"
    ):
        """Initialize multi-provider manager with fallback chain."""
        self.providers: List[tuple[str, BaseLLMProvider]] = []
        
        # Add Gemini Key 1 as primary provider
        if gemini_api_key:
            try:
                gemini = GeminiProvider(api_key=gemini_api_key, model=gemini_model)
                self.providers.append(("Gemini (Key 1)", gemini))
                logger.info(f"✓ Initialized Gemini Key 1 with model: {gemini_model}")
            except Exception as e:
                logger.warning(f"✗ Failed to initialize Gemini Key 1: {e}")
        
        # Add Gemini Key 2 as first fallback
        if gemini_api_key_2:
            try:
                gemini2 = GeminiProvider(api_key=gemini_api_key_2, model=gemini_model)
                self.providers.append(("Gemini (Key 2)", gemini2))
                logger.info(f"✓ Initialized Gemini Key 2 with model: {gemini_model}")
            except Exception as e:
                logger.warning(f"✗ Failed to initialize Gemini Key 2: {e}")
        
        # Add NVIDIA NIM as second fallback
        if nvidia_api_key:
            try:
                nvidia = NVIDIAProvider(api_key=nvidia_api_key, model=nvidia_model)
                self.providers.append(("NVIDIA NIM", nvidia))
                logger.info(f"✓ Initialized NVIDIA NIM with model: {nvidia_model}")
            except Exception as e:
                logger.warning(f"✗ Failed to initialize NVIDIA NIM: {e}")
        
        # Add OpenAI as final fallback
        if openai_api_key:
            try:
                openai = OpenAIProvider(api_key=openai_api_key, model=openai_model)
                self.providers.append(("OpenAI", openai))
                logger.info(f"✓ Initialized OpenAI with model: {openai_model}")
            except Exception as e:
                logger.warning(f"✗ Failed to initialize OpenAI: {e}")
        
        if not self.providers:
            raise ValueError("At least one LLM provider must be configured")
        
        provider_chain = " → ".join([name for name, _ in self.providers])
        logger.info(f"🔗 Multi-provider LLM initialized with {len(self.providers)} provider(s): {provider_chain}")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from messages with automatic fallback.
        
        Tries each provider in order until one succeeds.
        """
        last_error = None
        
        for provider_name, provider in self.providers:
            try:
                logger.debug(f"Attempting generation with {provider_name}...")
                response = await provider.generate(messages, temperature, max_tokens, **kwargs)
                logger.info(f"✓ Successfully generated response using {provider_name}")
                return response
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"✗ {provider_name} failed: {error_msg}")
                last_error = e
                
                # Check if it's a quota/rate limit error
                if "quota" in error_msg.lower() or "429" in error_msg or "rate limit" in error_msg.lower():
                    logger.info(f"→ {provider_name} quota exceeded, trying next provider...")
                    continue
                else:
                    logger.error(f"→ {provider_name} error (non-quota): {error_msg}")
                    continue
        
        # All providers failed
        provider_names = [name for name, _ in self.providers]
        raise Exception(
            f"All LLM providers failed. Tried: {', '.join(provider_names)}. "
            f"Last error: {str(last_error)}"
        )
    
    async def generate_with_system(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response with system prompt and user message."""
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_message)
        ]
        return await self.generate(messages, temperature, max_tokens, **kwargs)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [name for name, _ in self.providers]
