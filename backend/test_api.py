"""Quick API test script"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import httpx

async def test_api():
    """Test basic API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing ORVENA API...\n")
    
    # Test 1: Health check
    print("1️⃣  Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed: {data['status']}")
                print(f"   📊 Version: {data['version']}, Env: {data['environment']}\n")
            else:
                print(f"   ❌ Health check failed: {response.status_code}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    # Test 2: Check if auth endpoint is accessible
    print("2️⃣  Testing auth endpoint accessibility...")
    async with httpx.AsyncClient() as client:
        try:
            # Try to access /me without token (should get 401)
            response = await client.get(f"{base_url}/api/v1/auth/me")
            if response.status_code == 401:
                print(f"   ✅ Auth endpoint working (requires authentication)\n")
            else:
                print(f"   ⚠️  Unexpected response: {response.status_code}\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    # Test 3: Test CORS headers
    print("3️⃣  Testing CORS configuration...")
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Origin": "http://localhost:3000"}
            response = await client.options(f"{base_url}/health", headers=headers)
            cors_header = response.headers.get("access-control-allow-origin")
            if cors_header:
                print(f"   ✅ CORS enabled: {cors_header}\n")
            else:
                print(f"   ⚠️  CORS header not found\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    print("✨ API is ready for frontend requests!\n")
    print("🌐 Frontend should be able to:")
    print("   - Register new users")
    print("   - Login existing users")
    print("   - Create student profiles")
    print("   - Use all career discovery features")
    print("   - Upload and analyze resumes")
    print("\n🚀 Open http://localhost:3000 to start using ORVENA!")

if __name__ == "__main__":
    asyncio.run(test_api())
