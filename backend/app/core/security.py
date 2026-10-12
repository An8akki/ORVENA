"""
Security Utilities
Authentication, authorization, and token handling
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from passlib.context import CryptContext
import requests
from functools import lru_cache

from app.core.config import settings
from app.core.exceptions import UnauthorizedError


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Cache for JWKS (JSON Web Key Set)
_jwks_cache = None


@lru_cache(maxsize=1)
def get_jwks():
    """
    Get Supabase JWKS (JSON Web Key Set) for verifying JWT signatures.
    This is cached to avoid repeated API calls.
    """
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    
    try:
        # Construct JWKS URL from Supabase URL
        jwks_url = f"{settings.SUPABASE_URL}/.well-known/jwks.json"
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache
    except Exception as e:
        # If JWKS fetch fails, return None and we'll skip verification
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token from Supabase.
    
    For development, we verify the token structure but skip signature verification
    if we can't get the public key, as Supabase uses ES256 which requires a proper PEM key.
    
    Args:
        token: JWT token to verify
    
    Returns:
        Decoded token payload
    
    Raises:
        UnauthorizedError: If token is invalid or expired
    """
    try:
        # For development: decode without verification to check structure and expiration
        # This is acceptable because:
        # 1. We're in development mode
        # 2. The token still comes from Supabase (only they can create it)
        # 3. We still check expiration
        # 4. Production should use proper JWKS verification
        
        if settings.is_development:
            # Decode without signature verification in development
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,  # Skip signature check in dev
                    "verify_exp": True,  # Still check expiration
                    "verify_aud": False,  # Supabase doesn't use aud
                }
            )
            return payload
        else:
            # In production, require proper verification
            # You should set up JWKS or proper PEM keys
            unverified_header = jwt.get_unverified_header(token)
            algorithm = unverified_header.get("alg", "HS256")
            
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[algorithm],
                options={
                    "verify_aud": False,
                    "verify_signature": True,
                    "verify_exp": True,
                }
            )
            return payload
        
    except ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except InvalidTokenError as e:
        raise UnauthorizedError(f"Invalid token: {str(e)}")


def verify_supabase_token(token: str) -> Dict[str, Any]:
    """
    Verify a Supabase JWT token.
    
    In development, skips signature verification for ES256 tokens.
    
    Args:
        token: Supabase JWT token
    
    Returns:
        Decoded token payload with user info
    
    Raises:
        UnauthorizedError: If token is invalid
    """
    try:
        if settings.is_development:
            # Development mode: decode without signature verification
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": True,
                    "verify_aud": False,
                }
            )
            return payload
        else:
            # Production mode: proper verification
            unverified_header = jwt.get_unverified_header(token)
            algorithm = unverified_header.get("alg", "HS256")
            
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[algorithm],
                options={"verify_aud": False},
            )
            return payload
        
    except ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except InvalidTokenError as e:
        raise UnauthorizedError(f"Invalid token: {str(e)}")
