"""add launchpad and guide tables

Revision ID: 20261022_launchpad_guide
Revises: 20261012_1633_intelligence
Create Date: 2026-10-22 19:10:00.000000

Adds tables and columns for Orvena Project Launchpad & Guide:
- Extended project attributes (problem, solution, stage, domain, difficulty, completion %, plan_data, origin)
- Project milestones (project_milestones)
- 5-dimension project evaluations (project_assessments)
- Outcome intelligence evaluations (project_outcome_assessments)
- Project showcase portfolio (project_showcases)
- Curated opportunities directory (opportunities)
- Tracked opportunity applications (project_opportunity_applications)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261022_launchpad_guide'
down_revision = 'b4e3c530c27d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add extended columns to projects table
    op.add_column('projects', sa.Column('problem_statement', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('target_users', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('proposed_solution', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('domain', sa.String(length=100), nullable=True))
    op.add_column('projects', sa.Column('difficulty_level', sa.String(length=50), server_default='intermediate', nullable=True))
    op.add_column('projects', sa.Column('primary_goal', sa.String(length=50), server_default='portfolio', nullable=True))
    op.add_column('projects', sa.Column('stage', sa.String(length=50), server_default='idea', nullable=True))
    op.add_column('projects', sa.Column('status', sa.String(length=50), server_default='in_progress', nullable=True))
    op.add_column('projects', sa.Column('blocker_description', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('weekly_hours', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('estimated_duration_weeks', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('completion_percentage', sa.Integer(), server_default='0', nullable=False))
    op.add_column('projects', sa.Column('plan_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('projects', sa.Column('origin', sa.String(length=50), server_default='scratch', nullable=True))
    op.add_column('projects', sa.Column('catalogue_idea_id', sa.String(length=100), nullable=True))

    # 2. Project Milestones
    op.create_table(
        'project_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('phase', sa.String(length=50), nullable=False, server_default='Implementation'),
        sa.Column('sequence_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='not_started'),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deliverables', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('resources', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('blocker_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_project_milestones_project_id', 'project_milestones', ['project_id'])
    op.create_index('ix_project_milestones_status', 'project_milestones', ['status'])

    # 3. Project Assessments (5-Dimension Evaluation)
    op.create_table(
        'project_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_score', sa.Numeric(precision=4, scale=1), nullable=False),
        sa.Column('overall_rating', sa.String(length=50), nullable=False),
        sa.Column('dimension_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('strengths', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('missing_evidence', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('improvement_priorities', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('recommended_milestone', sa.Text(), nullable=True),
        sa.Column('reassessment_conditions', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('raw_answers', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_project_assessments_project_id', 'project_assessments', ['project_id'])
    op.create_index('ix_project_assessments_student_profile_id', 'project_assessments', ['student_profile_id'])

    # 4. Project Outcome Assessments (6 Strategic Pathways)
    op.create_table(
        'project_outcome_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('selected_goal', sa.String(length=100), nullable=True),
        sa.Column('top_pathway', sa.String(length=50), nullable=False),
        sa.Column('pathways', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('readiness_summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_project_outcome_assessments_project_id', 'project_outcome_assessments', ['project_id'])
    op.create_index('ix_project_outcome_assessments_student_profile_id', 'project_outcome_assessments', ['student_profile_id'])

    # 5. Project Showcases
    op.create_table(
        'project_showcases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('student_profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False, unique=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('headline', sa.String(length=255), nullable=True),
        sa.Column('problem_solution_summary', sa.Text(), nullable=True),
        sa.Column('key_contributions', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('outcomes_metrics', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('media_urls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('skills_highlighted', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_project_showcases_slug', 'project_showcases', ['slug'])
    op.create_index('ix_project_showcases_student_profile_id', 'project_showcases', ['student_profile_id'])

    # 6. Opportunities
    op.create_table(
        'opportunities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=255), nullable=False),
        sa.Column('opportunity_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('official_url', sa.String(length=500), nullable=False),
        sa.Column('eligibility_requirements', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('beneficiary_type', sa.String(length=100), server_default='individual_student', nullable=False),
        sa.Column('geographic_scope', sa.String(length=100), server_default='Global', nullable=False),
        sa.Column('domains', sa.ARRAY(sa.Text()), nullable=True),
        sa.Column('required_project_stage', sa.String(length=50), server_default='any', nullable=False),
        sa.Column('funding_amount_or_benefits', sa.String(length=255), nullable=True),
        sa.Column('is_monetary', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('application_deadline', sa.Date(), nullable=True),
        sa.Column('is_rolling', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('application_instructions', sa.Text(), nullable=True),
        sa.Column('date_last_verified', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='active', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('source_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_opportunities_opportunity_type', 'opportunities', ['opportunity_type'])
    op.create_index('ix_opportunities_status', 'opportunities', ['status'])
    op.create_index('ix_opportunities_title', 'opportunities', ['title'])

    # 7. Project Opportunity Applications
    op.create_table(
        'project_opportunity_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('student_profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='saved', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('submission_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('student_profile_id', 'opportunity_id', 'project_id', name='unique_student_opportunity_project')
    )
    op.create_index('ix_project_opportunity_applications_student_profile_id', 'project_opportunity_applications', ['student_profile_id'])
    op.create_index('ix_project_opportunity_applications_status', 'project_opportunity_applications', ['status'])


def downgrade() -> None:
    op.drop_table('project_opportunity_applications')
    op.drop_table('opportunities')
    op.drop_table('project_showcases')
    op.drop_table('project_outcome_assessments')
    op.drop_table('project_assessments')
    op.drop_table('project_milestones')

    op.drop_column('projects', 'catalogue_idea_id')
    op.drop_column('projects', 'origin')
    op.drop_column('projects', 'plan_data')
    op.drop_column('projects', 'completion_percentage')
    op.drop_column('projects', 'estimated_duration_weeks')
    op.drop_column('projects', 'weekly_hours')
    op.drop_column('projects', 'blocker_description')
    op.drop_column('projects', 'status')
    op.drop_column('projects', 'stage')
    op.drop_column('projects', 'primary_goal')
    op.drop_column('projects', 'difficulty_level')
    op.drop_column('projects', 'domain')
    op.drop_column('projects', 'proposed_solution')
    op.drop_column('projects', 'target_users')
    op.drop_column('projects', 'problem_statement')
