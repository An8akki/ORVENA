/**
 * API Client for ORVENA Backend
 * Provides centralized HTTP communication with error handling
 */

import { getAccessToken } from './auth'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class APIError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

interface RequestOptions extends RequestInit {
  token?: string
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch {
      throw new APIError(
        response.status,
        'UNKNOWN_ERROR',
        response.statusText || 'An error occurred'
      )
    }

    let errorMessage = 'An error occurred'
    if (errorData.error?.message) {
      errorMessage = errorData.error.message
    } else if (typeof errorData.detail === 'string') {
      errorMessage = errorData.detail
    } else if (Array.isArray(errorData.detail)) {
      errorMessage = errorData.detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ')
    } else if (errorData.detail) {
      errorMessage = JSON.stringify(errorData.detail)
    }

    throw new APIError(
      response.status,
      errorData.error?.code || 'UNKNOWN_ERROR',
      errorMessage,
      errorData.error?.details || errorData.detail
    )
  }

  if (response.status === 204) {
    return {} as T
  }

  return response.json()
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options

  const headers = new Headers(fetchOptions.headers)
  if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  // Get token from Supabase session if not provided
  const authToken = token || await getAccessToken()
  if (authToken) {
    headers.set('Authorization', `Bearer ${authToken}`)
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  })

  return handleResponse<T>(response)
}

export const api = {
  get: <T>(endpoint: string, token?: string) =>
    apiRequest<T>(endpoint, { method: 'GET', token }),

  post: <T>(endpoint: string, data?: any, token?: string) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      token,
    }),

  patch: <T>(endpoint: string, data?: any, token?: string) =>
    apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
      token,
    }),

  put: <T>(endpoint: string, data?: any, token?: string) =>
    apiRequest<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      token,
    }),

  delete: <T>(endpoint: string, token?: string) =>
    apiRequest<T>(endpoint, { method: 'DELETE', token }),

  // Special method for file uploads
  upload: async <T>(endpoint: string, formData: FormData, token?: string): Promise<T> => {
    const headers: HeadersInit = {}

    // Get token from Supabase session if not provided
    const authToken = token || await getAccessToken()
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    })

    return handleResponse<T>(response)
  },
}

// Wrapper function for direct calls (backward compatibility)
export async function apiClient<T>(
  endpoint: string,
  options?: RequestOptions
): Promise<T> {
  return apiRequest<T>(endpoint, options)
}

// Export as default and named for flexibility
export default api
