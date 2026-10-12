"""
ORVENA FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    domain_error_handler,
    generic_error_handler,
)
from app.core.exceptions import OrvenaDomainError
from app.api.v1.router import api_router


# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(
        "Starting ORVENA API",
        extra={
            "version": "1.0.0",
            "environment": settings.APP_ENV,
            "debug": settings.DEBUG,
        }
    )
    
    # Validate required settings
    if not settings.DATABASE_URL:
        logger.error("DATABASE_URL is not configured")
        raise ValueError("DATABASE_URL must be set")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ORVENA API")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered career, resume, job-matching and interview preparation platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENABLE_API_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_API_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_API_DOCS else None,
    lifespan=lifespan,
)

# Middleware - order matters!
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(OrvenaDomainError, domain_error_handler)
app.add_exception_handler(Exception, generic_error_handler)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "1.0.0",
            "environment": settings.APP_ENV,
        }
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "ORVENA API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_PREFIX}/docs" if settings.ENABLE_API_DOCS else None,
    }


# Simple test endpoint to bypass auth
@app.get("/test-direct", tags=["Test"])
async def test_direct():
    """Test endpoint without auth"""
    import sys
    print("TEST ENDPOINT CALLED", file=sys.stderr)
    return {"message": "Test successful"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
