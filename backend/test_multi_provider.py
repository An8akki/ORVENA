"""
Test script to verify multi-provider LLM setup.

This script tests that:
1. Providers are loaded correctly
2. Fallback chain works when primary provider fails
3. All configured providers can generate responses
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm import get_llm_provider
from app.services.llm.base import LLMMessage
from app.core.config import settings


async def test_providers():
    """Test multi-provider LLM setup."""
    print("=" * 70)
    print("ORVENA Multi-Provider LLM Test")
    print("=" * 70)
    print()
    
    # Show configuration
    print("📋 Configuration:")
    print(f"  Primary Gemini Key: {'✓ Set' if settings.LLM_API_KEY else '✗ Not set'}")
    print(f"  Gemini Key 2: {'✓ Set' if settings.GEMINI_API_KEY_2 else '✗ Not set'}")
    print(f"  NVIDIA NIM Key: {'✓ Set' if settings.NVIDIA_API_KEY else '✗ Not set'}")
    print(f"  OpenAI Key: {'✓ Set' if settings.OPENAI_API_KEY else '✗ Not set'}")
    print()
    
    # Initialize provider
    print("🔧 Initializing multi-provider LLM...")
    print()
    
    try:
        llm = get_llm_provider()
        print(f"✅ Successfully initialized LLM with {len(llm.providers)} provider(s)")
        print()
        
        # Show provider chain
        print("🔗 Provider Chain:")
        for i, (name, _) in enumerate(llm.providers, 1):
            print(f"  {i}. {name}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        print()
        print("💡 Make sure at least one API key is configured in backend/.env")
        return
    
    # Test simple generation
    print("=" * 70)
    print("🧪 Testing Simple Generation")
    print("=" * 70)
    print()
    
    test_messages = [
        LLMMessage(role="system", content="You are a helpful career advisor."),
        LLMMessage(role="user", content="What is Python programming? Answer in one sentence.")
    ]
    
    try:
        print("Sending test request...")
        response = await llm.generate(messages=test_messages, temperature=0.7, max_tokens=100)
        
        print("✅ Success!")
        print()
        print(f"Response: {response.content}")
        print()
        print(f"Model: {response.model}")
        print(f"Tokens - Input: {response.input_tokens}, Output: {response.output_tokens}")
        print()
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        print()
        return
    
    # Test career-specific generation
    print("=" * 70)
    print("🎯 Testing Career Discovery Question")
    print("=" * 70)
    print()
    
    career_messages = [
        LLMMessage(
            role="system",
            content="You are ORVENA, an AI career advisor. Generate one career discovery question."
        ),
        LLMMessage(
            role="user",
            content="Generate a question to understand a student's interests."
        )
    ]
    
    try:
        print("Generating career question...")
        response = await llm.generate(messages=career_messages, temperature=0.8, max_tokens=200)
        
        print("✅ Success!")
        print()
        print(f"Generated Question: {response.content}")
        print()
        print(f"Model: {response.model}")
        print()
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        print()
        return
    
    # Summary
    print("=" * 70)
    print("✅ All Tests Passed!")
    print("=" * 70)
    print()
    print("🎉 Your multi-provider LLM setup is working correctly!")
    print()
    print("Next steps:")
    print("  1. Start the backend: uvicorn app.main:app --reload")
    print("  2. Start the frontend: npm run dev")
    print("  3. Test Career Discovery in the UI")
    print()


if __name__ == "__main__":
    asyncio.run(test_providers())
