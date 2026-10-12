"""Gemini LLM provider implementation."""

import os
import asyncio
from typing import List, Optional
import google.generativeai as genai
from app.services.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.core.config import settings


class GeminiProvider(BaseLLMProvider):
    """Gemini LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Gemini provider."""
        self.api_key = api_key or settings.LLM_API_KEY
        self.model_name = model or settings.LLM_MODEL or "gemini-flash-latest"
        
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _convert_messages(self, messages: List[LLMMessage]) -> tuple[str, List[dict]]:
        """Convert LLMMessage format to Gemini format."""
        system_prompt = ""
        history = []
        
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            elif msg.role == "user":
                history.append({
                    "role": "user",
                    "parts": [msg.content]
                })
            elif msg.role == "assistant":
                history.append({
                    "role": "model",
                    "parts": [msg.content]
                })
        
        return system_prompt, history

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from messages."""
        system_prompt, history = self._convert_messages(messages)
        
        # Configure generation
        generation_config = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # Create chat with history
        if system_prompt:
            # Include system prompt in first message
            full_history = []
            if history:
                if history[0]["role"] == "user":
                    full_history = [{
                        "role": "user",
                        "parts": [f"{system_prompt}\n\n{history[0]['parts'][0]}"]
                    }] + history[1:]
                else:
                    full_history = history
        else:
            full_history = history
        
        # Generate response
        def _send():
            chat = self.model.start_chat(history=full_history[:-1] if len(full_history) > 1 else [])
            return chat.send_message(
                full_history[-1]["parts"][0] if full_history else "",
                generation_config=generation_config
            )

        try:
            timeout_sec = float(getattr(settings, "LLM_TIMEOUT_SECONDS", 15))
            response = await asyncio.wait_for(asyncio.to_thread(_send), timeout=timeout_sec)
            
            return LLMResponse(
                content=response.text,
                model=self.model_name,
                usage={
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                },
                finish_reason=response.candidates[0].finish_reason.name if response.candidates else None
            )
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

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
