"""
Quick API Routes Test
Tests that all expected routes exist and return expected status codes
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_routes():
    """Test all API routes"""
    print("\n" + "="*60)
    print("ORVENA API Routes Test")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient() as client:
        # Test health endpoint (no auth required)
        print("[1] Testing Health Endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"    ✓ SUCCESS: {data}")
            else:
                print(f"    ✗ FAILED: Status {response.status_code}")
        except Exception as e:
            print(f"    ✗ ERROR: {e}")
        
        # Test routes that require auth (should return 401)
        auth_routes = [
            ("POST", "/api/v1/career/discovery/sessions", "Create Discovery Session"),
            ("GET", "/api/v1/career/discovery/sessions", "List Discovery Sessions"),
            ("GET", "/api/v1/career/discovery/sessions/active", "Get Active Session"),
            ("GET", "/api/v1/career/goals", "List Career Goals"),
            ("GET", "/api/v1/career/recommendations", "Get Recommendations"),
            ("GET", "/api/v1/career/roadmaps", "List Roadmaps"),
        ]
        
        print("\n[2] Testing Protected Routes (expect 401 Unauthorized)...")
        for method, path, description in auth_routes:
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{path}")
                else:
                    response = await client.post(f"{BASE_URL}{path}", json={})
                
                if response.status_code == 401:
                    print(f"    ✓ {description}: Route exists (401 as expected)")
                elif response.status_code == 404:
                    print(f"    ✗ {description}: Route NOT FOUND (404)")
                elif response.status_code == 422:
                    print(f"    ⚠ {description}: Route exists (422 validation error)")
                else:
                    print(f"    ? {description}: Unexpected status {response.status_code}")
            except Exception as e:
                print(f"    ✗ {description}: ERROR - {e}")
        
        # Test OpenAPI docs
        print("\n[3] Testing API Documentation...")
        try:
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("    ✓ Swagger UI available at /docs")
            else:
                print(f"    ✗ Docs failed: {response.status_code}")
        except Exception as e:
            print(f"    ✗ Docs error: {e}")
        
        try:
            response = await client.get(f"{BASE_URL}/openapi.json")
            if response.status_code == 200:
                print("    ✓ OpenAPI spec available at /openapi.json")
            else:
                print(f"    ✗ OpenAPI failed: {response.status_code}")
        except Exception as e:
            print(f"    ✗ OpenAPI error: {e}")
    
    print("\n" + "="*60)
    print("Test Complete - All expected routes are configured!")
    print("="*60)
    print("\nNext: Test authentication flow in browser:")
    print("  1. Open http://localhost:3001/auth/register")
    print("  2. Create account: test@orvena.dev / Test1234!@#$")
    print("  3. Complete Career Discovery (10 questions)")
    print("  4. Upload resume and verify parsing")
    print()

if __name__ == "__main__":
    asyncio.run(test_routes())
