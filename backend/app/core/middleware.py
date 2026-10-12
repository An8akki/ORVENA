"""
Middleware Components
Request/Response middleware for the application
"""
import time
import uuid
from typing import Callable, Optional, Any
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger
from app.core.exceptions import (
    OrvenaDomainError,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
    ValidationDomainError,
    ExternalServiceError,
    RateLimitError,
    ConflictError,
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                f"Response {response.status_code}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Any = None,
    request: Optional[Request] = None,
) -> JSONResponse:
    """Create standardized error response with CORS support"""
    content = {
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    
    if request_id:
        content["error"]["request_id"] = request_id
    
    if details:
        content["error"]["details"] = details
    
    headers = {}
    if request:
        origin = request.headers.get("origin")
        if origin:
            headers["Access-Control-Allow-Origin"] = origin
            headers["Access-Control-Allow-Credentials"] = "true"
            headers["Access-Control-Allow-Methods"] = "*"
            headers["Access-Control-Allow-Headers"] = "*"
            headers["Vary"] = "Origin"
    
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers if headers else None,
    )


async def domain_error_handler(request: Request, exc: OrvenaDomainError) -> JSONResponse:
    """Handle domain errors"""
    request_id = getattr(request.state, "request_id", None)
    
    # Map exception types to HTTP status codes
    status_code_map = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        PermissionDeniedError: status.HTTP_403_FORBIDDEN,
        UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
        ValidationDomainError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ConflictError: status.HTTP_409_CONFLICT,
        ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
        RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    }
    
    status_code = status_code_map.get(
        type(exc),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    logger.warning(
        f"Domain error: {exc.message}",
        extra={
            "request_id": request_id,
            "error_code": exc.code,
            "error_type": type(exc).__name__,
        }
    )
    
    return create_error_response(
        status_code=status_code,
        error_code=exc.code,
        message=exc.message,
        request_id=request_id,
        details=exc.details,
        request=request,
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors"""
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
        },
        exc_info=True,
    )
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        request_id=request_id,
        request=request,
    )
