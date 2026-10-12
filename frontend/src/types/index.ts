/**
 * Shared TypeScript types for ORVENA frontend
 */

// User and Authentication
export interface User {
  id: string
  email: string
  created_at: string
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
  expires_in?: number
}

// Student Profile
export interface StudentProfile {
  id: string
  user_id: string
  full_name: string
  phone?: string | null
  location?: string | null
  bio?: string | null
  linkedin_url?: string | null
  github_url?: string | null
  portfolio_url?: string | null
  graduation_year?: number | null
  expected_salary_min?: number | null
  expected_salary_max?: number | null
  profile_completed: boolean
  created_at: string
  updated_at: string
}

// Education
export type EducationLevel = 'high_school' | 'associate' | 'bachelor' | 'master' | 'phd' | 'bootcamp' | 'certification'

export interface EducationRecord {
  id: string
  student_profile_id: string
  institution_name: string
  degree: string
  field_of_study: string
  education_level: EducationLevel
  start_date: string
  end_date?: string | null
  is_current: boolean
  gpa?: number | null
  gpa_scale?: number | null
  honors?: string | null
  activities?: string | null
  created_at: string
  updated_at: string
}

// Skills
export type SkillCategory = 'technical' | 'soft' | 'language' | 'tool' | 'domain'
export type ProficiencyLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert'

export interface Skill {
  id: string
  name: string
  category: SkillCategory
  created_at: string
  updated_at: string
}

export interface StudentSkill {
  id: string
  student_profile_id: string
  skill_id: string
  skill_name: string
  skill_category: SkillCategory
  proficiency_level: ProficiencyLevel
  years_of_experience?: number | null
  last_used_date?: string | null
  is_verified: boolean
  evidence?: string | null
  created_at: string
  updated_at: string
}

// Projects
export interface Project {
  id: string
  student_profile_id: string
  title: string
  description: string
  role?: string | null
  technologies: string[]
  start_date: string
  end_date?: string | null
  is_current: boolean
  project_url?: string | null
  repo_url?: string | null
  demo_url?: string | null
  metrics?: string | null
  team_size?: number | null
  created_at: string
  updated_at: string
}

// Certifications
export interface Certification {
  id: string
  student_profile_id: string
  name: string
  issuing_organization: string
  issue_date: string
  expiry_date?: string | null
  credential_id?: string | null
  credential_url?: string | null
  skills: string[]
  created_at: string
  updated_at: string
}

// Complete Profile Response
export interface CompleteProfile {
  profile: StudentProfile
  education: EducationRecord[]
  skills: StudentSkill[]
  projects: Project[]
  certifications: Certification[]
}

// Career
export interface CareerRole {
  id: string
  name: string
  category: string
  description: string
}

export interface CareerRecommendation {
  id: string
  career_role: CareerRole
  fit_score: number
  reasoning: string
  strengths: string[]
  gaps: string[]
  opportunities: string[]
  threats: string[]
  recommendation_rank?: number
}

export interface CareerRoadmap {
  id: string
  title: string
  description?: string
  target_duration_weeks: number
  status: 'active' | 'completed' | 'paused' | 'archived'
  progress_percentage: number
  milestones: RoadmapMilestone[]
  created_at: string
}

export interface RoadmapMilestone {
  id: string
  title: string
  description?: string
  category: string
  estimated_hours?: number
  sequence_number: number
  status: 'pending' | 'in_progress' | 'completed' | 'skipped'
  completed_at?: string
  resources?: string[]
}

// Resume
export interface Resume {
  id: string
  student_profile_id: string
  title: string
  source_type: 'uploaded' | 'built'
  original_filename?: string
  file_size_bytes?: number
  status: 'processing' | 'ready' | 'failed'
  is_primary: boolean
  created_at: string
  updated_at: string
}

export interface ResumeExtraction {
  id: string
  resume_id: string
  contact_info: any
  education: any[]
  experience: any[]
  skills: any
  projects: any[]
  certifications: any[]
  is_confirmed: boolean
  created_at: string
}

export interface ResumeReview {
  id: string
  resume_id: string
  review_type: 'general' | 'job-tailored'
  overall_score: number
  overall_feedback: string
  findings: ResumeFinding[]
  created_at: string
}

export interface ResumeFinding {
  id: string
  category: string
  severity: 'critical' | 'major' | 'minor' | 'suggestion'
  section?: string
  current_text?: string
  suggested_improvement: string
  reasoning?: string
}

// Jobs
export interface JobListing {
  id: string
  company_name: string
  title: string
  description: string
  role_type?: string
  employment_type?: string
  experience_level?: string
  location?: string
  is_remote: boolean
  salary_min?: number
  salary_max?: number
  salary_currency?: string
  posted_date?: string
  status: 'active' | 'expired' | 'filled'
}

export interface JobMatch {
  job: JobListing
  match_score: number
  match_explanation: string
  met_requirements: any[]
  gap_requirements: any[]
  recommendation: 'apply' | 'improve_first' | 'stretch_opportunity'
}

// Applications
export interface Application {
  id: string
  job_listing_id?: string
  company_name: string
  job_title: string
  status: 'applied' | 'screening' | 'interview' | 'offer' | 'rejected' | 'withdrawn'
  applied_date: string
  notes?: string
  created_at: string
  updated_at: string
}

// Interview
export interface InterviewPlan {
  id: string
  target_role: string
  company_id?: string
  interview_date?: string
  plan_type: 'general' | 'company-specific' | 'role-specific'
  status: 'active' | 'completed' | 'archived'
  tasks: PreparationTask[]
  created_at: string
}

export interface PreparationTask {
  id: string
  category: string
  task_title: string
  task_description?: string
  estimated_time_minutes?: number
  status: 'pending' | 'in_progress' | 'completed' | 'skipped'
}

export interface PracticeSession {
  id: string
  interview_plan_id: string
  session_type: string
  total_questions: number
  completed_questions: number
  started_at: string
  completed_at?: string
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface APIError {
  code: string
  message: string
  details?: any
  request_id?: string
}
