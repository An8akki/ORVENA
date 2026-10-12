"""
Application Configuration
Loads settings from environment variables using Pydantic Settings
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    APP_ENV: str = Field(default="development")
    APP_NAME: str = Field(default="ORVENA")
    DEBUG: bool = Field(default=True)
    API_V1_PREFIX: str = Field(default="/api/v1")
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Database
    DATABASE_URL: str = Field(...)
    DATABASE_POOL_SIZE: int = Field(default=5)
    DATABASE_MAX_OVERFLOW: int = Field(default=10)
    DATABASE_POOL_TIMEOUT: int = Field(default=30)
    
    # Supabase
    SUPABASE_URL: str = Field(...)
    SUPABASE_ANON_KEY: str = Field(...)
    SUPABASE_SERVICE_ROLE_KEY: str = Field(...)
    SUPABASE_JWT_SECRET: str = Field(...)
    SUPABASE_JWT_ISSUER: str = Field(...)
    SUPABASE_STORAGE_BUCKET: str = Field(default="resumes")
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = Field(default=5)
    
    # LLM Provider - Multi-Provider Fallback Chain
    # Primary: Gemini Key 1
    LLM_PROVIDER: str = Field(default="gemini")
    LLM_API_KEY: str = Field(...)
    LLM_MODEL: str = Field(default="gemini-flash-latest")
    LLM_TIMEOUT_SECONDS: int = Field(default=30)
    LLM_MAX_RETRIES: int = Field(default=3)
    LLM_MAX_TOKENS: int = Field(default=2048)
    
    # Fallback: Gemini Key 2 (optional)
    GEMINI_API_KEY_2: Optional[str] = Field(default=None)
    
    # Fallback: NVIDIA NIM Provider
    NVIDIA_API_KEY: Optional[str] = Field(default=None)
    NVIDIA_MODEL: str = Field(default="nvidia/nemotron-3.5-lightning-30b-a3b")
    
    # Fallback: OpenAI Provider
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    
    # Security
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # CORS
    FRONTEND_ORIGIN: str = Field(default="http://localhost:3000")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    
    # Features
    ENABLE_API_DOCS: bool = Field(default=True)
    ENABLE_CAREER_DISCOVERY: bool = Field(default=True)
    ENABLE_RESUME_ANALYSIS: bool = Field(default=True)
    ENABLE_JOB_MATCHING: bool = Field(default=True)
    ENABLE_INTERVIEW_PREP: bool = Field(default=True)
    ENABLE_REGISTRATION: bool = Field(default=True)
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or JSON array"""
        if isinstance(v, str):
            # Try to parse as JSON first
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Fall back to comma-separated
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.APP_ENV == "development"
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes"""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


# Create global settings instance
settings = Settings()
