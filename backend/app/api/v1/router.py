"""
API V1 Router
Aggregates all v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, student, career, resume, system, jobs

api_router = APIRouter()

# Include authentication router
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include student profile router
api_router.include_router(student.router, prefix="/student", tags=["Student Profile"])

# Include career router
api_router.include_router(career.router, prefix="/career", tags=["Career Discovery"])

# Include resume router
api_router.include_router(resume.router, prefix="/resumes", tags=["Resume"])

# Deterministic, profile-specific job matching.
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])

# Include system monitoring router (no prefix - goes at root level)
api_router.include_router(system.router, tags=["System"])

# TODO: Include other routers when implemented
# api_router.include_router(interviews.router, prefix="/interview", tags=["Interviews"])


@api_router.get("/ping")
async def ping():
    """Simple ping endpoint for testing"""
    return {"message": "pong"}
