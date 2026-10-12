"""Quick schema audit - outputs to file"""
from sqlalchemy.orm import class_mapper
from app.db.models.student import EducationRecord, StudentSkill, Project, Certification
from app.db.models.career import CareerGoal, CareerRoadmap
from app.schemas.student import (
    EducationRecordResponse, StudentSkillResponse, 
    ProjectResponse, CertificationResponse
)
from app.schemas.career import CareerGoalResponse, CareerRoadmapResponse

def get_model_columns(model_class):
    mapper = class_mapper(model_class)
    return {col.name for col in mapper.columns}

def get_schema_fields(schema_class):
    if hasattr(schema_class, 'model_fields'):
        return set(schema_class.model_fields.keys())
    return set()

pairs = [
    (EducationRecordResponse, EducationRecord, "EducationRecord"),
    (StudentSkillResponse, StudentSkill, "StudentSkill"),
    (ProjectResponse, Project, "Project"),
    (CertificationResponse, Certification, "Certification"),
    (CareerGoalResponse, CareerGoal, "CareerGoal"),
    (CareerRoadmapResponse, CareerRoadmap, "CareerRoadmap"),
]

with open("schema_audit_results.txt", "w") as f:
    for schema_class, model_class, name in pairs:
        model_fields = get_model_columns(model_class)
        schema_fields = get_schema_fields(schema_class)
        extra = schema_fields - model_fields
        
        f.write(f"\n{'='*70}\n")
        f.write(f"{name}\n")
        f.write(f"{'='*70}\n")
        f.write(f"Model fields: {sorted(model_fields)}\n")
        f.write(f"Schema fields: {sorted(schema_fields)}\n")
        
        if extra:
            f.write(f"\nEXTRA IN SCHEMA (WRONG!):\n")
            for field in sorted(extra):
                f.write(f"  - {field}\n")
        else:
            f.write(f"\nOK - no extra fields\n")

print("Results written to schema_audit_results.txt")
