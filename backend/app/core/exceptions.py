"""
Custom Exception Classes
Defines application-specific exceptions with HTTP status codes
"""
from typing import Any, Optional


class OrvenaDomainError(Exception):
    """Base exception for all domain errors"""
    
    def __init__(
        self,
        message: str,
        code: str = "DOMAIN_ERROR",
        details: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class NotFoundError(OrvenaDomainError):
    """Resource not found error (404)"""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(message=message, code="NOT_FOUND", details=details)


class PermissionDeniedError(OrvenaDomainError):
    """Permission denied error (403)"""
    
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(message=message, code="PERMISSION_DENIED", details=details)


class UnauthorizedError(OrvenaDomainError):
    """Unauthorized error (401)"""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[Any] = None):
        super().__init__(message=message, code="UNAUTHORIZED", details=details)


class ValidationDomainError(OrvenaDomainError):
    """Business validation error (422)"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class ConflictError(OrvenaDomainError):
    """Resource conflict error (409)"""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Any] = None):
        super().__init__(message=message, code="CONFLICT", details=details)


class ExternalServiceError(OrvenaDomainError):
    """External service error (502)"""
    
    def __init__(self, message: str, service: str, details: Optional[Any] = None):
        self.service = service
        super().__init__(
            message=f"{service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details=details
        )


class LLMProviderError(ExternalServiceError):
    """LLM provider error"""
    
    def __init__(self, message: str, provider: str = "LLM", details: Optional[Any] = None):
        super().__init__(message=message, service=provider, details=details)


class LLMTimeoutError(LLMProviderError):
    """LLM request timeout"""
    
    def __init__(self, message: str = "LLM request timed out", provider: str = "LLM"):
        super().__init__(message=message, provider=provider)
        self.code = "LLM_TIMEOUT"


class LLMRateLimitError(LLMProviderError):
    """LLM rate limit exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        provider: str = "LLM",
        retry_after: Optional[int] = None
    ):
        super().__init__(message=message, provider=provider)
        self.code = "LLM_RATE_LIMIT"
        self.retry_after = retry_after


class LLMValidationError(LLMProviderError):
    """LLM output validation failed"""
    
    def __init__(self, message: str, provider: str = "LLM", details: Optional[Any] = None):
        super().__init__(message=message, provider=provider, details=details)
        self.code = "LLM_VALIDATION_ERROR"


class StorageError(ExternalServiceError):
    """File storage error"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message=message, service="Storage", details=details)


class DocumentParsingError(OrvenaDomainError):
    """Document parsing error"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message=message, code="DOCUMENT_PARSING_ERROR", details=details)


class DatabaseOperationError(OrvenaDomainError):
    """Database operation error"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message=message, code="DATABASE_ERROR", details=details)


class RateLimitError(OrvenaDomainError):
    """Rate limit exceeded (429)"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Any] = None
    ):
        super().__init__(message=message, code="RATE_LIMIT_EXCEEDED", details=details)
        self.retry_after = retry_after


# Alias for backward compatibility
ValidationError = ValidationDomainError
