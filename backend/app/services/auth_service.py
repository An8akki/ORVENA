"""
Authentication Service
Business logic for user authentication and authorization
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models.user import User
from app.db.models.student import StudentProfile
from app.core.exceptions import UnauthorizedError, ValidationDomainError
from app.core.logging import logger


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_id: UUID, email: str) -> User:
        """Create a new user record"""
        # Check if user already exists
        existing_user = await self.get_user_by_id(user_id)
        if existing_user:
            logger.info(f"User {user_id} already exists")
            return existing_user
        
        user = User(id=user_id, email=email)
        self.db.add(user)
        await self.db.flush()
        
        logger.info(f"Created user: {user_id}")
        return user
    
    async def create_student_profile(
        self,
        user_id: UUID,
        email: str,
        full_name: str
    ) -> StudentProfile:
        """Create student profile for new user"""
        # Ensure user exists
        user = await self.get_user_by_id(user_id)
        if not user:
            user = await self.create_user(user_id, email)
        
        # Check if profile already exists
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        existing_profile = result.scalar_one_or_none()
        
        if existing_profile:
            logger.info(f"Profile for user {user_id} already exists")
            return existing_profile
        
        profile = StudentProfile(
            user_id=user_id,
            email=email,
            full_name=full_name
        )
        self.db.add(profile)
        await self.db.flush()
        
        logger.info(f"Created student profile for user: {user_id}")
        return profile
    
    async def get_student_profile(self, user_id: UUID) -> Optional[StudentProfile]:
        """Get student profile by user ID"""
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def ensure_user_and_profile(
        self,
        user_id: UUID,
        email: str,
        full_name: Optional[str] = None
    ) -> tuple[User, StudentProfile]:
        """Ensure user and profile exist, create if needed"""
        user = await self.get_user_by_id(user_id)
        if not user:
            user = await self.create_user(user_id, email)
        
        profile = await self.get_student_profile(user_id)
        if not profile:
            if not full_name:
                full_name = email.split('@')[0]
            profile = await self.create_student_profile(user_id, email, full_name)
        
        return user, profile


# Singleton instance
auth_service = AuthService
