/**
 * API client functions for career discovery
 */

import { apiClient } from '../api-client'

export interface CareerDiscoverySession {
  id: string
  student_profile_id: string
  session_type: 'initial' | 'refinement' | 'focused'
  status: 'in_progress' | 'completed' | 'abandoned'
  current_phase: string | null
  completed_phases: string[] | null
  responses: CareerDiscoveryResponse[]
  completed_at: string | null
  started_at: string
  created_at: string
  updated_at: string
}

export interface CareerDiscoveryResponse {
  id: string
  session_id: string
  sequence_number: number
  question_text: string
  response_text: string
  question_category: string | null
  phase: string | null
  created_at: string
}

export interface NextQuestionResponse {
  question_number: number
  question_text: string
  question_type: 'mcq' | 'descriptive' | 'pathway_selection' | string
  options?: Record<string, string> | null
  session_id: string
}

export interface SessionAnalysis {
  session_id: string
  insights: any
  summary: string
}

export interface CareerRecommendation {
  id: string
  student_profile_id: string
  career_role_id: string
  session_id: string | null
  fit_score: number
  reasoning: string
  strengths: string[]
  gaps: string[]
  opportunities: string[]
  threats: string[]
  recommendation_rank: number
  career_role: {
    id: string
    name: string
    category: string
    description: string
    typical_salary_min: number | null
    typical_salary_max: number | null
  }
  created_at: string
  updated_at: string
}

export interface CareerRoadmap {
  id: string
  student_profile_id: string
  target_role_id: string
  title: string
  description: string | null
  target_duration_weeks: number
  status: string
  progress_percentage: number
  target_role: {
    id: string
    name: string
    category: string
  }
  milestones: RoadmapMilestone[]
  created_at: string
  updated_at: string
}

export interface RoadmapMilestone {
  id: string
  roadmap_id: string
  title: string
  description: string | null
  category: string
  estimated_hours: number | null
  sequence_number: number
  resources: string[]
  status: 'pending' | 'in_progress' | 'completed' | 'skipped'
  completed_at: string | null
  created_at: string
  updated_at: string
}

// Discovery Sessions
export async function createDiscoverySession(
  sessionType: 'initial' | 'refinement' | 'focused' = 'initial'
): Promise<CareerDiscoverySession> {
  return apiClient<CareerDiscoverySession>('/api/v1/career/discovery/sessions', {
    method: 'POST',
    body: JSON.stringify({ session_type: sessionType }),
  })
}

export async function getDiscoverySessions(): Promise<CareerDiscoverySession[]> {
  return apiClient<CareerDiscoverySession[]>('/api/v1/career/discovery/sessions')
}

export async function getActiveDiscoverySession(): Promise<CareerDiscoverySession> {
  return apiClient<CareerDiscoverySession>('/api/v1/career/discovery/sessions/active')
}

export async function getDiscoverySession(sessionId: string): Promise<CareerDiscoverySession> {
  return apiClient<CareerDiscoverySession>(`/api/v1/career/discovery/sessions/${sessionId}`)
}

export async function getNextQuestion(sessionId: string): Promise<NextQuestionResponse> {
  return apiClient<NextQuestionResponse>('/api/v1/career/discovery/next-question', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })
}

export async function submitAnswer(data: {
  session_id: string
  question_number: number
  question_text: string
  response_text: string
}): Promise<CareerDiscoveryResponse> {
  return apiClient<CareerDiscoveryResponse>('/api/v1/career/discovery/submit-answer', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function completeDiscoverySession(sessionId: string): Promise<void> {
  return apiClient<void>(`/api/v1/career/discovery/sessions/${sessionId}/complete`, {
    method: 'POST',
  })
}

export async function analyzeDiscoverySession(sessionId: string): Promise<SessionAnalysis> {
  return apiClient<SessionAnalysis>(`/api/v1/career/discovery/sessions/${sessionId}/analysis`)
}

// Recommendations
export async function generateRecommendations(sessionId?: string): Promise<CareerRecommendation[]> {
  const url = sessionId
    ? `/api/v1/career/recommendations/generate?session_id=${sessionId}`
    : '/api/v1/career/recommendations/generate'
  
  return apiClient<CareerRecommendation[]>(url, {
    method: 'POST',
  })
}

export async function getRecommendations(): Promise<CareerRecommendation[]> {
  return apiClient<CareerRecommendation[]>('/api/v1/career/recommendations')
}

// Roadmaps
export async function createRoadmap(data: {
  recommendation_id?: string
  career_goal_id?: string
  career_role_id?: string
  title?: string
  target_duration_weeks: number
}): Promise<CareerRoadmap> {
  return apiClient<CareerRoadmap>('/api/v1/career/roadmaps', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getRoadmaps(): Promise<CareerRoadmap[]> {
  return apiClient<CareerRoadmap[]>('/api/v1/career/roadmaps')
}

export async function updateMilestoneStatus(
  milestoneId: string,
  status: 'pending' | 'in_progress' | 'completed' | 'skipped'
): Promise<RoadmapMilestone> {
  return apiClient<RoadmapMilestone>(`/api/v1/career/roadmaps/milestones/${milestoneId}`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}
