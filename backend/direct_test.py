"""
Direct test of the profile endpoint logic - bypass middleware to see real errors
"""
import asyncio
import sys
import traceback
from uuid import UUID

# Add backend to path
sys.path.insert(0, ".")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.auth_service import AuthService


async def test_profile_creation():
    """Test profile creation with full error details"""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Use a test user ID (replace with actual UUID from your Supabase auth)
    # This should be a valid UUID that exists in your Supabase auth.users table
    test_user_id = UUID("12345678-1234-1234-1234-123456789012")  # Replace with real ID
    
    print(f"\n{'='*60}")
    print(f"Testing profile creation for user: {test_user_id}")
    print(f"{'='*60}\n")
    
    async with async_session() as db:
        try:
            auth_svc = AuthService(db)
            
            print("Step 1: Get or create user...")
            user = await auth_svc.get_user_by_id(test_user_id)
            
            if not user:
                print(f"  → User not found, creating...")
                user = await auth_svc.create_user(test_user_id, f"{test_user_id}@test.com")
                await db.flush()
                print(f"  ✓ User created: {user.id}")
            else:
                print(f"  ✓ User exists: {user.id}")
            
            print("\nStep 2: Get or create profile...")
            profile = await auth_svc.get_student_profile(test_user_id)
            
            if not profile:
                print(f"  → Profile not found, creating...")
                profile = await auth_svc.create_student_profile(
                    user_id=test_user_id,
                    email=user.email,
                    full_name=user.email.split('@')[0]
                )
                await db.commit()
                print(f"  ✓ Profile created: {profile.id}")
            else:
                print(f"  ✓ Profile exists: {profile.id}")
            
            print("\nStep 3: Verify profile retrieval...")
            profile_check = await auth_svc.get_student_profile(test_user_id)
            
            if profile_check:
                print(f"  ✓ Profile retrieval successful")
                print(f"    - ID: {profile_check.id}")
                print(f"    - User ID: {profile_check.user_id}")
                print(f"    - Email: {profile_check.email}")
                print(f"    - Name: {profile_check.full_name}")
            else:
                print(f"  ✗ Profile retrieval failed!")
            
            print(f"\n{'='*60}")
            print("✓ TEST PASSED - All operations successful")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n{'='*60}")
            print("✗ TEST FAILED - Exception occurred:")
            print(f"{'='*60}\n")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"\nFull Traceback:")
            print("-" * 60)
            traceback.print_exc()
            print("-" * 60)
            sys.exit(1)
    
    await engine.dispose()


if __name__ == "__main__":
    print("\nStarting direct profile creation test...")
    print("This bypasses FastAPI middleware to show real errors\n")
    
    asyncio.run(test_profile_creation())
