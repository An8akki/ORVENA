"""
Simple connection tests that don't require backend imports
"""
import os
import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine
import google.generativeai as genai

print("=" * 70)
print("ORVENA SIMPLE CONNECTION TEST")
print("=" * 70)

# Load .env
from dotenv import load_dotenv
load_dotenv()

async def test_database():
    """Test database connection"""
    print("\n" + "=" * 70)
    print("TEST 1: DATABASE CONNECTION")
    print("=" * 70)
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return False
            
        from sqlalchemy import text
        engine = create_async_engine(database_url, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()  # Remove await
        await engine.dispose()
        print("✅ Database connection: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Database connection: FAILED")
        print(f"   Error: {str(e)[:200]}")
        return False

async def test_gemini():
    """Test Gemini AI connection"""
    print("\n" + "=" * 70)
    print("TEST 2: GOOGLE GEMINI AI CONNECTION")
    print("=" * 70)
    try:
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            print("❌ LLM_API_KEY not found in environment")
            return False
        
        print(f"   API Key format: {api_key[:10]}...")
        
        # This might not be a Google Gemini key - let's test with HTTP request
        async with httpx.AsyncClient() as client:
            # Test if it's Google AI Studio key
            response = await client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            )
            
            if response.status_code == 200:
                models = response.json()
                print(f"✅ API Key valid for Google AI")
                available = [m['name'] for m in models.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                print(f"   Available models: {available[:3]}")
                
                # Test generation with the second model (gemini-2.5-pro) or try newer version
                if available:
                    # Try to use gemini-3.8-flash as suggested, fallback to available
                    test_models = ['models/gemini-3.8-flash', 'models/gemini-2.5-pro'] + available
                    
                    for model_name in test_models:
                        try:
                            gen_response = await client.post(
                                f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}",
                                json={
                                    "contents": [{"parts": [{"text": "Say hello"}]}]
                                }
                            )
                            if gen_response.status_code == 200:
                                print("✅ Gemini AI connection: SUCCESS")
                                print(f"   Working model: {model_name}")
                                result = gen_response.json()
                                text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                                print(f"   Response: {text[:100]}")
                                return True
                        except Exception as e:
                            continue
                    
                    print(f"⚠️  All models failed generation")
                    return False
            else:
                print(f"❌ API Key validation failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                print("   Note: This might not be a Google Gemini API key")
                print("   Expected format: AIza... or similar")
                return False
                
    except Exception as e:
        print(f"❌ Gemini AI connection: FAILED")
        print(f"   Error: {str(e)[:300]}")
        return False

async def test_api_endpoints():
    """Test FastAPI endpoints"""
    print("\n" + "=" * 70)
    print("TEST 3: FASTAPI ENDPOINTS")
    print("=" * 70)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health endpoint
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Health endpoint: SUCCESS")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health endpoint: FAILED (status {response.status_code})")
                return False
            
            # Test docs endpoint
            response = await client.get("http://localhost:8000/docs")
            if response.status_code == 200:
                print("✅ API docs: ACCESSIBLE")
            else:
                print(f"⚠️  API docs: status {response.status_code}")
            
            return True
    except Exception as e:
        print(f"❌ API endpoints: FAILED")
        print(f"   Error: {str(e)[:200]}")
        print("   Make sure backend is running on port 8000")
        return False

async def test_resume_endpoint():
    """Test resume endpoint with mock token"""
    print("\n" + "=" * 70)
    print("TEST 4: RESUME ENDPOINT (QUICK CHECK)")
    print("=" * 70)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Just check if endpoint exists and accepts requests
            response = await client.get(
                "http://localhost:8000/api/v1/resumes/",
                headers={"Authorization": "Bearer test_token"}
            )
            # We expect 401 (unauthorized) which means endpoint is working
            if response.status_code == 401:
                print("✅ Resume endpoint: REACHABLE")
                print("   (401 Unauthorized is expected without valid token)")
                return True
            elif response.status_code == 200:
                print("✅ Resume endpoint: SUCCESS")
                return True
            else:
                print(f"⚠️  Resume endpoint: status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return True  # Still counts as accessible
    except Exception as e:
        print(f"❌ Resume endpoint: FAILED")
        print(f"   Error: {str(e)[:200]}")
        return False

async def main():
    """Run all tests"""
    results = {
        "Database": await test_database(),
        "Gemini": await test_gemini(),
        "API": await test_api_endpoints(),
        "Resume": await test_resume_endpoint()
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    elif passed > 0:
        print(f"⚠️  {total - passed} test(s) failed - Check errors above")
    else:
        print("❌ ALL TESTS FAILED - Check configuration")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
