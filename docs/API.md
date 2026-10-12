# ORVENA API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Staging**: `https://api-staging.orvena.com`
- **Production**: `https://api.orvena.com`

## API Versioning

All endpoints are prefixed with `/api/v1/`

## Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

#### POST `/api/v1/auth/register`

Register a new user account.

**Request:**
```json
{
  "email": "student@university.edu",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "user": {
    "id": "uuid",
    "email": "student@university.edu",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### POST `/api/v1/auth/login`

Authenticate and receive tokens.

**Request:**
```json
{
  "email": "student@university.edu",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/api/v1/auth/refresh`

Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Profile Endpoints

### GET `/api/v1/profile`

Get current user's profile.

**Headers**: `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "full_name": "John Doe",
  "email": "student@university.edu",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "bio": "Computer Science student...",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "graduation_year": 2024,
  "current_status": "student",
  "remote_preference": "hybrid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### PATCH `/api/v1/profile`

Update user profile.

**Request:**
```json
{
  "full_name": "John Doe",
  "location": "New York, NY",
  "bio": "Updated bio...",
  "remote_preference": "remote"
}
```

**Response (200):** Updated profile object

### GET `/api/v1/profile/skills`

Get user's skills with proficiency levels.

**Response (200):**
```json
{
  "skills": [
    {
      "id": "uuid",
      "skill": {
        "id": "uuid",
        "name": "Python",
        "category": "technical"
      },
      "proficiency_level": "advanced",
      "years_of_experience": 2.5,
      "evidence_type": "project",
      "last_used_date": "2024-01-15"
    }
  ]
}
```

### POST `/api/v1/profile/skills`

Add a skill to user's profile.

**Request:**
```json
{
  "skill_name": "Python",
  "proficiency_level": "advanced",
  "years_of_experience": 2.5,
  "evidence_type": "project",
  "evidence_description": "Built multiple web applications"
}
```

**Response (201):** Created skill object

---

## Career Intelligence Endpoints

### POST `/api/v1/career/discovery/sessions`

Start a new career discovery session.

**Request:**
```json
{
  "session_type": "discovery"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "student_profile_id": "uuid",
  "session_type": "discovery",
  "status": "in_progress",
  "current_phase": "interests",
  "started_at": "2024-01-15T10:30:00Z"
}
```

### GET `/api/v1/career/discovery/sessions/{session_id}`

Get career discovery session details.

**Response (200):**
```json
{
  "id": "uuid",
  "status": "in_progress",
  "current_phase": "interests",
  "completed_phases": ["background", "education"],
  "responses_count": 8,
  "started_at": "2024-01-15T10:30:00Z"
}
```

### POST `/api/v1/career/discovery/sessions/{session_id}/responses`

Submit a response to a discovery question.

**Request:**
```json
{
  "question_text": "What type of projects do you enjoy working on?",
  "response_text": "I enjoy building web applications with Python and React...",
  "question_category": "interests",
  "phase": "interests"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "question_text": "...",
  "response_text": "...",
  "next_question": {
    "text": "Can you describe a recent project that excited you?",
    "category": "interests",
    "type": "open_ended"
  },
  "created_at": "2024-01-15T10:35:00Z"
}
```

### POST `/api/v1/career/recommendations`

Generate career recommendations based on profile and discovery.

**Request:**
```json
{
  "session_id": "uuid",
  "max_recommendations": 5
}
```

**Response (200):**
```json
{
  "recommendations": [
    {
      "id": "uuid",
      "career_role": {
        "id": "uuid",
        "name": "Full-Stack Developer",
        "category": "Software Engineering",
        "description": "..."
      },
      "fit_score": 0.85,
      "reasoning": "Your strong Python and web development skills...",
      "strengths": [
        "Solid programming foundation",
        "Full-stack project experience"
      ],
      "gaps": [
        "Limited experience with cloud deployment",
        "Need more knowledge in system design"
      ],
      "opportunities": [
        "High demand in tech industry",
        "Remote work widely available"
      ],
      "threats": [
        "Competitive job market",
        "Rapid technology changes"
      ],
      "recommendation_rank": 1
    }
  ],
  "generated_at": "2024-01-15T10:40:00Z"
}
```

### POST `/api/v1/career/roadmaps`

Create a career development roadmap.

**Request:**
```json
{
  "career_goal_id": "uuid",
  "recommendation_id": "uuid",
  "target_duration_weeks": 12
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "title": "Full-Stack Developer Roadmap",
  "description": "12-week plan to become job-ready...",
  "target_duration_weeks": 12,
  "status": "active",
  "progress_percentage": 0,
  "milestones": [
    {
      "id": "uuid",
      "title": "Master React Fundamentals",
      "description": "Learn React hooks, state management...",
      "category": "skill",
      "estimated_hours": 40,
      "sequence_number": 1,
      "status": "pending",
      "resources": [
        "https://react.dev/learn",
        "https://frontendmasters.com/courses/react/"
      ]
    }
  ],
  "created_at": "2024-01-15T10:45:00Z"
}
```

### GET `/api/v1/career/roadmaps/current`

Get user's active roadmap with progress.

**Response (200):** Roadmap object with milestones

### PATCH `/api/v1/career/roadmaps/{roadmap_id}/milestones/{milestone_id}`

Update milestone status.

**Request:**
```json
{
  "status": "completed"
}
```

**Response (200):** Updated milestone object

---

## Resume Intelligence Endpoints

### POST `/api/v1/resumes`

Upload a resume for parsing.

**Content-Type**: `multipart/form-data`

**Request:**
```
file: [PDF or DOCX file]
title: "Software Engineer Resume"
```

**Response (202):**
```json
{
  "id": "uuid",
  "title": "Software Engineer Resume",
  "status": "processing",
  "created_at": "2024-01-15T11:00:00Z"
}
```

### GET `/api/v1/resumes/{resume_id}/status`

Check resume processing status.

**Response (200):**
```json
{
  "id": "uuid",
  "status": "ready",
  "message": "Resume processed successfully"
}
```

### GET `/api/v1/resumes/{resume_id}`

Get resume details.

**Response (200):**
```json
{
  "id": "uuid",
  "student_profile_id": "uuid",
  "title": "Software Engineer Resume",
  "source_type": "uploaded",
  "original_filename": "resume_v3.pdf",
  "file_size_bytes": 125000,
  "status": "ready",
  "is_primary": true,
  "created_at": "2024-01-15T11:00:00Z"
}
```

### GET `/api/v1/resumes/{resume_id}/extraction`

Get extracted structured data from resume.

**Response (200):**
```json
{
  "id": "uuid",
  "resume_id": "uuid",
  "contact_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "location": "San Francisco, CA",
    "linkedin": "https://linkedin.com/in/johndoe"
  },
  "education": [
    {
      "institution": "University of California",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "start_date": "2020-09",
      "end_date": "2024-05",
      "gpa": "3.8"
    }
  ],
  "experience": [
    {
      "company": "Tech Startup Inc",
      "title": "Software Engineering Intern",
      "start_date": "2023-06",
      "end_date": "2023-08",
      "description": "Developed RESTful APIs...",
      "achievements": [
        "Improved API response time by 40%"
      ]
    }
  ],
  "skills": {
    "technical": ["Python", "JavaScript", "React", "PostgreSQL"],
    "soft": ["Team collaboration", "Problem-solving"]
  },
  "projects": [...],
  "certifications": [...],
  "is_confirmed": false
}
```

### PATCH `/api/v1/resumes/{resume_id}/extraction`

Confirm or correct extracted resume data.

**Request:**
```json
{
  "contact_info": {
    "email": "corrected@example.com"
  },
  "is_confirmed": true
}
```

**Response (200):** Updated extraction object

### POST `/api/v1/resumes/{resume_id}/reviews`

Generate AI review and feedback for resume.

**Request:**
```json
{
  "review_type": "general",
  "target_job_id": null
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "resume_id": "uuid",
  "review_type": "general",
  "overall_score": 0.78,
  "overall_feedback": "Your resume shows strong technical skills...",
  "findings": [
    {
      "category": "content",
      "severity": "major",
      "section": "experience",
      "current_text": "Worked on web development projects",
      "suggested_improvement": "Developed 5 responsive web applications using React...",
      "reasoning": "Be specific about quantity and technologies used"
    }
  ],
  "created_at": "2024-01-15T11:10:00Z"
}
```

### POST `/api/v1/resumes/{resume_id}/tailor`

Tailor resume for a specific job.

**Request:**
```json
{
  "job_listing_id": "uuid"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "resume_id": "uuid",
  "job_listing_id": "uuid",
  "review_type": "job-tailored",
  "match_analysis": {
    "matching_requirements": 8,
    "total_requirements": 10,
    "match_percentage": 80,
    "met_requirements": [...],
    "gap_requirements": [...]
  },
  "findings": [...],
  "tailored_sections": {
    "summary": "...",
    "highlighted_skills": [...]
  }
}
```

### POST `/api/v1/resumes/build`

Build a new resume from profile data.

**Request:**
```json
{
  "title": "Full-Stack Developer Resume",
  "template": "professional",
  "sections": ["contact", "summary", "experience", "education", "skills", "projects"],
  "target_role": "Full-Stack Developer"
}
```

**Response (201):** New resume object

### GET `/api/v1/resumes/{resume_id}/export`

Export resume as PDF or DOCX.

**Query Parameters:** `?format=pdf` or `?format=docx`

**Response (200):**
```json
{
  "download_url": "https://storage.supabase.co/...",
  "expires_at": "2024-01-15T11:20:00Z",
  "format": "pdf"
}
```

---

## Job Intelligence Endpoints

### GET `/api/v1/jobs`

Search and filter job listings.

**Query Parameters:**
- `role_type`: Filter by role (e.g., "Full-Stack Developer")
- `location`: Filter by location
- `is_remote`: Boolean
- `experience_level`: "entry", "mid", "senior"
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 20, max: 100)

**Response (200):**
```json
{
  "jobs": [
    {
      "id": "uuid",
      "company_name": "Tech Corp",
      "title": "Junior Full-Stack Developer",
      "description": "We're looking for...",
      "role_type": "Full-Stack Developer",
      "employment_type": "full-time",
      "experience_level": "entry",
      "location": "San Francisco, CA",
      "is_remote": false,
      "salary_min": 80000,
      "salary_max": 100000,
      "salary_currency": "USD",
      "posted_date": "2024-01-10",
      "status": "active"
    }
  ],
  "total": 45,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

### GET `/api/v1/jobs/{job_id}`

Get detailed job information.

**Response (200):**
```json
{
  "id": "uuid",
  "company": {
    "id": "uuid",
    "name": "Tech Corp",
    "website": "https://techcorp.com",
    "industry": "Software",
    "company_size": "201-1000"
  },
  "title": "Junior Full-Stack Developer",
  "description": "Full job description...",
  "requirements": [
    {
      "requirement_text": "2+ years experience with React",
      "requirement_type": "skill",
      "importance": "required"
    }
  ],
  "posted_date": "2024-01-10",
  "application_url": "https://techcorp.com/careers/apply",
  "status": "active",
  "last_verified_at": "2024-01-15T00:00:00Z"
}
```

### GET `/api/v1/jobs/{job_id}/match`

Get personalized match analysis for a job.

**Response (200):**
```json
{
  "job_id": "uuid",
  "match_score": 0.82,
  "match_explanation": "You're a strong match because...",
  "met_requirements": [
    {
      "requirement": "Experience with React",
      "evidence": "3 projects using React, 2 years experience"
    }
  ],
  "gap_requirements": [
    {
      "requirement": "Experience with Docker",
      "recommendation": "Complete Docker fundamentals course"
    }
  ],
  "recommendation": "apply" | "improve_first" | "stretch_opportunity"
}
```

### POST `/api/v1/jobs/recommendations`

Get personalized job recommendations.

**Request:**
```json
{
  "max_results": 10,
  "preferences": {
    "remote_only": false,
    "max_commute_distance_km": 50,
    "min_salary": 70000
  }
}
```

**Response (200):**
```json
{
  "recommendations": [
    {
      "job": {...},
      "match_score": 0.85,
      "match_reasons": [...]
    }
  ]
}
```

### POST `/api/v1/jobs/{job_id}/save`

Save a job to favorites.

**Response (201):**
```json
{
  "id": "uuid",
  "job_listing_id": "uuid",
  "match_score": 0.82,
  "match_explanation": "...",
  "notes": null,
  "created_at": "2024-01-15T12:00:00Z"
}
```

### GET `/api/v1/jobs/saved`

Get saved jobs.

**Response (200):**
```json
{
  "saved_jobs": [
    {
      "id": "uuid",
      "job": {...},
      "notes": "Applied on 01/15",
      "created_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

---

## Application Tracking Endpoints

### POST `/api/v1/applications`

Create a new job application record.

**Request:**
```json
{
  "job_listing_id": "uuid",
  "company_name": "Tech Corp",
  "job_title": "Full-Stack Developer",
  "resume_id": "uuid",
  "applied_date": "2024-01-15",
  "application_url": "https://...",
  "notes": "Applied through company website"
}
```

**Response (201):** Created application object

### GET `/api/v1/applications`

Get all applications with filtering.

**Query Parameters:** `?status=applied&sort=applied_date_desc`

**Response (200):**
```json
{
  "applications": [
    {
      "id": "uuid",
      "company_name": "Tech Corp",
      "job_title": "Full-Stack Developer",
      "status": "interview",
      "applied_date": "2024-01-15",
      "events": [
        {
          "event_type": "applied",
          "event_date": "2024-01-15",
          "description": "Application submitted"
        },
        {
          "event_type": "interview_scheduled",
          "event_date": "2024-01-18",
          "description": "Technical interview scheduled"
        }
      ],
      "created_at": "2024-01-15T13:00:00Z"
    }
  ]
}
```

### PATCH `/api/v1/applications/{application_id}`

Update application status.

**Request:**
```json
{
  "status": "interview",
  "notes": "Technical interview scheduled for 01/20"
}
```

**Response (200):** Updated application object

---

## Interview Preparation Endpoints

### POST `/api/v1/interview/plans`

Create an interview preparation plan.

**Request:**
```json
{
  "target_role": "Full-Stack Developer",
  "company_id": "uuid",
  "application_id": "uuid",
  "interview_date": "2024-01-25",
  "plan_type": "company-specific"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "target_role": "Full-Stack Developer",
  "interview_date": "2024-01-25",
  "status": "active",
  "tasks": [
    {
      "category": "technical",
      "task_title": "Review JavaScript fundamentals",
      "estimated_time_minutes": 120,
      "priority": 1,
      "status": "pending"
    }
  ],
  "created_at": "2024-01-15T14:00:00Z"
}
```

### POST `/api/v1/interview/sessions`

Start a practice interview session.

**Request:**
```json
{
  "interview_plan_id": "uuid",
  "session_type": "technical",
  "question_count": 5
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "interview_plan_id": "uuid",
  "session_type": "technical",
  "total_questions": 5,
  "completed_questions": 0,
  "current_question": {
    "text": "Explain the difference between var, let, and const in JavaScript",
    "category": "technical",
    "difficulty": "medium"
  },
  "started_at": "2024-01-15T14:10:00Z"
}
```

### POST `/api/v1/interview/sessions/{session_id}/responses`

Submit an answer to a practice question.

**Request:**
```json
{
  "question_text": "Explain the difference between var, let, and const...",
  "student_answer": "var is function-scoped while let and const are block-scoped...",
  "time_taken_seconds": 180
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "evaluation_score": 0.85,
  "feedback": "Good explanation of scoping differences...",
  "strengths": [
    "Correctly explained scoping",
    "Mentioned hoisting behavior"
  ],
  "improvements": [
    "Could elaborate on temporal dead zone",
    "Add practical use case examples"
  ],
  "sample_answer": "Comprehensive answer would include...",
  "next_question": {
    "text": "What is a closure in JavaScript?",
    "category": "technical",
    "difficulty": "medium"
  }
}
```

### GET `/api/v1/interview/plans/{plan_id}/progress`

Get preparation progress.

**Response (200):**
```json
{
  "plan_id": "uuid",
  "completed_tasks": 8,
  "total_tasks": 15,
  "progress_percentage": 53,
  "practice_sessions_completed": 3,
  "weak_topics": [
    {
      "topic": "System Design",
      "attempts": 5,
      "average_score": 0.62
    }
  ],
  "strengths": [
    {
      "topic": "JavaScript",
      "attempts": 8,
      "average_score": 0.88
    }
  ]
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: External service error
- `503 Service Unavailable`: Temporary service outage

### Common Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_REQUIRED`: Missing or invalid token
- `PERMISSION_DENIED`: User lacks required permission
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `EXTERNAL_SERVICE_ERROR`: Third-party service failure
- `PROCESSING_ERROR`: Document or AI processing failed
- `STORAGE_ERROR`: File storage operation failed

---

**API Version**: 1.0  
**Last Updated**: 2024  
**OpenAPI Spec**: Available at `/api/v1/openapi.json`
