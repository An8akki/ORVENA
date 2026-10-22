"""
API Endpoints for Orvena Guide Rule-Based Platform Assistant
"""
from typing import List, Dict, Any
from fastapi import APIRouter
from app.services.orvena_guide_engine import orvena_guide_engine, GUIDE_INTENTS
from app.schemas.guide import GuideChatRequest, GuideChatResponse

router = APIRouter()


@router.post("/chat", response_model=GuideChatResponse)
async def guide_chat(request: GuideChatRequest):
    """
    Conversational assistant for platform guidance and navigation.
    Completely deterministic, rule-based, and zero external LLM API dependency.
    """
    return orvena_guide_engine.process_query(request)


@router.get("/topics")
async def list_guide_topics() -> List[Dict[str, Any]]:
    """List supported platform help topics and example queries."""
    topics = []
    for intent in GUIDE_INTENTS:
        topics.append({
            "intent_id": intent["id"],
            "title": intent["id"].replace("_", " ").title(),
            "suggested_prompts": intent.get("suggested_prompts", []),
            "actions": intent.get("actions", []),
        })
    return topics
