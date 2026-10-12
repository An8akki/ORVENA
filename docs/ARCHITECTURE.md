# ORVENA Architecture Documentation

## System Overview

ORVENA is built as a **modular monolith** - a single cohesive application with clear internal boundaries between modules. This architecture provides the benefits of modularity without the operational complexity of microservices.

## Architecture Principles

1. **Clear Module Boundaries**: Each domain (Career, Resume, Jobs, Interviews) has isolated components
2. **Layered Architecture**: Separation of concerns through API, Service, Repository, and Data layers
3. **Provider Independence**: External integrations abstracted behind interfaces
4. **Security by Design**: Authentication and authorization at every layer
5. **Performance First**: Optimized for free-tier hosting with minimal resource usage

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / Client                     │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend (Vercel)                   │
│  ┌────────────┬──────────────┬──────────────────────┐  │
│  │ App Router │  Components  │  Feature Modules     │  │
│  │  (Pages)   │   (UI/UX)    │  (Business Logic)    │  │
│  └────────────┴──────────────┴──────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────────────┐
│             FastAPI Backend (Render)                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │ API Layer (Routes, Validation, Auth)            │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Service Layer (Business Logic, Orchestration)   │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Repository Layer (Data Access)                  │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ Integration Layer (External Services)           │   │
│  └─────────────────────────────────────────────────┘   │
└────────────┬──────────────────┬─────────────────────────┘
             │                  │
             ▼                  ▼
┌──────────────────────┐  ┌─────────────────┐
│ Supabase             │  │  LLM Provider   │
│ - PostgreSQL         │  │  (Gemini API)   │
│ - Auth               │  └─────────────────┘
│ - Storage            │
└──────────────────────┘
```

## Frontend Architecture

### Technology Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix primitives)
- **State**: React hooks, server components where appropriate
- **Forms**: React Hook Form + Zod
- **API Client**: Native fetch with custom error handling

### Directory Structure

```
frontend/src/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Auth routes (grouped)
│   ├── (dashboard)/         # Protected app routes
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Landing page
│
├── components/
│   ├── ui/                  # Base components (shadcn)
│   ├── layout/              # Layout components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── MobileNav.tsx
│   │   └── AppShell.tsx
│   └── shared/              # Shared components
│       ├── LoadingState.tsx
│       ├── ErrorState.tsx
│       ├── EmptyState.tsx
│       └── ConfirmDialog.tsx
│
├── features/                # Feature modules
│   ├── career/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── types/
│   ├── resume/
│   ├── jobs/
│   ├── interviews/
│   └── profile/
│
├── lib/                     # Utilities
│   ├── api-client.ts        # Centralized API client
│   ├── auth.ts              # Auth helpers
│   ├── storage.ts           # Local storage utilities
│   └── utils.ts             # General utilities
│
├── hooks/                   # Custom hooks
│   ├── useAuth.ts
│   ├── useToast.ts
│   └── useDebounce.ts
│
├── schemas/                 # Zod validation
│   └── index.ts
│
└── types/                   # TypeScript types
    └── index.ts
```

### Rendering Strategy
- **Server Components**: Default for static content, data fetching
- **Client Components**: Interactive UI, forms, real-time updates
- **SSR**: Auth pages, dashboard for initial load
- **Static Generation**: Marketing pages, documentation

### State Management
- Server state: React Query / SWR (optional, based on needs)
- Form state: React Hook Form
- UI state: React useState/useReducer
- Global state: Context API (minimal usage)

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: pytest, HTTPX

### Directory Structure

```
backend/app/
├── main.py                  # Application entry point
│
├── api/                     # API layer
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── router.py        # Main router
│   │   ├── career.py
│   │   ├── resume.py
│   │   ├── jobs.py
│   │   ├── interviews.py
│   │   └── profile.py
│   └── dependencies.py      # Dependency injection
│
├── core/                    # Core infrastructure
│   ├── config.py            # Settings (pydantic-settings)
│   ├── security.py          # Auth, JWT validation
│   ├── logging.py           # Structured logging
│   ├── exceptions.py        # Custom exceptions
│   └── middleware.py        # CORS, logging, error handling
│
├── db/                      # Database
│   ├── base.py              # Base class, imports
│   ├── session.py           # Session management
│   └── models/              # SQLAlchemy models
│       ├── __init__.py
│       ├── user.py
│       ├── profile.py
│       ├── career.py
│       ├── resume.py
│       ├── job.py
│       └── interview.py
│
├── schemas/                 # Pydantic schemas
│   ├── __init__.py
│   ├── career.py
│   ├── resume.py
│   ├── job.py
│   └── interview.py
│
├── repositories/            # Data access
│   ├── base.py              # Generic repository
│   ├── career.py
│   ├── resume.py
│   ├── job.py
│   └── interview.py
│
├── services/                # Business logic
│   ├── career_service.py
│   ├── resume_service.py
│   ├── job_service.py
│   └── interview_service.py
│
├── modules/                 # Domain modules
│   ├── career_intelligence/
│   │   ├── discovery.py
│   │   ├── recommendations.py
│   │   └── roadmap.py
│   ├── resume_intelligence/
│   │   ├── parser.py
│   │   ├── analyzer.py
│   │   └── builder.py
│   ├── job_intelligence/
│   │   ├── matcher.py
│   │   └── scraper.py
│   └── interview_intelligence/
│       ├── question_generator.py
│       └── evaluator.py
│
├── integrations/            # External services
│   ├── llm/
│   │   ├── base.py          # Provider interface
│   │   ├── gemini.py        # Gemini implementation
│   │   └── prompts.py       # Prompt templates
│   ├── storage/
│   │   └── supabase.py      # File storage
│   └── job_sources/
│       └── base.py          # Job API abstraction
│
└── utils/                   # Utilities
    ├── text_processing.py
    ├── validators.py
    └── datetime.py
```

### Layered Responsibilities

#### 1. API Layer (Routes)
**Responsibilities:**
- HTTP request/response handling
- Request validation (via Pydantic)
- Authentication enforcement
- Response serialization
- Error mapping to HTTP status codes

**Does NOT:**
- Contain business logic
- Access database directly
- Call external services

#### 2. Service Layer
**Responsibilities:**
- Business logic orchestration
- Transaction management
- Cross-module coordination
- External service integration
- Complex validations

**Does NOT:**
- Handle HTTP concerns
- Construct SQL queries directly

#### 3. Repository Layer
**Responsibilities:**
- Database queries
- CRUD operations
- Query optimization
- Transaction execution

**Does NOT:**
- Contain business rules
- Call external APIs

#### 4. Integration Layer
**Responsibilities:**
- External API communication
- Provider-specific logic
- Error translation
- Rate limiting
- Retry logic

## Module Architecture

### Career Intelligence Module

```
Career Discovery → Question Generation → Response Collection
                                       ↓
                      Career Analysis ← Student Profile
                                       ↓
                          Recommendations + Explanations
                                       ↓
                              Career Roadmap
```

**Key Components:**
- Discovery Session Manager
- Adaptive Question Generator (LLM-based)
- Career Matcher (rule-based + AI)
- Roadmap Generator
- SWOT Analyzer

### Resume Intelligence Module

```
Upload PDF/DOCX → Parse & Extract → Confirm Extraction
                                          ↓
                     AI Analysis ← Resume Content + Job Target
                                          ↓
                              Improvement Suggestions
                                          ↓
                           Updated Resume → Export
```

**Key Components:**
- Document Parser (PyMuPDF, python-docx)
- Resume Extractor (LLM-based structured extraction)
- Resume Analyzer (rule-based + AI feedback)
- Resume Builder (template-based generation)
- Job Tailor (comparison and optimization)

### Job Intelligence Module

```
Student Profile + Preferences → Job Matcher → Ranked Opportunities
                                                      ↓
                                          Job Detail + Match Explanation
                                                      ↓
                                         Application Tracker
```

**Key Components:**
- Job Source Adapters
- Eligibility Filter
- Match Scorer
- Company Intelligence Aggregator

### Interview Intelligence Module

```
Target Role + Company → Preparation Plan
                              ↓
              Practice Questions ← Question Bank
                              ↓
                   Student Response → AI Evaluation
                              ↓
                      Feedback + Progress Tracking
```

**Key Components:**
- Question Generator (role-specific)
- Answer Evaluator (rubric-based + AI)
- Progress Tracker
- Weak Topic Identifier

## Data Flow Patterns

### 1. Simple Query
```
Client → API Route → Service → Repository → Database
                                              ↓
Client ← JSON Response ← Schema ← Model ← Result
```

### 2. AI-Enhanced Operation
```
Client → API Route → Service → LLM Integration → External API
                         ↓
                    Validate Response
                         ↓
                    Repository → Database
                         ↓
Client ← Response
```

### 3. File Upload
```
Client → Upload → API → Validate → Storage Service → Supabase Storage
                           ↓
                    Parse Document
                           ↓
                    Extract Data (LLM)
                           ↓
                    Save Metadata → Database
                           ↓
Client ← Extraction Result
```

## Security Architecture

### Authentication Flow
```
1. User registers/signs in via Supabase Auth
2. Supabase returns JWT access token
3. Frontend stores token securely
4. Frontend includes token in Authorization header
5. Backend validates JWT signature and claims
6. Backend extracts user_id from token
7. Backend enforces ownership in queries
```

### Authorization Strategy
- **Supabase RLS**: Row-level security for direct database access
- **API Layer**: Ownership validation in every route
- **Service Layer**: Business rule enforcement
- **Repository Layer**: Filtered queries by user_id

### Data Protection
- **At Rest**: PostgreSQL encryption (Supabase)
- **In Transit**: HTTPS/TLS for all communication
- **Uploaded Files**: Private storage bucket with signed URLs
- **Secrets**: Environment variables, never in code

## Integration Patterns

### LLM Provider Abstraction

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        **kwargs
    ) -> BaseModel:
        pass
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int,
        **kwargs
    ) -> str:
        pass
```

**Benefits:**
- Switch providers without changing business logic
- Consistent error handling
- Unified retry and timeout logic
- Easy testing with mock providers

### Repository Pattern

```python
class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: UUID) -> Optional[T]: ...
    async def create(self, obj: T) -> T: ...
    async def update(self, obj: T) -> T: ...
    async def delete(self, id: UUID) -> bool: ...
    async def list(self, filters: dict) -> List[T]: ...
```

## Performance Considerations

### Database Optimization
- Connection pooling (SQLAlchemy async pool)
- Indexed foreign keys and frequently queried fields
- Pagination for large result sets
- Selective column loading (avoid SELECT *)
- Relationship lazy loading where appropriate

### Caching Strategy
- **Browser**: Service Worker for static assets
- **API**: In-memory caching for static data (career roles, skills)
- **Database**: Query result caching where appropriate
- **Files**: CDN caching for public assets

### AI Call Optimization
- Minimize context sent to LLM
- Reuse previous results when inputs unchanged
- Batch compatible operations
- Use cheaper models for simple tasks
- Cache AI-generated content when safe

## Error Handling

### Exception Hierarchy
```
Exception
└── OrvenaDomainError
    ├── NotFoundError
    ├── PermissionDeniedError
    ├── ValidationError
    ├── ExternalServiceError
    │   ├── LLMProviderError
    │   ├── StorageError
    │   └── JobSourceError
    └── DatabaseError
```

### Error Propagation
1. Domain exceptions raised in services
2. Caught by FastAPI exception handlers
3. Mapped to appropriate HTTP status
4. Logged with request context
5. Returned as structured JSON

## Deployment Architecture

### Production Setup
```
Vercel (Frontend)
    ↓
Render (Backend)
    ↓
Supabase (Database + Auth + Storage)
    ↓
Gemini API (AI Provider)
```

### Environment Separation
- **Development**: Local services + Supabase dev project
- **Staging**: Deployed services + Supabase staging project
- **Production**: Deployed services + Supabase production project

### Monitoring & Observability
- Structured JSON logging
- Request ID tracking
- Error aggregation (optional: Sentry)
- Performance metrics (optional: custom dashboard)

## Future Scalability

### Horizontal Scaling
- Stateless backend enables multiple instances
- Database connection pooling across instances
- Shared session state via Supabase Auth

### Potential Optimizations
- Add Redis for caching and session storage
- Implement background job queue (Celery/RQ)
- Introduce CDN for static assets
- Add read replicas for database

### Modularity Path
- Modules can be extracted to separate services if needed
- Clear boundaries make extraction straightforward
- Shared schemas enable API contracts

---

**Architecture Version**: 1.0  
**Last Updated**: 2024  
**Status**: Initial Implementation
