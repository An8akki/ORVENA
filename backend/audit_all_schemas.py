"""
Systematic audit of all Pydantic schemas vs SQLAlchemy models
Identifies field mismatches to prevent serialization errors
"""
import inspect
from typing import get_type_hints, get_origin, get_args
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import class_mapper
from sqlalchemy import inspect as sa_inspect

# Import all models
from app.db.models.user import User
from app.db.models.student import (
    StudentProfile, EducationRecord,
    StudentSkill, Project, Certification
)
from app.db.models.career import (
    CareerDiscoverySession,
    CareerDiscoveryResponse, CareerGoal,
    CareerRoadmap, RoadmapMilestone
)

# Import all response schemas
from app.schemas.student import (
    StudentProfileResponse, EducationRecordResponse,
    StudentSkillResponse, ProjectResponse, CertificationResponse
)
from app.schemas.career import (
    CareerDiscoverySessionResponse, CareerDiscoveryResponseResponse,
    CareerGoalResponse,
    CareerRoadmapResponse, RoadmapMilestoneResponse
)


def get_model_columns(model_class):
    """Get all column names from a SQLAlchemy model"""
    mapper = class_mapper(model_class)
    columns = set()
    
    # Add column attributes
    for column in mapper.columns:
        columns.add(column.name)
    
    # Add relationship attributes
    for rel in mapper.relationships:
        columns.add(rel.key)
    
    return columns


def get_schema_fields(schema_class):
    """Get all field names from a Pydantic schema"""
    if hasattr(schema_class, 'model_fields'):
        return set(schema_class.model_fields.keys())
    return set()


def audit_schema_model_pair(schema_class, model_class, schema_name, model_name):
    """Audit a single schema-model pair"""
    print(f"\n{'='*70}")
    print(f"Auditing: {schema_name} vs {model_name}")
    print(f"{'='*70}")
    
    model_fields = get_model_columns(model_class)
    schema_fields = get_schema_fields(schema_class)
    
    print(f"\nModel fields ({len(model_fields)}): {sorted(model_fields)}")
    print(f"Schema fields ({len(schema_fields)}): {sorted(schema_fields)}")
    
    # Fields in schema but not in model
    extra_in_schema = schema_fields - model_fields
    if extra_in_schema:
        print(f"\n⚠️  Fields in SCHEMA but NOT in MODEL:")
        for field in sorted(extra_in_schema):
            print(f"   - {field}")
    
    # Fields in model but not in schema (could be OK if optional/relationship)
    missing_in_schema = model_fields - schema_fields
    if missing_in_schema:
        print(f"\nℹ️  Fields in MODEL but NOT in SCHEMA (may be OK):")
        for field in sorted(missing_in_schema):
            print(f"   - {field}")
    
    # Check if schema uses from_attributes
    if hasattr(schema_class, 'model_config'):
        config = schema_class.model_config
        uses_from_attributes = config.get('from_attributes', False)
        print(f"\nUses from_attributes: {uses_from_attributes}")
        
        if uses_from_attributes and extra_in_schema:
            print(f"\n❌ CRITICAL: Schema has extra fields with from_attributes=True!")
            print(f"   This will cause serialization errors!")
    
    if not extra_in_schema and not missing_in_schema:
        print(f"\n✅ Perfect match!")
    elif not extra_in_schema:
        print(f"\n✅ No critical issues (schema subset of model)")
    
    return len(extra_in_schema) == 0


def main():
    """Run complete schema audit"""
    print("\n" + "="*70)
    print("ORVENA SCHEMA-MODEL AUDIT")
    print("="*70)
    
    audits = [
        # Student schemas
        (StudentProfileResponse, StudentProfile, "StudentProfileResponse", "StudentProfile"),
        (EducationRecordResponse, EducationRecord, "EducationRecordResponse", "EducationRecord"),
        (StudentSkillResponse, StudentSkill, "StudentSkillResponse", "StudentSkill"),
        (ProjectResponse, Project, "ProjectResponse", "Project"),
        (CertificationResponse, Certification, "CertificationResponse", "Certification"),
        
        # Career schemas
        (CareerDiscoverySessionResponse, CareerDiscoverySession, "CareerDiscoverySessionResponse", "CareerDiscoverySession"),
        (CareerDiscoveryResponseResponse, CareerDiscoveryResponse, "CareerDiscoveryResponseResponse", "CareerDiscoveryResponse"),
        (CareerGoalResponse, CareerGoal, "CareerGoalResponse", "CareerGoal"),
        (CareerRoadmapResponse, CareerRoadmap, "CareerRoadmapResponse", "CareerRoadmap"),
        (RoadmapMilestoneResponse, RoadmapMilestone, "RoadmapMilestoneResponse", "RoadmapMilestone"),
    ]
    
    passed = 0
    failed = 0
    
    for schema_class, model_class, schema_name, model_name in audits:
        try:
            result = audit_schema_model_pair(schema_class, model_class, schema_name, model_name)
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ ERROR auditing {schema_name}: {e}")
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"AUDIT SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
