"""OpenAI LLM provider implementation."""

from typing import List, Optional
import httpx
from app.services.llm.base import BaseLLMProvider, LLMMessage, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI provider."""
        self.api_key = api_key
        self.model_name = model
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    def _convert_messages(self, messages: List[LLMMessage]) -> List[dict]:
        """Convert LLMMessage format to OpenAI format."""
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
                
                # Extract usage
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
            if e.response.status_code == 429:
                raise Exception(f"OpenAI API quota exceeded: {e.response.text}")
            elif e.response.status_code == 401:
                raise Exception(f"OpenAI API authentication failed: Invalid API key")
            raise Exception(f"OpenAI API error ({e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

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
