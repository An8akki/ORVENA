"""
Authentication Schemas
Pydantic models for authentication requests and responses
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Complete authentication response"""
    user: UserResponse
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordUpdate(BaseModel):
    """Password update request"""
    new_password: str = Field(..., min_length=8)
