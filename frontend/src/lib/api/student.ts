/**
 * API client functions for student profile management
 */

import { apiClient } from '../api-client'
import type {
  StudentProfile,
  CompleteProfile,
  EducationRecord,
  StudentSkill,
  Project,
  Certification,
} from '@/types'

// Profile
export async function getProfile(): Promise<StudentProfile> {
  return apiClient<StudentProfile>('/api/v1/student/profile')
}

export async function getCompleteProfile(): Promise<CompleteProfile> {
  return apiClient<CompleteProfile>('/api/v1/student/profile/complete')
}

export async function createProfile(
  data: Partial<StudentProfile>
): Promise<StudentProfile> {
  return apiClient<StudentProfile>('/api/v1/student/profile', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateProfile(
  data: Partial<StudentProfile>
): Promise<StudentProfile> {
  return apiClient<StudentProfile>('/api/v1/student/profile', {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

// Education
export async function getEducationRecords(): Promise<EducationRecord[]> {
  return apiClient<EducationRecord[]>('/api/v1/student/education')
}

export async function getEducationRecord(id: string): Promise<EducationRecord> {
  return apiClient<EducationRecord>(`/api/v1/student/education/${id}`)
}

export async function createEducationRecord(
  data: Omit<EducationRecord, 'id' | 'student_profile_id' | 'created_at' | 'updated_at'>
): Promise<EducationRecord> {
  return apiClient<EducationRecord>('/api/v1/student/education', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateEducationRecord(
  id: string,
  data: Partial<Omit<EducationRecord, 'id' | 'student_profile_id' | 'created_at' | 'updated_at'>>
): Promise<EducationRecord> {
  return apiClient<EducationRecord>(`/api/v1/student/education/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteEducationRecord(id: string): Promise<void> {
  return apiClient<void>(`/api/v1/student/education/${id}`, {
    method: 'DELETE',
  })
}

// Skills
export async function getStudentSkills(): Promise<StudentSkill[]> {
  return apiClient<StudentSkill[]>('/api/v1/student/skills')
}

export async function getStudentSkill(id: string): Promise<StudentSkill> {
  return apiClient<StudentSkill>(`/api/v1/student/skills/${id}`)
}

export async function createStudentSkill(
  data: Omit<StudentSkill, 'id' | 'student_profile_id' | 'skill_id' | 'created_at' | 'updated_at'>
): Promise<StudentSkill> {
  return apiClient<StudentSkill>('/api/v1/student/skills', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateStudentSkill(
  id: string,
  data: Partial<Pick<StudentSkill, 'proficiency_level' | 'years_of_experience' | 'last_used_date' | 'is_verified' | 'evidence'>>
): Promise<StudentSkill> {
  return apiClient<StudentSkill>(`/api/v1/student/skills/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteStudentSkill(id: string): Promise<void> {
  return apiClient<void>(`/api/v1/student/skills/${id}`, {
    method: 'DELETE',
  })
}

// Projects
export async function getProjects(): Promise<Project[]> {
  return apiClient<Project[]>('/api/v1/student/projects')
}

export async function getProject(id: string): Promise<Project> {
  return apiClient<Project>(`/api/v1/student/projects/${id}`)
}

export async function createProject(
  data: Omit<Project, 'id' | 'student_profile_id' | 'created_at' | 'updated_at'>
): Promise<Project> {
  return apiClient<Project>('/api/v1/student/projects', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateProject(
  id: string,
  data: Partial<Omit<Project, 'id' | 'student_profile_id' | 'created_at' | 'updated_at'>>
): Promise<Project> {
  return apiClient<Project>(`/api/v1/student/projects/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteProject(id: string): Promise<void> {
  return apiClient<void>(`/api/v1/student/projects/${id}`, {
    method: 'DELETE',
  })
}

// Certifications
export async function getCertifications(): Promise<Certification[]> {
  return apiClient<Certification[]>('/api/v1/student/certifications')
}

export async function getCertification(id: string): Promise<Certification> {
  return apiClient<Certification>(`/api/v1/student/certifications/${id}`)
}

export async function createCertification(
  data: Omit<Certification, 'id' | 'student_profile_id' | 'created_at' | 'updated_at'>
): Promise<Certification> {
  return apiClient<Certification>('/api/v1/student/certifications', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateCertification(
  id: string,
  data: Partial<Omit<Certification, 'id' | 'student_profile_id' | 'created_at' | 'updated_at'>>
): Promise<Certification> {
  return apiClient<Certification>(`/api/v1/student/certifications/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function deleteCertification(id: string): Promise<void> {
  return apiClient<void>(`/api/v1/student/certifications/${id}`, {
    method: 'DELETE',
  })
}
