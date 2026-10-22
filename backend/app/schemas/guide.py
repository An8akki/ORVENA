"""
Pydantic Schemas for Orvena Guide Rule-Based Platform Assistant
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class GuideChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str


class GuideNavigationAction(BaseModel):
    label: str
    href: str
    description: Optional[str] = None


class GuideChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    current_path: Optional[str] = Field(default=None, max_length=255)
    user_name: Optional[str] = Field(default=None, max_length=100)
    history: Optional[List[GuideChatMessage]] = None


class GuideChatResponse(BaseModel):
    reply: str
    matched_intent: str
    confidence: float
    suggested_actions: List[GuideNavigationAction] = []
    suggested_prompts: List[str] = []
    context_hint: Optional[str] = None
