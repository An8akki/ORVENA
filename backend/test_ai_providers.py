"""Test script to verify AI providers are working."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini():
    """Test Gemini API."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("LLM_API_KEY")
        model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
        
        print(f"\n🧪 Testing Gemini API...")
        print(f"Model: {model_name}")
        print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT SET")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content("Say 'Hello from Gemini!'")
        print(f"✅ Gemini Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Gemini Error: {str(e)}")
        return False


async def test_nvidia():
    """Test NVIDIA NIM API with multiple models."""
    import httpx
    
    api_key = os.getenv("NVIDIA_API_KEY")
    
    # Try multiple models
    models_to_try = [
        "deepseek-ai/deepseek-r1",
        "qwen/qwen3.5-122b-a10b",
        "nvidia/nemotron-3.5-lightning-30b-a3b",
        os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
    ]
    
    for model_name in models_to_try:
        try:
            print(f"\n🧪 Testing NVIDIA NIM API...")
            print(f"Model: {model_name}")
            print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT SET")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Say 'Hello from NVIDIA!'"}],
                "temperature": 0.7,
                "max_tokens": 100
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    print(f"❌ Model {model_name} Error ({response.status_code}): {response.text[:200]}")
                    continue
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                print(f"✅ NVIDIA Response: {content}")
                print(f"✅ SUCCESS! Working model: {model_name}")
                return True
                
        except Exception as e:
            print(f"❌ Model {model_name} Error: {str(e)[:200]}")
            continue
    
    print(f"\n❌ All NVIDIA models failed")
    return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 ORVENA AI Provider Tests")
    print("=" * 60)
    
    gemini_ok = await test_gemini()
    nvidia_ok = await test_nvidia()
    
    print("\n" + "=" * 60)
    print("📊 Results:")
    print("=" * 60)
    print(f"Gemini: {'✅ WORKING' if gemini_ok else '❌ FAILED'}")
    print(f"NVIDIA: {'✅ WORKING' if nvidia_ok else '❌ FAILED'}")
    
    if gemini_ok or nvidia_ok:
        print("\n🎉 At least one provider is working!")
    else:
        print("\n⚠️  All providers failed. Check your API keys and models.")


if __name__ == "__main__":
    asyncio.run(main())
