"""
Database Models
SQLAlchemy ORM models for all entities
"""

# Import all models here for Alembic to detect them
from app.db.models.user import User
from app.db.models.student import (
    StudentProfile,
    EducationRecord,
    StudentPreferences,
    Skill,
    StudentSkill,
    Project,
    Certification,
)
from app.db.models.career import (
    CareerRole,
    RoleRequirement,
    CareerDiscoverySession,
    CareerDiscoveryResponse,
    CareerGoal,
    CareerRecommendation,
    CareerRoadmap,
    RoadmapMilestone,
)
from app.db.models.resume import (
    Resume,
    ResumeExtraction,
    ResumeVersion,
    ResumeReview,
    ResumeReviewFinding,
)
from app.db.models.job import (
    Company,
    JobListing,
    JobRequirement,
    SavedJob,
    Application,
    ApplicationEvent,
)
from app.db.models.interview import (
    InterviewPlan,
    PreparationTask,
    PracticeSession,
    QuestionAttempt,
)
from app.db.models.intelligence import (
    CareerClassification,
    SkillEvidenceRecord,
    RoadmapTemplate,
    RoadmapTemplatePhase,
    RoadmapTemplateMilestone,
    ResumeSkillExtraction,
    ResumeRoleMatch,
    AIGenerationRecord,
    MLModelMetadata,
)
from app.db.models.launchpad import (
    ProjectMilestone,
    ProjectAssessment,
    ProjectOutcomeAssessment,
    ProjectShowcase,
    Opportunity,
    ProjectOpportunityApplication,
)

__all__ = [
    "User",
    "StudentProfile",
    "EducationRecord",
    "StudentPreferences",
    "Skill",
    "StudentSkill",
    "Project",
    "Certification",
    "CareerRole",
    "RoleRequirement",
    "CareerDiscoverySession",
    "CareerDiscoveryResponse",
    "CareerGoal",
    "CareerRecommendation",
    "CareerRoadmap",
    "RoadmapMilestone",
    "Resume",
    "ResumeExtraction",
    "ResumeVersion",
    "ResumeReview",
    "ResumeReviewFinding",
    "Company",
    "JobListing",
    "JobRequirement",
    "SavedJob",
    "Application",
    "ApplicationEvent",
    "InterviewPlan",
    "PreparationTask",
    "PracticeSession",
    "QuestionAttempt",
    "CareerClassification",
    "SkillEvidenceRecord",
    "RoadmapTemplate",
    "RoadmapTemplatePhase",
    "RoadmapTemplateMilestone",
    "ResumeSkillExtraction",
    "ResumeRoleMatch",
    "AIGenerationRecord",
    "MLModelMetadata",
    "ProjectMilestone",
    "ProjectAssessment",
    "ProjectOutcomeAssessment",
    "ProjectShowcase",
    "Opportunity",
    "ProjectOpportunityApplication",
]
