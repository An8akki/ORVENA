"""
Direct test of career session creation with full error details
"""
import asyncio
import sys
import traceback
from uuid import uuid4
from datetime import datetime

sys.path.insert(0, ".")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.auth_service import AuthService
from app.db.models.career import CareerDiscoverySession


async def test_session_creation():
    """Test session creation with full error details"""
    
    # Create async engine with SQL echo
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,  # Show all SQL
        pool_pre_ping=True,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    test_user_id = uuid4()
    
    print(f"\n{'='*60}")
    print(f"Testing career session creation")
    print(f"User ID: {test_user_id}")
    print(f"{'='*60}\n")
    
    async with async_session() as db:
        try:
            # Step 1: Create user
            print("Step 1: Creating user...")
            auth_svc = AuthService(db)
            user = await auth_svc.create_user(test_user_id, f"{test_user_id}@test.com")
            await db.flush()
            print(f"  ✓ User created: {user.id}")
            
            # Step 2: Create profile
            print("\nStep 2: Creating profile...")
            profile = await auth_svc.create_student_profile(
                user_id=test_user_id,
                email=user.email,
                full_name="Test User"
            )
            await db.commit()
            print(f"  ✓ Profile created: {profile.id}")
            
            # Step 3: Create session - THE FAILING PART
            print("\nStep 3: Creating career discovery session...")
            print("  Creating session object...")
            
            session = CareerDiscoverySession(
                student_profile_id=profile.id,
                session_type="initial",
                status="in_progress",
                current_phase="initial",
            )
            
            print(f"  Session object created: {session}")
            print(f"    - student_profile_id: {session.student_profile_id}")
            print(f"    - session_type: {session.session_type}")
            print(f"    - status: {session.status}")
            print(f"    - current_phase: {session.current_phase}")
            
            print("  Adding to session...")
            db.add(session)
            
            print("  Flushing to database...")
            await db.flush()
            
            print("  Committing...")
            await db.commit()
            
            print("  Refreshing...")
            await db.refresh(session)
            
            print(f"\n  ✓ Session created: {session.id}")
            print(f"\n{'='*60}")
            print("✓ TEST PASSED")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n{'='*60}")
            print("✗ TEST FAILED - Exception occurred:")
            print(f"{'='*60}\n")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            
            # Check for specific error types
            if hasattr(e, 'orig'):
                print(f"\nOriginal Error: {e.orig}")
            
            if hasattr(e, 'params'):
                print(f"\nSQL Params: {e.params}")
            
            if hasattr(e, 'statement'):
                print(f"\nSQL Statement: {e.statement}")
            
            print(f"\nFull Traceback:")
            print("-" * 60)
            traceback.print_exc()
            print("-" * 60)
            sys.exit(1)
    
    await engine.dispose()


if __name__ == "__main__":
    print("\nStarting direct career session creation test...")
    print("This will show SQL queries and detailed errors\n")
    
    asyncio.run(test_session_creation())
