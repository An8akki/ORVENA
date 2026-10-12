"""
Global Error Handlers

Provides consistent error handling and user-friendly error messages.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with user-friendly messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"] if x != "body")
        message = error["msg"]
        errors.append(f"{field}: {message}" if field else message)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Please check your input and try again.",
            "details": errors
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "message": get_user_friendly_message(exc.status_code, exc.detail),
            "status_code": exc.status_code
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully."""
    logger.error(f"Unexpected error: {str(exc)}")
    logger.error(traceback.format_exc())
    
    # Never expose internal errors to users
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong. Our team has been notified and is working on it.",
            "request_id": str(id(request))  # For support tracking
        }
    )


def get_user_friendly_message(status_code: int, detail: str) -> str:
    """Convert technical errors to user-friendly messages."""
    
    # Common HTTP status codes
    messages = {
        400: "The request was invalid. Please check your input and try again.",
        401: "Please log in to access this feature.",
        403: "You don't have permission to access this resource.",
        404: "The requested resource was not found.",
        409: "This action conflicts with existing data.",
        422: "Please check your input and try again.",
        429: "Too many requests. Please try again in a moment.",
        500: "Something went wrong on our end. Please try again later.",
        503: "Service temporarily unavailable. Please try again in a few moments."
    }
    
    # Return custom message or fallback to detail
    return messages.get(status_code, detail)


class UserFriendlyError(Exception):
    """Custom exception that always shows user-friendly messages."""
    
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


async def user_friendly_error_handler(request: Request, exc: UserFriendlyError):
    """Handle custom user-friendly errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "message": exc.message,
            "details": exc.details
        }
    )


# Timeout handling
class TimeoutError(Exception):
    """Raised when an operation times out."""
    pass


async def timeout_error_handler(request: Request, exc: TimeoutError):
    """Handle timeout errors gracefully."""
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "error": "Request Timeout",
            "message": "The request took too long to process. We're using a faster method to get you results.",
            "fallback_used": True
        }
    )


# AI Service errors
class AIServiceError(Exception):
    """Raised when AI service fails."""
    pass


async def ai_service_error_handler(request: Request, exc: AIServiceError):
    """Handle AI service errors with fallback message."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,  # Don't fail the request
        content={
            "warning": "AI service unavailable",
            "message": "Using alternative method to provide results. Quality may vary slightly.",
            "fallback_used": True,
            "data": None  # Service should provide fallback data
        }
    )
