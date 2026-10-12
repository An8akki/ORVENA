"""API endpoints for career discovery and recommendations."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user_id
from app.services.student_service import student_service
from app.services.career_discovery_service import career_discovery_service
from app.services.career_recommendation_service import career_recommendation_service
from app.services.auth_service import AuthService
from app.schemas.career import (
    CareerDiscoverySessionCreate,
    CareerDiscoverySessionResponse,
    CareerDiscoveryResponseCreate,
    CareerDiscoveryResponseResponse,
    NextQuestionRequest,
    NextQuestionResponse,
    SubmitAnswerRequest,
    SessionAnalysisResponse,
    CareerGoalCreate,
    CareerGoalUpdate,
    CareerGoalResponse,
    CareerRecommendationResponse,
    CareerRoadmapCreate,
    CareerRoadmapResponse,
    UpdateMilestoneStatusRequest,
    RoadmapMilestoneResponse,
)
from app.core.exceptions import NotFoundError

router = APIRouter()


async def ensure_profile_exists(db: AsyncSession, user_id: UUID):
    """
    Ensure student profile exists, create if needed.
    Returns the profile.
    """
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        # Auto-create user and profile
        auth_svc = AuthService(db)
        user = await auth_svc.get_user_by_id(user_id)
        if not user:
            user = await auth_svc.create_user(user_id, f"{user_id}@supabase.user")
            await db.flush()
        
        profile = await auth_svc.create_student_profile(
            user_id=user_id,
            email=user.email,
            full_name=user.email.split('@')[0]
        )
        await db.flush()
    return profile


# Discovery Session Endpoints
@router.post(
    "/discovery/sessions",
    response_model=CareerDiscoverySessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_discovery_session(
    session_data: CareerDiscoverySessionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a new career discovery session. Auto-creates profile if needed."""
    profile = await ensure_profile_exists(db, user_id)
    session = await career_discovery_service.create_session(
        db, profile.id, session_data
    )
    return session


@router.get("/discovery/sessions", response_model=List[CareerDiscoverySessionResponse])
async def get_discovery_sessions(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all discovery sessions."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    sessions = await career_discovery_service.get_sessions(db, profile.id)
    return sessions


@router.get("/discovery/sessions/active", response_model=CareerDiscoverySessionResponse)
async def get_active_discovery_session(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get the active discovery session. Auto-creates profile if needed."""
    profile = await ensure_profile_exists(db, user_id)
    session = await career_discovery_service.get_active_session(db, profile.id)
    if not session:
        raise NotFoundError("No active session found")
    return session


@router.get(
    "/discovery/sessions/{session_id}",
    response_model=CareerDiscoverySessionResponse,
)
async def get_discovery_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get a specific discovery session."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")

    session = await career_discovery_service.get_session(db, session_id, profile.id)
    if not session:
        raise NotFoundError("Session not found")
    
    return session


@router.post("/discovery/next-question", response_model=NextQuestionResponse)
async def get_next_question(
    request_data: NextQuestionRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get the next discovery question."""
    profile = await ensure_profile_exists(db, user_id)

    session = await career_discovery_service.get_session(db, request_data.session_id, profile.id)
    if not session:
        raise NotFoundError("Session not found")

    question_data = await career_discovery_service.generate_next_question(
        db, session, profile.id
    )

    return NextQuestionResponse(
        question_number=len(session.responses) + 1,
        question_text=question_data["question_text"],
        question_type=question_data["question_type"],
        options=question_data.get("options"),
        session_id=request_data.session_id,
    )


@router.post(
    "/discovery/submit-answer",
    response_model=CareerDiscoveryResponseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_answer(
    answer: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Submit an answer to a discovery question."""
    profile = await ensure_profile_exists(db, user_id)

    response_data = CareerDiscoveryResponseCreate(
        sequence_number=answer.question_number,
        question_text=answer.question_text,
        response_text=answer.response_text,
    )

    response = await career_discovery_service.add_response(
        db, answer.session_id, profile.id, response_data
    )
    return response


@router.post("/discovery/sessions/{session_id}/complete")
async def complete_discovery_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Complete a discovery session."""
    profile = await ensure_profile_exists(db, user_id)

    session = await career_discovery_service.complete_session(
        db, session_id, profile.id
    )
    return {"message": "Session completed successfully", "session_id": session.id}


@router.get(
    "/discovery/sessions/{session_id}/analysis",
    response_model=SessionAnalysisResponse,
)
async def analyze_discovery_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Analyze a discovery session."""
    profile = await ensure_profile_exists(db, user_id)

    analysis = await career_discovery_service.analyze_responses(
        db, session_id, profile.id
    )

    return SessionAnalysisResponse(
        session_id=session_id,
        insights=analysis,
        summary=analysis.get("raw_analysis", "Analysis completed"),
    )


# Career Goals Endpoints
@router.get("/goals", response_model=List[CareerGoalResponse])
async def get_career_goals(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all career goals."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")
    
    goals = await career_recommendation_service.get_goals(db, profile.id)
    return goals


@router.post(
    "/goals",
    response_model=CareerGoalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_career_goal(
    goal_data: CareerGoalCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a career goal."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")
    
    goal = await career_recommendation_service.create_goal(db, profile.id, goal_data)
    return goal


@router.patch("/goals/{goal_id}", response_model=CareerGoalResponse)
async def update_career_goal(
    goal_id: UUID,
    goal_data: CareerGoalUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update a career goal."""
    # TODO: Implement in career service
    raise NotFoundError("Not implemented yet")


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_career_goal(
    goal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Delete a career goal."""
    # TODO: Implement in career service
    pass


# Career Recommendations Endpoints
@router.post(
    "/recommendations/generate",
    response_model=List[CareerRecommendationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_recommendations(
    session_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Generate AI-powered career recommendations."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")
    
    recommendations = await career_recommendation_service.generate_recommendations(
        db, profile.id, session_id
    )
    return recommendations


@router.get("/recommendations", response_model=List[CareerRecommendationResponse])
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all career recommendations."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")
    
    recommendations = await career_recommendation_service.get_recommendations(
        db, profile.id
    )
    return recommendations


# Career Roadmap Endpoints
@router.post(
    "/roadmaps",
    response_model=CareerRoadmapResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post("/roadmaps", response_model=CareerRoadmapResponse, status_code=status.HTTP_201_CREATED)
async def create_roadmap(
    roadmap_data: CareerRoadmapCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Generate a personalized career development roadmap."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")
    
    roadmap = await career_recommendation_service.generate_roadmap(
        db,
        profile.id,
        roadmap_data.career_goal_id,
        roadmap_data.recommendation_id,
        roadmap_data.title,
        roadmap_data.description,
        roadmap_data.target_duration_weeks,
    )
    return roadmap


@router.get("/roadmaps", response_model=List[CareerRoadmapResponse])
async def get_roadmaps(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Get all career roadmaps."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")
    
    roadmaps = await career_recommendation_service.get_roadmaps(db, profile.id)
    return roadmaps


@router.patch(
    "/roadmaps/milestones/{milestone_id}",
    response_model=RoadmapMilestoneResponse,
)
async def update_milestone_status(
    milestone_id: UUID,
    status_data: UpdateMilestoneStatusRequest,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update milestone status."""
    profile = await student_service.get_profile(db, user_id)
    if not profile:
        raise NotFoundError("Profile not found")
    
    milestone = await career_recommendation_service.update_milestone_status(
        db, milestone_id, profile.id, status_data.status
    )
    return milestone
