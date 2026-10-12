"""
Authentication Endpoints
API routes for user authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user_id
from app.schemas.auth import UserResponse
from app.services.auth_service import AuthService
from app.core.logging import logger

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user information
    
    This endpoint verifies the JWT token and returns the user's basic info.
    The actual authentication is handled by Supabase Auth on the frontend.
    """
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
        
        auth_service = AuthService(db)
        
        # Get user from database
        user = await auth_service.get_user_by_id(user_uuid)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get profile for full_name
        profile = await auth_service.get_student_profile(user_uuid)
        full_name = profile.full_name if profile else None
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=full_name,
            created_at=user.created_at.isoformat()
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user information"
        )


@router.post("/sync", status_code=status.HTTP_201_CREATED)
async def sync_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync user from Supabase Auth to our database
    
    This endpoint is called after successful registration or first login
    to ensure the user exists in our database with a profile.
    """
    try:
        from uuid import UUID
        user_uuid = UUID(user_id)
        
        auth_service = AuthService(db)
        
        # This will create user and profile if they don't exist
        user, profile = await auth_service.ensure_user_and_profile(
            user_uuid,
            email="",  # Will be updated from token metadata
            full_name=None
        )
        
        await db.commit()
        
        return {
            "message": "User synced successfully",
            "user_id": str(user.id),
            "profile_id": str(profile.id)
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except Exception as e:
        logger.error(f"Error syncing user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync user"
        )


@router.get("/check", status_code=status.HTTP_200_OK)
async def check_auth(user_id: str = Depends(get_current_user_id)):
    """
    Simple endpoint to verify authentication
    Returns 200 if authenticated, 401 if not
    """
    return {
        "authenticated": True,
        "user_id": user_id
    }
