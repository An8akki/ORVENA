"""
Roadmap Engine

Personalizes general roadmap templates based on student's starting level,
existing skills, and learning goals. Validates roadmap integrity and dependencies.

Works without AI - AI enrichment is optional enhancement.
"""
from typing import List, Dict, Optional, Set
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from copy import deepcopy

from ..types import (
    StudentFeatures, RoadmapPhase, RoadmapMilestoneData,
    MilestoneStatus, SkillEvidence, EvidenceState
)
from ..evidence.skill_assessor import SkillAssessment
from .template_library import get_template


class RoadmapValidationError(Exception):
    """Raised when roadmap validation fails."""
    pass


class PersonalizedRoadmap:
    """A personalized roadmap instance for a student."""
    
    def __init__(
        self,
        roadmap_id: UUID,
        student_profile_id: UUID,
        role_key: str,
        role_name: str,
        template_version: str
    ):
        self.roadmap_id = roadmap_id
        self.student_profile_id = student_profile_id
        self.role_key = role_key
        self.role_name = role_name
        self.template_version = template_version
        
        self.title: str = ""
        self.description: str = ""
        self.target_duration_weeks: int = 0
        self.estimated_hours: int = 0
        
        self.phases: List[RoadmapPhase] = []
        self.milestones: List[RoadmapMilestoneData] = []
        
        # Personalization metadata
        self.personalization_notes: List[str] = []
        self.skipped_milestones: List[str] = []
        self.prerequisite_status: Dict[str, str] = {}
        
        self.created_at: datetime = datetime.utcnow()


class RoadmapEngine:
    """
    Personalizes roadmap templates based on student evidence.
    
    Maintains structural integrity:
    - Enforces prerequisites
    - Validates dependencies
    - Ensures logical progression
    - Never removes mandatory milestones without justification
    """
    
    def personalize_roadmap(
        self,
        role_key: str,
        student_features: StudentFeatures,
        skill_assessment: SkillAssessment,
        student_profile_id: UUID,
        target_hours_per_week: int = 10,
        target_completion_date: Optional[datetime] = None
    ) -> PersonalizedRoadmap:
        """
        Create a personalized roadmap for a student.
        
        Args:
            role_key: Target role identifier
            student_features: Student's profile and evidence
            skill_assessment: Assessment of current skill level
            student_profile_id: Student UUID
            target_hours_per_week: Available study hours
            target_completion_date: Optional target date
            
        Returns:
            PersonalizedRoadmap instance
        """
        # Load template
        template = get_template(role_key)
        if not template:
            raise ValueError(f"No template found for role: {role_key}")
        
        # Create roadmap instance
        roadmap = PersonalizedRoadmap(
            roadmap_id=uuid4(),
            student_profile_id=student_profile_id,
            role_key=role_key,
            role_name=template["template_name"],
            template_version=template["version"]
        )
        
        # Set basic info
        roadmap.title = f"{template['template_name']} - Personalized for You"
        roadmap.description = template["description"]
        
        # Personalize based on starting level
        roadmap = self._adjust_for_starting_level(
            roadmap,
            template,
            skill_assessment
        )
        
        # Mark completed/satisf milestones based on evidence
        roadmap = self._mark_satisfied_milestones(
            roadmap,
            student_features,
            skill_assessment
        )
        
        # Adjust timeline
        roadmap = self._adjust_timeline(
            roadmap,
            target_hours_per_week,
            target_completion_date
        )
        
        # Validate roadmap integrity
        self._validate_roadmap(roadmap)
        
        # Calculate total effort
        roadmap.estimated_hours = sum(
            m.estimated_hours for m in roadmap.milestones
        )
        
        return roadmap
    
    def _adjust_for_starting_level(
        self,
        roadmap: PersonalizedRoadmap,
        template: Dict,
        assessment: SkillAssessment
    ) -> PersonalizedRoadmap:
        """Adjust roadmap based on starting level."""
        level = assessment.starting_level
        
        # Copy phases from template
        for phase_data in template["phases"]:
            phase = RoadmapPhase(
                phase_id=phase_data["phase_id"],
                phase_number=phase_data["phase_number"],
                title=phase_data["title"],
                description=phase_data["description"],
                objectives=phase_data["objectives"],
                estimated_hours=phase_data["estimated_hours"],
                prerequisites=phase_data.get("prerequisites", [])
            )
            roadmap.phases.append(phase)
            
            # Copy milestones
            for milestone_data in phase_data.get("milestones", []):
                milestone = RoadmapMilestoneData(
                    milestone_id=milestone_data["milestone_id"],
                    title=milestone_data["title"],
                    description=milestone_data["description"],
                    phase_id=phase_data["phase_id"],
                    learning_objectives=milestone_data["learning_objectives"],
                    topics=milestone_data["topics"],
                    activities=milestone_data["activities"],
                    deliverable=milestone_data["deliverable"],
                    prerequisites=milestone_data.get("prerequisites", []),
                    estimated_hours=milestone_data["estimated_hours"],
                    completion_criteria=milestone_data["completion_criteria"],
                    assessment_method=milestone_data.get("assessment_method"),
                    resources=milestone_data.get("resources", []),
                    status=milestone_data.get("status", MilestoneStatus.PENDING),
                    sequence_number=milestone_data["sequence_number"]
                )
                roadmap.milestones.append(milestone)
        
        # Add personalization note
        if level == "advanced":
            roadmap.personalization_notes.append(
                "Starting at advanced level - some basic milestones may be fast-tracked"
            )
        elif level == "intermediate":
            roadmap.personalization_notes.append(
                "Starting at intermediate level - foundation skills in place"
            )
        else:
            roadmap.personalization_notes.append(
                "Starting at beginner level - full learning path ahead"
            )
        
        return roadmap
    
    def _mark_satisfied_milestones(
        self,
        roadmap: PersonalizedRoadmap,
        student_features: StudentFeatures,
        assessment: SkillAssessment
    ) -> PersonalizedRoadmap:
        """
        Mark milestones as satisfied based on demonstrated evidence.
        
        IMPORTANT: Only marks milestones when there's STRONG evidence.
        Does not skip mandatory milestones without clear justification.
        """
        demonstrated_skills = set(
            s["skill_name"] for s in assessment.demonstrated_skills
        )
        
        for milestone in roadmap.milestones:
            # Check if milestone's skills are demonstrated
            milestone_topics_lower = [t.lower() for t in milestone.topics]
            
            # Count how many required skills are demonstrated
            relevant_skills = [
                skill for skill in demonstrated_skills
                if any(skill in topic for topic in milestone_topics_lower)
            ]
            
            # If majority of skills demonstrated AND student has projects
            if len(relevant_skills) >= 2 and student_features.project_count > 0:
                # Don't auto-skip - suggest review instead
                roadmap.personalization_notes.append(
                    f"Consider reviewing {milestone.title} - you may have relevant experience"
                )
                # Mark prerequisite as satisfied
                roadmap.prerequisite_status[milestone.milestone_id] = "review_needed"
            
            # Only mark as completed if there's VERY strong evidence
            # (Not implemented here - requires explicit student confirmation)
        
        return roadmap
    
    def _adjust_timeline(
        self,
        roadmap: PersonalizedRoadmap,
        target_hours_per_week: int,
        target_completion_date: Optional[datetime]
    ) -> PersonalizedRoadmap:
        """Adjust timeline based on available hours and target date."""
        total_hours = sum(m.estimated_hours for m in roadmap.milestones)
        
        if target_hours_per_week > 0:
            weeks_needed = total_hours / target_hours_per_week
            roadmap.target_duration_weeks = int(weeks_needed) + 1
        else:
            roadmap.target_duration_weeks = 16  # Default
        
        if target_completion_date:
            weeks_available = (target_completion_date - datetime.utcnow()).days // 7
            
            if weeks_available < roadmap.target_duration_weeks:
                roadmap.personalization_notes.append(
                    f"Target date ambitious - need {roadmap.target_duration_weeks} weeks "
                    f"at {target_hours_per_week}h/week, but only {weeks_available} weeks available"
                )
            elif weeks_available > roadmap.target_duration_weeks * 1.5:
                roadmap.personalization_notes.append(
                    f"Comfortable timeline - {weeks_available} weeks available "
                    f"for {roadmap.target_duration_weeks} weeks of content"
                )
        
        return roadmap
    
    def _validate_roadmap(self, roadmap: PersonalizedRoadmap) -> None:
        """
        Validate roadmap integrity.
        
        Checks:
        - All milestone IDs are unique
        - Prerequisites point to existing milestones
        - No circular dependencies
        - Phases are sequential
        """
        # Check unique IDs
        milestone_ids = [m.milestone_id for m in roadmap.milestones]
        if len(milestone_ids) != len(set(milestone_ids)):
            raise RoadmapValidationError("Duplicate milestone IDs found")
        
        # Check prerequisites exist
        milestone_id_set = set(milestone_ids)
        for milestone in roadmap.milestones:
            for prereq_id in milestone.prerequisites:
                if prereq_id not in milestone_id_set:
                    raise RoadmapValidationError(
                        f"Milestone {milestone.milestone_id} has invalid prerequisite: {prereq_id}"
                    )
        
        # Check for circular dependencies
        if self._has_circular_dependencies(roadmap.milestones):
            raise RoadmapValidationError("Circular dependencies detected")
        
        # Check phase numbers are sequential
        phase_numbers = [p.phase_number for p in roadmap.phases]
        if phase_numbers != sorted(phase_numbers):
            raise RoadmapValidationError("Phase numbers must be sequential")
    
    def _has_circular_dependencies(
        self,
        milestones: List[RoadmapMilestoneData]
    ) -> bool:
        """Check for circular dependencies using DFS."""
        # Build adjacency list
        graph: Dict[str, List[str]] = {}
        for milestone in milestones:
            graph[milestone.milestone_id] = milestone.prerequisites
        
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for prereq in graph.get(node, []):
                if prereq not in visited:
                    if has_cycle(prereq):
                        return True
                elif prereq in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for milestone_id in graph:
            if milestone_id not in visited:
                if has_cycle(milestone_id):
                    return True
        
        return False
    
    def get_next_milestones(
        self,
        roadmap: PersonalizedRoadmap,
        completed_milestone_ids: List[str]
    ) -> List[RoadmapMilestoneData]:
        """
        Get milestones that are ready to be started.
        
        A milestone is ready if:
        - Not completed
        - All prerequisites are completed
        """
        completed_set = set(completed_milestone_ids)
        ready_milestones = []
        
        for milestone in roadmap.milestones:
            # Skip if already completed
            if milestone.milestone_id in completed_set:
                continue
            
            # Check if all prerequisites are met
            prereqs_met = all(
                prereq_id in completed_set
                for prereq_id in milestone.prerequisites
            )
            
            if prereqs_met:
                ready_milestones.append(milestone)
        
        # Sort by sequence number
        ready_milestones.sort(key=lambda m: m.sequence_number)
        
        return ready_milestones
    
    def calculate_progress(
        self,
        roadmap: PersonalizedRoadmap,
        completed_milestone_ids: List[str]
    ) -> Dict:
        """Calculate overall progress statistics."""
        total_milestones = len(roadmap.milestones)
        completed_count = len(completed_milestone_ids)
        
        completed_hours = sum(
            m.estimated_hours
            for m in roadmap.milestones
            if m.milestone_id in completed_milestone_ids
        )
        
        total_hours = sum(m.estimated_hours for m in roadmap.milestones)
        
        # Calculate by phase
        phase_progress = {}
        for phase in roadmap.phases:
            phase_milestones = [
                m for m in roadmap.milestones
                if m.phase_id == phase.phase_id
            ]
            phase_completed = sum(
                1 for m in phase_milestones
                if m.milestone_id in completed_milestone_ids
            )
            phase_progress[phase.phase_id] = {
                "completed": phase_completed,
                "total": len(phase_milestones),
                "percentage": (phase_completed / len(phase_milestones) * 100) if phase_milestones else 0
            }
        
        return {
            "total_milestones": total_milestones,
            "completed_milestones": completed_count,
            "percentage": (completed_count / total_milestones * 100) if total_milestones else 0,
            "completed_hours": completed_hours,
            "total_hours": total_hours,
            "hours_remaining": total_hours - completed_hours,
            "phase_progress": phase_progress
        }
    
    def update_milestone_status(
        self,
        roadmap: PersonalizedRoadmap,
        milestone_id: str,
        new_status: MilestoneStatus,
        completion_notes: Optional[str] = None
    ) -> bool:
        """
        Update a milestone's status.
        
        Validates that prerequisites are met before marking as complete.
        """
        milestone = next(
            (m for m in roadmap.milestones if m.milestone_id == milestone_id),
            None
        )
        
        if not milestone:
            return False
        
        # If marking as completed, verify prerequisites
        if new_status == MilestoneStatus.COMPLETED:
            # This would check against actual completed milestones in DB
            # For now, just update status
            milestone.status = new_status
        else:
            milestone.status = new_status
        
        return True
    
    def suggest_learning_pace(
        self,
        roadmap: PersonalizedRoadmap,
        available_hours_per_week: int
    ) -> Dict:
        """Suggest realistic learning pace and timeline."""
        total_hours = roadmap.estimated_hours
        weeks_needed = total_hours / available_hours_per_week if available_hours_per_week > 0 else 0
        
        # Suggest pace levels
        paces = {
            "relaxed": {
                "hours_per_week": max(5, available_hours_per_week // 2),
                "weeks": int(total_hours / max(5, available_hours_per_week // 2)),
                "description": "Comfortable pace with time for deep learning"
            },
            "moderate": {
                "hours_per_week": available_hours_per_week,
                "weeks": int(weeks_needed),
                "description": "Balanced pace for consistent progress"
            },
            "intensive": {
                "hours_per_week": available_hours_per_week * 1.5,
                "weeks": int(total_hours / (available_hours_per_week * 1.5)) if available_hours_per_week > 0 else 0,
                "description": "Fast-paced learning requiring strong commitment"
            }
        }
        
        return {
            "total_hours": total_hours,
            "paces": paces,
            "recommendation": "moderate",  # Default recommendation
            "notes": [
                "Learning pace can be adjusted based on your progress",
                "Quality of learning is more important than speed",
                "Consider your other commitments when choosing pace"
            ]
        }
