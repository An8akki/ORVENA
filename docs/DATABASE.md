# ORVENA Database Design

## Overview

ORVENA uses PostgreSQL as its primary relational database, hosted on Supabase. The schema is designed for:
- Clear ownership and access control
- Normalized data with appropriate relationships
- Evidence-based career and skill tracking
- Audit trail for AI-generated content
- Version control for resumes

## Database Principles

1. **UUID Primary Keys**: All tables use UUID for primary keys
2. **Timestamps**: `created_at` and `updated_at` on all tables
3. **Soft Deletes**: `deleted_at` for important entities
4. **Ownership**: Every student-owned record links to `user_id`
5. **Indexes**: On foreign keys, status fields, and frequently queried columns
6. **Constraints**: Foreign keys, unique constraints, check constraints
7. **Migrations**: All schema changes via Alembic migrations

## Entity Relationship Diagram

```
users (Supabase Auth)
  ↓
student_profiles ←→ education_records
  ↓                    ↓
  ├─→ skills ←─── student_skills
  ├─→ projects
  ├─→ certifications
  ├─→ student_preferences
  ↓
career_goals ←→ career_discovery_sessions
  ↓                ↓
  ↓         career_discovery_responses
  ↓
career_recommendations
  ↓
career_roadmaps → roadmap_milestones
  ↓
resumes → resume_versions
  ↓
saved_jobs ← job_listings → job_requirements
  ↓
applications → application_events
  ↓
interview_plans → preparation_tasks
  ↓
practice_sessions → question_attempts
```

## Core Tables

### Identity and Profile

#### `student_profiles`
Student profile information and preferences.

```sql
CREATE TABLE student_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(255),
    bio TEXT,
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    graduation_year INTEGER,
    current_status VARCHAR(50), -- 'student', 'graduate', 'employed'
    availability_date DATE,
    preferred_locations TEXT[], -- Array of location preferences
    remote_preference VARCHAR(20), -- 'remote', 'hybrid', 'onsite', 'flexible'
    work_authorization VARCHAR(100),
    expected_salary_min INTEGER,
    expected_salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_student_profiles_user_id ON student_profiles(user_id);
CREATE INDEX idx_student_profiles_graduation_year ON student_profiles(graduation_year);
```

#### `education_records`
Educational background and academic history.

```sql
CREATE TABLE education_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    institution_name VARCHAR(255) NOT NULL,
    degree VARCHAR(100) NOT NULL, -- 'Bachelor', 'Master', 'PhD'
    field_of_study VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    gpa DECIMAL(3, 2),
    gpa_scale DECIMAL(3, 2),
    achievements TEXT[],
    relevant_coursework TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_education_records_student ON education_records(student_profile_id);
```

#### `student_preferences`
Career and job search preferences.

```sql
CREATE TABLE student_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    preferred_industries TEXT[],
    preferred_company_sizes TEXT[], -- 'startup', 'midsize', 'enterprise'
    work_environment_preferences TEXT[],
    values TEXT[], -- 'innovation', 'work-life-balance', 'growth'
    avoid_industries TEXT[],
    willing_to_relocate BOOLEAN DEFAULT false,
    maximum_commute_minutes INTEGER,
    requires_sponsorship BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_student_preferences UNIQUE(student_profile_id)
);
```

### Skills and Evidence

#### `skills`
Master skill catalog.

```sql
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL, -- 'technical', 'soft', 'domain'
    subcategory VARCHAR(100),
    description TEXT,
    aliases TEXT[], -- Alternative names
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_name ON skills(name);
```

#### `student_skills`
Student skill proficiency with evidence.

```sql
CREATE TABLE student_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level VARCHAR(20) NOT NULL, -- 'beginner', 'intermediate', 'advanced', 'expert'
    years_of_experience DECIMAL(3, 1),
    evidence_type VARCHAR(50), -- 'project', 'work', 'certification', 'course', 'self-assessed'
    evidence_description TEXT,
    last_used_date DATE,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_student_skill UNIQUE(student_profile_id, skill_id)
);

CREATE INDEX idx_student_skills_student ON student_skills(student_profile_id);
CREATE INDEX idx_student_skills_skill ON student_skills(skill_id);
CREATE INDEX idx_student_skills_proficiency ON student_skills(proficiency_level);
```

#### `projects`
Student projects with detailed information.

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    role VARCHAR(100),
    technologies TEXT[] NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT false,
    github_url VARCHAR(500),
    demo_url VARCHAR(500),
    achievements TEXT[],
    team_size INTEGER,
    impact_metrics TEXT[], -- Quantifiable results
    visibility VARCHAR(20) DEFAULT 'public', -- 'public', 'private'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_projects_student ON projects(student_profile_id);
```

#### `certifications`
Professional certifications and courses.

```sql
CREATE TABLE certifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255) NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE,
    credential_id VARCHAR(255),
    credential_url VARCHAR(500),
    skills_covered TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_certifications_student ON certifications(student_profile_id);
```

### Career Intelligence

#### `career_roles`
Master career role definitions.

```sql
CREATE TABLE career_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    typical_responsibilities TEXT[],
    entry_requirements TEXT[],
    typical_salary_min INTEGER,
    typical_salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    growth_outlook TEXT,
    work_environment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_career_roles_category ON career_roles(category);
```

#### `role_requirements`
Skills and qualifications required for roles.

```sql
CREATE TABLE role_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    career_role_id UUID NOT NULL REFERENCES career_roles(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    requirement_type VARCHAR(50) NOT NULL, -- 'skill', 'education', 'experience', 'certification'
    requirement_text TEXT NOT NULL,
    importance VARCHAR(20) NOT NULL, -- 'required', 'preferred', 'optional'
    min_proficiency VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_role_requirements_role ON role_requirements(career_role_id);
CREATE INDEX idx_role_requirements_skill ON role_requirements(skill_id);
```

#### `career_discovery_sessions`
Career discovery conversation sessions.

```sql
CREATE TABLE career_discovery_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL, -- 'discovery', 'targeted'
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed', 'abandoned'
    current_phase VARCHAR(50),
    completed_phases TEXT[],
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_discovery_sessions_student ON career_discovery_sessions(student_profile_id);
CREATE INDEX idx_discovery_sessions_status ON career_discovery_sessions(status);
```

#### `career_discovery_responses`
Student responses during discovery.

```sql
CREATE TABLE career_discovery_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES career_discovery_sessions(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    question_category VARCHAR(100),
    phase VARCHAR(50),
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_discovery_responses_session ON career_discovery_responses(session_id);
CREATE INDEX idx_discovery_responses_sequence ON career_discovery_responses(session_id, sequence_number);
```

#### `career_goals`
Student career goals and targets.

```sql
CREATE TABLE career_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    career_role_id UUID REFERENCES career_roles(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_timeline VARCHAR(50), -- 'immediate', '3-6-months', '6-12-months', '1-2-years'
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'achieved', 'modified', 'abandoned'
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_career_goals_student ON career_goals(student_profile_id);
CREATE INDEX idx_career_goals_status ON career_goals(status);
```

#### `career_recommendations`
AI-generated career recommendations.

```sql
CREATE TABLE career_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    session_id UUID REFERENCES career_discovery_sessions(id) ON DELETE SET NULL,
    career_role_id UUID NOT NULL REFERENCES career_roles(id) ON DELETE CASCADE,
    fit_score DECIMAL(3, 2), -- 0.00 to 1.00
    reasoning TEXT NOT NULL,
    strengths TEXT[],
    gaps TEXT[],
    opportunities TEXT[],
    threats TEXT[],
    recommendation_rank INTEGER,
    student_feedback VARCHAR(20), -- 'interested', 'maybe', 'not-interested'
    student_notes TEXT,
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    prompt_version VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_career_recommendations_student ON career_recommendations(student_profile_id);
CREATE INDEX idx_career_recommendations_role ON career_recommendations(career_role_id);
CREATE INDEX idx_career_recommendations_feedback ON career_recommendations(student_feedback);
```

#### `career_roadmaps`
Development roadmaps for career goals.

```sql
CREATE TABLE career_roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    career_goal_id UUID NOT NULL REFERENCES career_goals(id) ON DELETE CASCADE,
    recommendation_id UUID REFERENCES career_recommendations(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_duration_weeks INTEGER,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'paused', 'archived'
    progress_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_roadmaps_student ON career_roadmaps(student_profile_id);
CREATE INDEX idx_roadmaps_goal ON career_roadmaps(career_goal_id);
CREATE INDEX idx_roadmaps_status ON career_roadmaps(status);
```

#### `roadmap_milestones`
Specific milestones and tasks in roadmaps.

```sql
CREATE TABLE roadmap_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id UUID NOT NULL REFERENCES career_roadmaps(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 'skill', 'project', 'certification', 'networking', 'knowledge'
    estimated_hours INTEGER,
    sequence_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'skipped'
    completed_at TIMESTAMP WITH TIME ZONE,
    resources TEXT[], -- Links, books, courses
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_roadmap_milestones_roadmap ON roadmap_milestones(roadmap_id);
CREATE INDEX idx_roadmap_milestones_status ON roadmap_milestones(status);
CREATE INDEX idx_roadmap_milestones_sequence ON roadmap_milestones(roadmap_id, sequence_number);
```

### Resume Intelligence

#### `resumes`
Resume documents and metadata.

```sql
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    source_type VARCHAR(20) NOT NULL, -- 'uploaded', 'built'
    original_filename VARCHAR(255),
    storage_path VARCHAR(500),
    file_size_bytes INTEGER,
    content_type VARCHAR(100),
    status VARCHAR(20) DEFAULT 'processing', -- 'processing', 'ready', 'failed'
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_resumes_student ON resumes(student_profile_id);
CREATE INDEX idx_resumes_status ON resumes(status);
CREATE INDEX idx_resumes_primary ON resumes(student_profile_id, is_primary) WHERE is_primary = true;
```

#### `resume_extractions`
Extracted structured data from resumes.

```sql
CREATE TABLE resume_extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL UNIQUE REFERENCES resumes(id) ON DELETE CASCADE,
    raw_text TEXT,
    contact_info JSONB,
    education JSONB,
    experience JSONB,
    projects JSONB,
    skills JSONB,
    certifications JSONB,
    achievements JSONB,
    is_confirmed BOOLEAN DEFAULT false,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    extraction_method VARCHAR(50), -- 'ai', 'manual'
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_resume_extractions_resume ON resume_extractions(resume_id);
```

#### `resume_versions`
Version history for resumes.

```sql
CREATE TABLE resume_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    file_format VARCHAR(10) NOT NULL, -- 'pdf', 'docx'
    changes_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_resume_version UNIQUE(resume_id, version_number)
);

CREATE INDEX idx_resume_versions_resume ON resume_versions(resume_id);
```

#### `resume_reviews`
AI-generated resume reviews and feedback.

```sql
CREATE TABLE resume_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    review_type VARCHAR(50) NOT NULL, -- 'general', 'job-tailored'
    target_job_id UUID REFERENCES job_listings(id) ON DELETE SET NULL,
    overall_score DECIMAL(3, 2),
    overall_feedback TEXT NOT NULL,
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    prompt_version VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_resume_reviews_resume ON resume_reviews(resume_id);
CREATE INDEX idx_resume_reviews_type ON resume_reviews(review_type);
```

#### `resume_review_findings`
Specific findings and suggestions from reviews.

```sql
CREATE TABLE resume_review_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES resume_reviews(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL, -- 'content', 'format', 'grammar', 'keywords', 'achievements'
    severity VARCHAR(20) NOT NULL, -- 'critical', 'major', 'minor', 'suggestion'
    section VARCHAR(100), -- Which resume section
    current_text TEXT,
    suggested_improvement TEXT NOT NULL,
    reasoning TEXT,
    sequence_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_review_findings_review ON resume_review_findings(review_id);
CREATE INDEX idx_review_findings_severity ON resume_review_findings(severity);
```

### Job and Opportunity Intelligence

#### `companies`
Company information database.

```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    website VARCHAR(500),
    description TEXT,
    industry VARCHAR(100),
    company_size VARCHAR(50), -- 'startup', '1-50', '51-200', '201-1000', '1000+'
    headquarters VARCHAR(255),
    founded_year INTEGER,
    logo_url VARCHAR(500),
    culture_tags TEXT[],
    tech_stack TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_industry ON companies(industry);
```

#### `job_listings`
Job postings and opportunities.

```sql
CREATE TABLE job_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    company_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    role_type VARCHAR(100), -- Maps to career_roles
    employment_type VARCHAR(50), -- 'full-time', 'part-time', 'contract', 'internship'
    experience_level VARCHAR(50), -- 'entry', 'mid', 'senior'
    location VARCHAR(255),
    is_remote BOOLEAN DEFAULT false,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    application_url VARCHAR(500),
    source VARCHAR(100) NOT NULL, -- 'manual', 'rapidapi', 'linkedin', 'company-website'
    source_id VARCHAR(255), -- External ID from source
    posted_date DATE,
    expires_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'expired', 'filled', 'removed'
    last_verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_job_listings_company ON job_listings(company_id);
CREATE INDEX idx_job_listings_status ON job_listings(status);
CREATE INDEX idx_job_listings_role_type ON job_listings(role_type);
CREATE INDEX idx_job_listings_posted_date ON job_listings(posted_date DESC);
CREATE INDEX idx_job_listings_source ON job_listings(source, source_id);
```

#### `job_requirements`
Extracted requirements from job listings.

```sql
CREATE TABLE job_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_listing_id UUID NOT NULL REFERENCES job_listings(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    requirement_text TEXT NOT NULL,
    requirement_type VARCHAR(50), -- 'skill', 'education', 'experience', 'certification'
    importance VARCHAR(20), -- 'required', 'preferred', 'nice-to-have'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_job_requirements_listing ON job_requirements(job_listing_id);
CREATE INDEX idx_job_requirements_skill ON job_requirements(skill_id);
```

#### `saved_jobs`
Jobs bookmarked by students.

```sql
CREATE TABLE saved_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    job_listing_id UUID NOT NULL REFERENCES job_listings(id) ON DELETE CASCADE,
    notes TEXT,
    match_score DECIMAL(3, 2),
    match_explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_saved_job UNIQUE(student_profile_id, job_listing_id)
);

CREATE INDEX idx_saved_jobs_student ON saved_jobs(student_profile_id);
CREATE INDEX idx_saved_jobs_job ON saved_jobs(job_listing_id);
```

#### `applications`
Job application tracking.

```sql
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    job_listing_id UUID REFERENCES job_listings(id) ON DELETE SET NULL,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    resume_id UUID REFERENCES resumes(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'applied', -- 'applied', 'screening', 'interview', 'offer', 'rejected', 'withdrawn'
    applied_date DATE NOT NULL,
    application_url VARCHAR(500),
    notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_applications_student ON applications(student_profile_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_applied_date ON applications(applied_date DESC);
```

#### `application_events`
Timeline of application progress.

```sql
CREATE TABLE application_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'applied', 'status_change', 'interview_scheduled', 'offer_received'
    event_date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_application_events_application ON application_events(application_id);
CREATE INDEX idx_application_events_date ON application_events(event_date DESC);
```

### Interview Intelligence

#### `interview_plans`
Structured interview preparation plans.

```sql
CREATE TABLE interview_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    target_role VARCHAR(255) NOT NULL,
    company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
    application_id UUID REFERENCES applications(id) ON DELETE SET NULL,
    interview_date DATE,
    plan_type VARCHAR(50), -- 'general', 'company-specific', 'role-specific'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'archived'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_interview_plans_student ON interview_plans(student_profile_id);
CREATE INDEX idx_interview_plans_status ON interview_plans(status);
```

#### `preparation_tasks`
Tasks in interview preparation plans.

```sql
CREATE TABLE preparation_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_plan_id UUID NOT NULL REFERENCES interview_plans(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL, -- 'technical', 'behavioral', 'project-discussion', 'aptitude', 'hr'
    task_title VARCHAR(255) NOT NULL,
    task_description TEXT,
    estimated_time_minutes INTEGER,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'skipped'
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_preparation_tasks_plan ON preparation_tasks(interview_plan_id);
CREATE INDEX idx_preparation_tasks_status ON preparation_tasks(status);
```

#### `practice_sessions`
Interview practice sessions.

```sql
CREATE TABLE practice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interview_plan_id UUID NOT NULL REFERENCES interview_plans(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL, -- 'technical', 'behavioral', 'mixed'
    total_questions INTEGER DEFAULT 0,
    completed_questions INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_practice_sessions_plan ON practice_sessions(interview_plan_id);
```

#### `question_attempts`
Individual question responses and evaluations.

```sql
CREATE TABLE question_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    practice_session_id UUID NOT NULL REFERENCES practice_sessions(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_category VARCHAR(50),
    difficulty VARCHAR(20), -- 'easy', 'medium', 'hard'
    student_answer TEXT NOT NULL,
    evaluation_score DECIMAL(3, 2),
    feedback TEXT NOT NULL,
    strengths TEXT[],
    improvements TEXT[],
    sample_answer TEXT,
    time_taken_seconds INTEGER,
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_question_attempts_session ON question_attempts(practice_session_id);
CREATE INDEX idx_question_attempts_category ON question_attempts(question_category);
```

## Data Integrity and Constraints

### Foreign Keys
All foreign keys use `ON DELETE CASCADE` or `ON DELETE SET NULL` appropriately:
- User profile deletion cascades to all student data
- Resume deletion cascades to versions and reviews
- Soft references use SET NULL (e.g., deleted job listings)

### Check Constraints

```sql
-- Salary constraints
ALTER TABLE student_profiles ADD CONSTRAINT check_salary_range 
    CHECK (expected_salary_min IS NULL OR expected_salary_max IS NULL OR expected_salary_min <= expected_salary_max);

-- Score constraints
ALTER TABLE career_recommendations ADD CONSTRAINT check_fit_score 
    CHECK (fit_score >= 0 AND fit_score <= 1);

ALTER TABLE resume_reviews ADD CONSTRAINT check_review_score 
    CHECK (overall_score >= 0 AND overall_score <= 1);

-- Progress constraints
ALTER TABLE career_roadmaps ADD CONSTRAINT check_progress 
    CHECK (progress_percentage >= 0 AND progress_percentage <= 100);

-- Date constraints
ALTER TABLE education_records ADD CONSTRAINT check_education_dates 
    CHECK (end_date IS NULL OR end_date >= start_date);

ALTER TABLE projects ADD CONSTRAINT check_project_dates 
    CHECK (end_date IS NULL OR end_date >= start_date);
```

### Unique Constraints

```sql
-- Prevent duplicate skills per student
ALTER TABLE student_skills ADD CONSTRAINT unique_student_skill 
    UNIQUE(student_profile_id, skill_id);

-- Prevent duplicate job saves
ALTER TABLE saved_jobs ADD CONSTRAINT unique_saved_job 
    UNIQUE(student_profile_id, job_listing_id);

-- One primary resume per student
CREATE UNIQUE INDEX idx_one_primary_resume 
    ON resumes(student_profile_id) WHERE is_primary = true;
```

## Indexes

### Performance Indexes

```sql
-- Common query patterns
CREATE INDEX idx_student_profile_graduation ON student_profiles(graduation_year) 
    WHERE deleted_at IS NULL;

CREATE INDEX idx_job_listings_active ON job_listings(posted_date DESC) 
    WHERE status = 'active';

CREATE INDEX idx_applications_recent ON applications(student_profile_id, applied_date DESC);

-- Search indexes (PostgreSQL full-text search)
CREATE INDEX idx_job_listings_search ON job_listings 
    USING gin(to_tsvector('english', title || ' ' || description));

CREATE INDEX idx_companies_search ON companies 
    USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
```

## Migrations Strategy

### Migration Naming Convention
```
YYYYMMDD_HHMM_description.py
Example: 20240115_1430_create_student_profiles.py
```

### Migration Best Practices
1. Each migration should be reversible (implement both upgrade and downgrade)
2. Add indexes after table creation for large datasets
3. Use batch operations for data migrations
4. Test migrations on a copy of production data
5. Never modify existing migrations after deployment

### Running Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Check current version
alembic current

# View migration history
alembic history
```

## Backup and Recovery

### Backup Strategy
- **Automated**: Supabase handles automated daily backups
- **Manual**: Export critical data before major migrations
- **Point-in-time**: Supabase provides PITR for paid plans

### Data Retention
- Active records: Indefinite retention
- Soft-deleted profiles: 90 days before hard delete
- Application history: 2 years
- Practice sessions: 1 year
- Audit logs: 1 year

## Row Level Security (RLS)

When using Supabase Auth with direct database access:

```sql
-- Enable RLS on all student tables
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Students can only access their own data
CREATE POLICY student_access ON student_profiles
    FOR ALL
    USING (user_id = auth.uid());

CREATE POLICY resume_access ON resumes
    FOR ALL
    USING (student_profile_id IN (
        SELECT id FROM student_profiles WHERE user_id = auth.uid()
    ));
```

## Performance Considerations

### Query Optimization
- Use `EXPLAIN ANALYZE` to verify query plans
- Avoid N+1 queries through proper JOINs
- Use pagination for large result sets
- Consider materialized views for complex aggregations

### Connection Pooling
- Backend uses SQLAlchemy connection pool
- Pool size: 5-10 connections per instance
- Max overflow: 10 additional connections
- Timeout: 30 seconds

---

**Database Version**: 1.0  
**Last Updated**: 2024  
**Status**: Initial Schema Design
