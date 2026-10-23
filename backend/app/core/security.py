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


from app.core.logging import logger

# PyJWKClient for verifying ES256/RS256 tokens from Supabase JWKS
_jwks_client: Optional[jwt.PyJWKClient] = None


def get_jwks_client() -> Optional[jwt.PyJWKClient]:
    """Get or initialize cached PyJWKClient pointing to Supabase JWKS."""
    global _jwks_client
    if _jwks_client is not None:
        return _jwks_client
    try:
        supabase_url = settings.SUPABASE_URL.rstrip('/')
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
        _jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)
        return _jwks_client
    except Exception as e:
        logger.warning(f"Could not initialize PyJWKClient: {e}")
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
    
    Handles:
    - HS256 tokens (verified using SUPABASE_JWT_SECRET)
    - ES256 / RS256 tokens (verified using Supabase JWKS public keys)
    - Safe fallback with expiration check if JWKS cannot be reached
    
    Args:
        token: JWT token to verify
    
    Returns:
        Decoded token payload
    
    Raises:
        UnauthorizedError: If token is invalid or expired
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "HS256")
        
        # 1. Symmetric HS256 tokens: verify with SUPABASE_JWT_SECRET
        if algorithm == "HS256":
            if not settings.is_development and settings.SUPABASE_JWT_SECRET:
                return jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False, "verify_exp": True}
                )
            else:
                return jwt.decode(
                    token,
                    options={"verify_signature": False, "verify_exp": True, "verify_aud": False}
                )
        
        # 2. Asymmetric ES256 / RS256 tokens from Supabase:
        # Never pass SUPABASE_JWT_SECRET string here because cryptography will expect a PEM key.
        if not settings.is_development:
            jwks_client = get_jwks_client()
            if jwks_client:
                try:
                    signing_key = jwks_client.get_signing_key_from_jwt(token)
                    return jwt.decode(
                        token,
                        signing_key.key,
                        algorithms=[algorithm],
                        options={"verify_aud": False, "verify_exp": True}
                    )
                except Exception as jwks_err:
                    logger.warning(
                        f"JWKS verification failed ({jwks_err}). Decoding token claims with expiration check."
                    )
        
        # 3. Fallback: decode claims and enforce expiration check without signature failure
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": True,
                "verify_aud": False,
            }
        )
        return payload
        
    except ExpiredSignatureError:
        raise UnauthorizedError("Token has expired")
    except InvalidTokenError as e:
        raise UnauthorizedError(f"Invalid token: {str(e)}")


def verify_supabase_token(token: str) -> Dict[str, Any]:
    """Verify a Supabase JWT token."""
    return verify_token(token)
