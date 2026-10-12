"""add intelligence tables

Revision ID: 20261012_1633_intelligence
Revises: previous migration
Create Date: 2026-10-12 16:33:00.000000

Adds tables for the ORVENA Intelligence Engine:
- Career classifications
- Skill evidence records
- Roadmap templates (phases and milestones)
- Resume skill extractions
- Resume role matches
- AI generation records
- ML model metadata
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261012_1633_intelligence'
down_revision = None  # Update this to point to the latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    
    # Career Classifications
    op.create_table(
        'career_classifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('classifier_type', sa.String(50), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('confidence_level', sa.String(20), nullable=False),
        sa.Column('candidate_roles', postgresql.JSONB, nullable=False),
        sa.Column('missing_information', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('summary', sa.Text, nullable=False),
        sa.Column('input_features', postgresql.JSONB, nullable=True),
        sa.Column('student_feedback', sa.String(50), nullable=True),
        sa.Column('selected_role_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['student_profile_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['career_discovery_sessions.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_career_classifications_student_profile_id', 'career_classifications', ['student_profile_id'])
    op.create_index('ix_career_classifications_session_id', 'career_classifications', ['session_id'])
    
    # Skill Evidence Records
    op.create_table(
        'skill_evidence_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('skill_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evidence_type', sa.String(50), nullable=False),
        sa.Column('evidence_state', sa.String(50), nullable=False),
        sa.Column('proficiency_level', sa.String(20), nullable=True),
        sa.Column('source_description', sa.Text, nullable=False),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=False, server_default='0.5'),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('certification_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_verified', sa.Boolean, default=False, nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['student_profile_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['certification_id'], ['certifications.id'], ondelete='CASCADE'),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_score'),
    )
    op.create_index('ix_skill_evidence_records_student_profile_id', 'skill_evidence_records', ['student_profile_id'])
    op.create_index('ix_skill_evidence_records_skill_id', 'skill_evidence_records', ['skill_id'])
    op.create_index('ix_skill_evidence_records_evidence_type', 'skill_evidence_records', ['evidence_type'])
    op.create_index('ix_skill_evidence_records_evidence_state', 'skill_evidence_records', ['evidence_state'])
    
    # Roadmap Templates
    op.create_table(
        'roadmap_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('career_role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_name', sa.String(255), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('starting_level', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('prerequisites', postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column('estimated_duration_weeks', sa.Integer, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_published', sa.Boolean, default=False, nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('last_reviewed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['career_role_id'], ['career_roles.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('career_role_id', 'version', name='unique_template_version'),
    )
    op.create_index('ix_roadmap_templates_career_role_id', 'roadmap_templates', ['career_role_id'])
    
    # Roadmap Template Phases
    op.create_table(
        'roadmap_template_phases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phase_number', sa.Integer, nullable=False),
        sa.Column('phase_id', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('objectives', postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column('estimated_hours', sa.Integer, nullable=False),
        sa.Column('prerequisites', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['roadmap_templates.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('template_id', 'phase_number', name='unique_phase_number'),
        sa.UniqueConstraint('template_id', 'phase_id', name='unique_phase_id'),
    )
    op.create_index('ix_roadmap_template_phases_template_id', 'roadmap_template_phases', ['template_id'])
    
    # Roadmap Template Milestones
    op.create_table(
        'roadmap_template_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('phase_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('milestone_id', sa.String(100), nullable=False),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('learning_objectives', postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column('topics', postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column('activities', postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column('deliverable', sa.Text, nullable=False),
        sa.Column('prerequisites', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('estimated_hours', sa.Integer, nullable=False),
        sa.Column('completion_criteria', postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column('assessment_method', sa.String(100), nullable=True),
        sa.Column('resources', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['phase_id'], ['roadmap_template_phases.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('phase_id', 'sequence_number', name='unique_milestone_sequence'),
        sa.UniqueConstraint('phase_id', 'milestone_id', name='unique_milestone_id'),
    )
    op.create_index('ix_roadmap_template_milestones_phase_id', 'roadmap_template_milestones', ['phase_id'])
    
    # Resume Skill Extractions
    op.create_table(
        'resume_skill_extractions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('raw_skill_text', sa.String(255), nullable=False),
        sa.Column('canonical_skill_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('canonical_skill_name', sa.String(100), nullable=True),
        sa.Column('skill_category', sa.String(50), nullable=True),
        sa.Column('context', sa.Text, nullable=True),
        sa.Column('normalization_method', sa.String(50), nullable=False),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=False, server_default='1.0'),
        sa.Column('is_confirmed', sa.Boolean, default=False, nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['canonical_skill_id'], ['skills.id'], ondelete='SET NULL'),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_skill_confidence'),
    )
    op.create_index('ix_resume_skill_extractions_resume_id', 'resume_skill_extractions', ['resume_id'])
    op.create_index('ix_resume_skill_extractions_canonical_skill_id', 'resume_skill_extractions', ['canonical_skill_id'])
    
    # Resume Role Matches
    op.create_table(
        'resume_role_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('career_role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_score', sa.Numeric(3, 2), nullable=False),
        sa.Column('confidence_level', sa.String(20), nullable=False),
        sa.Column('match_rank', sa.Integer, nullable=True),
        sa.Column('matching_skills', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('missing_skills', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('partial_skills', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('reasoning', sa.Text, nullable=False),
        sa.Column('strengths', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('gaps', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('next_steps', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('matcher_version', sa.String(50), nullable=True),
        sa.Column('student_feedback', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['career_role_id'], ['career_roles.id'], ondelete='CASCADE'),
        sa.CheckConstraint('match_score >= 0 AND match_score <= 1', name='check_match_score'),
        sa.UniqueConstraint('resume_id', 'career_role_id', name='unique_resume_role_match'),
    )
    op.create_index('ix_resume_role_matches_resume_id', 'resume_role_matches', ['resume_id'])
    op.create_index('ix_resume_role_matches_career_role_id', 'resume_role_matches', ['career_role_id'])
    
    # AI Generation Records
    op.create_table(
        'ai_generation_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('generation_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('llm_provider', sa.String(50), nullable=False),
        sa.Column('llm_model', sa.String(100), nullable=False),
        sa.Column('prompt_version', sa.String(20), nullable=False),
        sa.Column('input_data', postgresql.JSONB, nullable=True),
        sa.Column('output_data', postgresql.JSONB, nullable=True),
        sa.Column('tokens_used', sa.Integer, nullable=True),
        sa.Column('generation_time_ms', sa.Integer, nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('validation_passed', sa.Boolean, nullable=True),
        sa.Column('validation_notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_ai_generation_records_generation_type', 'ai_generation_records', ['generation_type'])
    op.create_index('ix_ai_generation_records_entity_id', 'ai_generation_records', ['entity_id'])
    
    # ML Model Metadata
    op.create_table(
        'ml_model_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_name', sa.String(100), unique=True, nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('algorithm', sa.String(100), nullable=False),
        sa.Column('framework', sa.String(50), nullable=True),
        sa.Column('artifact_path', sa.String(500), nullable=True),
        sa.Column('preprocessing_pipeline_path', sa.String(500), nullable=True),
        sa.Column('trained_on_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('training_dataset_size', sa.Integer, nullable=True),
        sa.Column('metrics', postgresql.JSONB, nullable=True),
        sa.Column('is_active', sa.Boolean, default=False, nullable=False),
        sa.Column('is_production', sa.Boolean, default=False, nullable=False),
        sa.Column('hyperparameters', postgresql.JSONB, nullable=True),
        sa.Column('feature_schema', postgresql.JSONB, nullable=True),
        sa.Column('validation_results', postgresql.JSONB, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_ml_model_metadata_model_name', 'ml_model_metadata', ['model_name'])


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_table('ml_model_metadata')
    op.drop_table('ai_generation_records')
    op.drop_table('resume_role_matches')
    op.drop_table('resume_skill_extractions')
    op.drop_table('roadmap_template_milestones')
    op.drop_table('roadmap_template_phases')
    op.drop_table('roadmap_templates')
    op.drop_table('skill_evidence_records')
    op.drop_table('career_classifications')
