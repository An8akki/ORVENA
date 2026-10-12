"""
API Dependencies
Dependency injection functions for FastAPI routes
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.logging import logger

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def ensure_user_exists(db: AsyncSession, user_id: str, email: str = "") -> None:
    """
    Ensure user exists in database, create if needed.
    Called automatically when a user makes their first authenticated request.
    """
    from uuid import UUID
    from app.services.auth_service import AuthService
    
    try:
        user_uuid = UUID(user_id)
        auth_svc = AuthService(db)
        
        # Check if user exists
        user = await auth_svc.get_user_by_id(user_uuid)
        if not user:
            # Create user record
            user = await auth_svc.create_user(user_uuid, email or f"{user_id}@temp.com")
            await db.flush()
            logger.info(f"Auto-created user record for {user_id}")
    except Exception as e:
        logger.error(f"Error ensuring user exists: {e}")
        # Don't fail the request if user creation fails


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Dependency to get current authenticated user ID from JWT token.
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(user_id: str = Depends(get_current_user_id)):
            ...
    
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        from app.core.security import verify_token
        
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise UnauthorizedError("Invalid token payload")
        
        return user_id
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Dependency to get current user ID if authenticated, None otherwise
    Useful for endpoints that can work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user_id(credentials)
    except HTTPException:
        return None
