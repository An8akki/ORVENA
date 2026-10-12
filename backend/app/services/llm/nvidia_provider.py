"""NVIDIA NIM LLM provider implementation."""

import os
from typing import List, Optional
import httpx
from app.services.llm.base import BaseLLMProvider, LLMMessage, LLMResponse


class NVIDIAProvider(BaseLLMProvider):
    """NVIDIA NIM LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "nvidia/nemotron-3.5-lightning-30b-a3b"):
        """Initialize NVIDIA NIM provider."""
        self.api_key = api_key
        self.model_name = model
        self.base_url = "https://integrate.api.nvidia.com/v1"
        
        if not self.api_key:
            raise ValueError("NVIDIA API key is required")

    def _convert_messages(self, messages: List[LLMMessage]) -> List[dict]:
        """Convert LLMMessage format to NVIDIA format."""
        converted = []
        for msg in messages:
            converted.append({
                "role": msg.role,
                "content": msg.content
            })
        return converted

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from messages."""
        converted_messages = self._convert_messages(messages)
        
        payload = {
            "model": self.model_name,
            "messages": converted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 2048,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract response
                choice = data["choices"][0]
                content = choice["message"]["content"]
                
                # Extract usage if available
                usage = data.get("usage", {})
                
                return LLMResponse(
                    content=content,
                    model=self.model_name,
                    usage={
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    finish_reason=choice.get("finish_reason")
                )
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if e.response.text else "Unknown error"
            if e.response.status_code == 429:
                raise Exception(f"NVIDIA API quota exceeded: {error_text}")
            raise Exception(f"NVIDIA API error ({e.response.status_code}): {error_text}")
        except httpx.TimeoutException:
            raise Exception("NVIDIA API request timed out after 60 seconds")
        except Exception as e:
            error_msg = str(e) if str(e) else "Unknown error occurred"
            raise Exception(f"NVIDIA API error: {error_msg}")

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
