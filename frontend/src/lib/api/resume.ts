/**
 * API client functions for resume management
 */

import { apiClient } from '../api-client'
import { getAccessToken } from '../auth'

export interface Resume {
  id: string
  student_profile_id: string
  title: string
  source_type: string
  original_filename: string | null
  file_size_bytes: number | null
  storage_path: string | null
  content_type: string | null
  status: 'processing' | 'ready' | 'failed'
  is_primary: boolean
  created_at: string
  updated_at: string
}

export interface ResumeExtraction {
  id: string
  resume_id: string
  raw_text: string | null
  contact_info: Record<string, unknown> | null
  summary?: string | null
  education: unknown
  experience: unknown
  projects: unknown
  skills: unknown
  certifications: unknown
  achievements: unknown
  is_confirmed: boolean
  extraction_method: string | null
  created_at: string
}

export interface ResumeAnalysis {
  resume_id: string
  overall_score: number
  score_grade: string
  category_scores: Record<string, number>
  suggestions: string[]
  strengths: string[]
  missing_elements: string[]
  ats_friendly: boolean
  estimated_pass_rate: string
  role_fit: Array<{
    role: string
    score: number
    matched_skills: string[]
    priority_gaps: string[]
    assessment: string
  }>
  extraction_method: string | null
  normalized_extraction: Partial<ResumeExtraction>
}

export async function getResume(resumeId: string): Promise<Resume> {
  return apiClient<Resume>(`/api/v1/resumes/${resumeId}`)
}

export async function getResumeExtraction(resumeId: string): Promise<ResumeExtraction> {
  return apiClient<ResumeExtraction>(`/api/v1/resumes/${resumeId}/extraction`)
}

export async function getResumeAnalysis(resumeId: string): Promise<ResumeAnalysis> {
  return apiClient<ResumeAnalysis>(`/api/v1/resumes/${resumeId}/analysis`)
}

export async function uploadResume(file: File, title: string): Promise<Resume> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('title', title)

  const token = await getAccessToken()
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const response = await fetch(`${apiUrl}/api/v1/resumes/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    const message = error.error?.message || error.detail || error.message
    throw new Error(typeof message === 'string' ? message : 'Failed to upload resume')
  }

  return response.json()
}

export async function getResumes(): Promise<Resume[]> {
  return apiClient<Resume[]>('/api/v1/resumes')
}

export async function setPrimaryResume(resumeId: string): Promise<Resume> {
  return apiClient<Resume>(`/api/v1/resumes/${resumeId}/set-primary`, {
    method: 'POST',
  })
}

export async function deleteResume(resumeId: string): Promise<void> {
  return apiClient<void>(`/api/v1/resumes/${resumeId}`, {
    method: 'DELETE',
  })
}
