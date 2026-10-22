# ORVENA Project Code Guide

This guide explains how the repository is organized, what its main source files do, and how a user action travels through the app. It describes the code currently in the repository; it is not a list of planned features. Generated files, installed packages, secrets, and local environment files are intentionally not documented line by line.

## 1. The application at a glance

ORVENA is a web application with two main programs:

1. **Frontend** (`frontend/`): Next.js App Router, React, and TypeScript. It renders pages, collects input, manages the signed-in browser session, and calls the API.
2. **Backend** (`backend/`): FastAPI and Python. It validates requests, checks authentication, runs business logic, reads and writes database records, and connects to file storage and optional AI providers.

The backend uses SQLAlchemy models for PostgreSQL/Supabase data, Pydantic schemas for API input/output, and Alembic migrations to evolve the database. AI-assisted operations have deterministic/statistical code in several places so the application can still produce results when a model provider is unavailable.

```text
Browser page/component
  -> frontend/src/lib/api/* or api-client.ts
  -> HTTP request to /api/v1/...
  -> FastAPI endpoint
  -> authentication + request schema
  -> service / matching / scoring code
  -> SQLAlchemy model and database, file storage, or optional LLM
  -> JSON response back to the page
```

## 2. Repository map

```text
ORVENA/
├── frontend/             Next.js user interface
├── backend/              FastAPI API and career/resume intelligence
├── docs/                 System, API, database, AI, deployment, and security notes
├── docker-compose.yml    Local container orchestration configuration
├── README.md             Project overview and setup notes
├── PROJECT_CODE_GUIDE.md This guide
├── TESTING_INSTRUCTIONS.md Manual feature-testing checklist
├── E2E_TEST_PLAN.md      End-to-end scenarios
└── SUPABASE_BUCKET_SETUP.md Resume storage bucket setup notes
```

Other root documentation includes `PROJECT_REPORT_COMPREHENSIVE.md`. The backend and frontend also have their own README files and feature/design notes under their `docs/` folders. Some older project documents describe earlier implementation plans; when they disagree with source code, use the current source and API behavior as the authority.

## 3. Frontend (`frontend/`)

### Configuration and project files

| File | Purpose |
| --- | --- |
| `package.json` | Frontend dependencies and commands such as `dev`, `build`, `start`, `lint`, `type-check`, and `test`. |
| `package-lock.json` | Locks the npm dependency versions for repeatable installs. Do not edit it by hand. |
| `next.config.js` | Next.js configuration. |
| `tsconfig.json` | TypeScript compiler settings and path aliases. |
| `tailwind.config.ts` | Tailwind theme, colors, and content scanning configuration. |
| `postcss.config.js` | CSS processing configuration used by Tailwind. |
| `next-env.d.ts` | Next.js-generated TypeScript declarations. |
| `test-auth-flow.html` | A standalone local HTML aid for checking an authentication flow; it is not a Next.js page. |

Runtime configuration is supplied through local environment files (for example `.env.local`). These files contain credentials and are not committed. `NEXT_PUBLIC_API_URL` determines the API base URL used by the browser; public Supabase settings initialize frontend authentication.

### App Router pages (`frontend/src/app/`)

Next.js maps folders and `page.tsx` files to URL routes. Pages are the screen-level components; feature-specific API functions live under `src/lib/api/`.

| Route / file | What it renders or does |
| --- | --- |
| `/` — `page.tsx` | Public landing page and sign-up entry point. |
| Root `layout.tsx` | Shared HTML document, font, metadata, and global CSS for all routes. |
| `globals.css` | Global styles, Tailwind directives, and shared CSS tokens/base styles. |
| `/auth/login` — `auth/login/page.tsx` | Login form and Supabase sign-in flow. |
| `/auth/register` — `auth/register/page.tsx` | Account registration form and Supabase sign-up flow. |
| `/dashboard` — `dashboard/page.tsx` | Authenticated landing page with shortcuts to discovery, resume analysis, and jobs. It is wrapped in `AuthGuard` and `AppLayout`. |
| `/career/discovery` — `career/discovery/page.tsx` | Career questionnaire. It creates or resumes a session, saves answers, and provides a path to results/recommendations. |
| `/career/results/[sessionId]` — `career/results/[sessionId]/page.tsx` | Loads a discovery session and its analysis using the route's session ID, then displays the saved responses and next actions. |
| `/career/recommendations` — `career/recommendations/page.tsx` | Displays career recommendations and related fit information returned by the API. |
| `/resume` — `resume/page.tsx` | Resume upload, list, extraction/analysis entry points, and resume status. |
| `/resume/[resumeId]` — `resume/[resumeId]/page.tsx` | Resume-specific view selected by resume ID. |
| `/jobs` — `jobs/page.tsx` | Job matching page that renders matches and match details from career/resume evidence. |
| `/dashboard/jobs` — `dashboard/jobs/page.tsx` | A separate job-page/placeholder reachable from the dashboard. |
| `/roadmap` — `roadmap/page.tsx` | Loads and displays a career roadmap and milestone state. |
| `/progress` — `progress/page.tsx` | Progress and activity summary. |
| `/settings` — `settings/page.tsx` | Account/application settings UI. |
| `/help` — `help/page.tsx` | Help content, FAQs, and guides. |
| `/profile` and `/profile/edit` | Temporarily redirect to `/dashboard`; profile editing is hidden from the product UI. These route files still exist so saved links do not land on a missing page. |

### Shared UI (`frontend/src/components/`)

| Path | Responsibility |
| --- | --- |
| `components/layout/AppLayout.tsx` | Authenticated application shell, combining the sidebar, header, and page content. |
| `components/layout/Header.tsx` | Top bar with mobile menu, search field, notifications, account menu, settings, and sign-out action. |
| `components/layout/Sidebar.tsx` | Main desktop navigation and collapse behavior. |
| `components/layout/MobileDrawer.tsx` | Small-screen navigation drawer. |
| `components/layout/index.ts` | Barrel exports for layout components. |
| `components/auth/AuthGuard.tsx` | Checks authentication before rendering protected content and redirects unauthenticated visitors. |
| `components/shared/LoadingSpinner.tsx` | Common loading indicator. |
| `components/shared/ErrorState.tsx` | Reusable error presentation. |
| `components/shared/EmptyState.tsx` | Reusable no-data presentation. |
| `components/shared/ComingSoon.tsx` | Placeholder view for unfinished features. |
| `components/ui/` | Reusable primitives: alert, badge, button, card, dropdown, input, label, progress, separator, switch, tabs, and textarea. These components centralize consistent styling and interaction behavior. |
| `components/brand/PathfinderVisual.tsx` | Brand/feature illustration used by the interface. |
| `components/design-system/ColorPalette.tsx` | UI/design reference component for the color palette. |

### Frontend hooks, types, and API utilities

| File | Responsibility |
| --- | --- |
| `src/hooks/useAuth.ts` | React hook exposing the current authentication user and sign-in/sign-out related state/actions. |
| `src/types/index.ts` | Shared TypeScript shapes for data returned by the API, including student, resume, career, and related records. |
| `src/lib/supabase.ts` | Creates/configures the browser Supabase client. |
| `src/lib/auth.ts` | Authentication helpers, including retrieving the active access token for API calls. |
| `src/lib/api-client.ts` | Shared HTTP client. Adds the access token, sends JSON or multipart uploads, parses responses, and converts non-success responses into `APIError`. |
| `src/lib/api/career.ts` | Typed functions for career discovery sessions, answers, analysis, recommendations, and roadmap API calls. |
| `src/lib/api/resume.ts` | Typed functions for resume upload, retrieval, extraction, and analysis. |
| `src/lib/api/student.ts` | Typed functions for student/account-profile API operations. The profile screen is hidden, but these data functions remain available to code that needs account data. |
| `src/lib/utils.ts` | Shared frontend utilities, including class-name composition helpers. |

### Frontend commands

Run commands from `frontend/`:

```powershell
npm run dev        # Local Next.js server, usually http://localhost:3000
npm run type-check # TypeScript validation
npm run lint       # Next.js ESLint checks
npm run build      # Production build
npm test           # Vitest tests
```

## 4. Backend (`backend/`)

### Application setup and API routing

| File/path | Responsibility |
| --- | --- |
| `app/main.py` | FastAPI application entry point. Configures logging, lifespan/startup validation, CORS, middleware, exception handlers, health/root routes, and the versioned API router. |
| `app/api/v1/router.py` | Collects endpoint routers and mounts them under the configured `/api/v1` prefix. Currently includes auth, student, career, resumes, jobs, system, and ping routes. |
| `app/api/dependencies.py` | Shared FastAPI dependencies, including database session access and current authenticated user ID. |
| `app/api/v1/endpoints/auth.py` | Authentication-related API routes and account synchronization with the identity provider. |
| `app/api/v1/endpoints/student.py` | Student/student-profile routes. |
| `app/api/v1/endpoints/career.py` | Career discovery sessions, answer submission, analysis/recommendations, goals, roadmaps, and milestone operations. |
| `app/api/v1/endpoints/resume.py` | Resume upload, extraction, retrieval, and analysis routes. |
| `app/api/v1/endpoints/jobs.py` | Job recommendations and matching routes. |
| `app/api/v1/endpoints/system.py` | Health/monitoring/system information endpoints. |

An endpoint is the HTTP boundary: it validates input, obtains the authenticated user and database session via dependencies, calls a service, and returns a schema-shaped response. Domain logic should generally live in services or intelligence modules, rather than in the endpoint itself.

### Core infrastructure (`backend/app/core/`)

| File | Responsibility |
| --- | --- |
| `config.py` | Reads and validates environment-based settings such as database URL, Supabase keys, CORS origins, file size, and AI-provider configuration. |
| `security.py` | Authentication/token and security helpers. |
| `middleware.py` | Request ID/logging middleware and standardized exception response handlers. |
| `exceptions.py` | Domain exception types used to represent expected application errors. |
| `error_handlers.py` | Error translation utilities/handlers shared by the application. |
| `logging.py` | Logging setup and logger configuration. |

### Database (`backend/app/db/`)

| File/path | Responsibility |
| --- | --- |
| `db/base.py` | SQLAlchemy declarative base and shared model metadata/mixins. |
| `db/session.py` | Async database engine, session factory, request-scoped session dependency support, and development initialization helpers. |
| `db/models/user.py` | Application user record. |
| `db/models/student.py` | Student profile, education, skills, and other student background records. |
| `db/models/career.py` | Career roles, discovery sessions/responses, recommendations, goals, roadmaps, and milestones. |
| `db/models/resume.py` | Resume metadata, extracted content, and analysis/review records. |
| `db/models/job.py` | Job opportunity and matching-related records. |
| `db/models/interview.py` | Interview preparation domain records. |
| `db/models/intelligence.py` | Additional normalized career/resume intelligence records used by the analysis modules. |
| `db/models/__init__.py` | Model exports/import registration so metadata and other modules can find the model classes. |

Database table structure is changed through `backend/migrations/`. `migrations/env.py` configures Alembic; `migrations/versions/` contains ordered schema changes. `migrations/script.py.mako` is the template Alembic uses when creating migrations. Prefer migrations for schema changes rather than editing a live database manually.

### API schemas (`backend/app/schemas/`)

Pydantic schemas define accepted request fields and the shape of serialized responses. They keep the HTTP contract separate from SQLAlchemy's database representation.

| File | Main data domain |
| --- | --- |
| `schemas/auth.py` | Authentication/account request and response data. |
| `schemas/student.py` | Student information and student profile request/response data. |
| `schemas/career.py` | Discovery session/answer, analysis, recommendation, goal, roadmap, and milestone data. |
| `schemas/resume.py` | Resume upload, extracted resume, and analysis response data. |

### Business services (`backend/app/services/`)

| File/path | Responsibility |
| --- | --- |
| `auth_service.py` | Application-side user and student-profile creation/retrieval supporting authenticated accounts. |
| `student_service.py` | Student profile and associated educational/skill data operations. |
| `career_discovery_service.py` | Creates/loads discovery sessions, records answers, and derives session-level analysis data. |
| `career_recommendation_service.py` | Generates/retrieves career recommendations and builds roadmaps using stored career evidence, rules, templates, and optional LLM support. |
| `career_signals.py` | Extracts normalized career/skill signals from text and saved user evidence for deterministic matching. |
| `job_matcher.py` | Scores and ranks job roles using available skills, education, experience, answers, and role requirements. |
| `resume_service.py` | Coordinates resume record creation, file storage, extraction, and access. |
| `resume_parser.py` | Parses resume content into text and structured information. |
| `resume_scorer.py` | Rule/statistics-based resume quality scoring and feedback. |
| `resume_analysis_service.py` | Coordinates detailed resume analysis/review, including optional AI analysis. |
| `storage_service.py` | Uploads/downloads files through configured storage (such as Supabase Storage). |
| `ai_fallback_monitor.py` | Records AI-provider and fallback events/statistics for observability. |
| `services/llm/` | Provider abstraction and implementations: `base.py` defines the provider contract; `gemini_provider.py`, `openai_provider.py`, and `nvidia_provider.py` integrate providers; `multi_provider.py` selects/falls through provider options. |

### Career intelligence module (`backend/app/modules/career_intelligence/`)

This area contains focused algorithms and domain knowledge separate from the HTTP layer.

| Path/file | Responsibility |
| --- | --- |
| `types.py` | Shared typed representations for career intelligence inputs/results. |
| `taxonomy/roles.py` | Known career roles and role metadata. |
| `taxonomy/skills.py` | Skill vocabulary and related groupings. |
| `taxonomy/requirements.py` | Role-to-skill/requirement definitions. |
| `classification/classifier.py` | Classifies evidence toward likely career paths. |
| `classification/role_matcher.py` | Scores similarity between a person's evidence and candidate roles. |
| `evidence/evidence_collector.py` | Collects evidence from available profile, resume, and career-discovery content. |
| `evidence/skill_assessor.py` | Estimates skill evidence/proficiency from that content. |
| `matching/candidate_matcher.py` | Matches a candidate's evidence to roles and computes fit-related outputs. |
| `roadmaps/roadmap_engine.py` | Builds roadmap phases/milestones using role needs and available evidence. |
| `roadmaps/template_library.py` | Reusable roadmap templates and learning/project guidance. |
| `ai_gateway/gateway.py` | AI gateway entry point and provider orchestration for supported operations. |
| `ai_gateway/operations.py` | Operation-specific prompt/request/response handling through the gateway. |
| `ai_gateway/README.md` | Design notes for the AI gateway. |

### Resume intelligence module (`backend/app/modules/resume_intelligence/`)

| Path/file | Responsibility |
| --- | --- |
| `extraction/text_extractor.py` | Reads document bytes and extracts plain text from supported resume formats. |
| `extraction/structured_parser.py` | Turns extracted text into structured contact, education, skills, experience, and project fields. |
| `matching/skill_normalizer.py` | Normalizes synonymous skill terms into consistent labels for scoring/matching. |
| `matching/role_matcher.py` | Compares resume skills/evidence against target-role expectations. |

### Tests, diagnostics, and operational files

| Path | Responsibility |
| --- | --- |
| `backend/tests/` | Focused automated tests for parsing, extraction, skill normalization/assessment, role matching, career classification/signals, roadmap generation, AI gateway behavior, and statistical fallbacks. |
| `backend/test_*.py` and diagnostic scripts | Manual/integration probes used during development. These are not all part of the normal automated test suite. Read each script before running it because some contact configured services. |
| `backend/requirements.txt` | Runtime Python dependencies. |
| `backend/requirements-dev.txt` | Development/test dependencies. |
| `backend/pyproject.toml` | Python tooling and project configuration. |
| `backend/Dockerfile` | Instructions for packaging the API as a container image. |
| `backend/run_migration.py` | Convenience helper for running database migrations. |
| `backend/migrations/` | Versioned PostgreSQL schema history. |
| `backend/docs/` | Backend phase notes and reports. |
| `docker-compose.yml` | Multi-service local/container configuration at the repository root. |

Run backend commands from `backend/` with the virtual environment activated:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest
```

The interactive API reference is normally available at `http://localhost:8000/docs` when API docs are enabled in configuration.

## 5. How the main user flows work

### Sign-in

1. The login/register page calls Supabase Auth through frontend auth helpers.
2. `useAuth` exposes the active user/session to the UI; `AuthGuard` protects application pages.
3. Frontend API requests retrieve the session access token and send it as a Bearer token.
4. Backend dependencies validate the token and expose the current user ID to endpoint handlers.

### Career discovery and recommendations

1. The discovery page asks the career API for the user's existing sessions or creates a new one.
2. Each answer is posted to a career endpoint and persisted as a response associated with the session.
3. The results/recommendations pages load saved sessions and request analysis/recommendations.
4. Backend services combine saved answers with resume/profile evidence when available.
5. Career intelligence classification/matching produces likely roles and supporting evidence. AI can enrich results when configured; deterministic matching is available as the fallback path.

### Resume upload and scoring

1. The resume page sends a multipart upload through `src/lib/api/resume.ts` and `api-client.ts`.
2. The backend endpoint checks the authenticated user, obtains or creates the app-side student record, and calls `resume_service`.
3. `storage_service` stores the original file in the configured storage bucket; the resume record keeps metadata and its storage reference.
4. Extraction/parser code reads the document text and structures fields. Scoring/analysis code evaluates completeness, evidence, skills, and role relevance; optional AI analysis can add feedback.
5. Resume detail/analysis UI fetches the saved record and displays extraction and feedback.

### Roadmaps and progress

1. The roadmap screen requests a roadmap for the signed-in user's stored discovery/recommendation evidence.
2. The career service and roadmap engine choose a target role, identify skill gaps, and build phases/milestones from rules/templates, with optional AI enrichment.
3. The API returns roadmap milestones and resources; the UI renders them and submits milestone completion changes.
4. Progress views summarize persisted milestone/activity state returned by the backend.

## 6. Where to make common changes

| Change needed | Start here |
| --- | --- |
| Add or change a page | `frontend/src/app/<route>/page.tsx` |
| Add a reusable visual/control | `frontend/src/components/` |
| Change API request URL/body handling | `frontend/src/lib/api/` and `frontend/src/lib/api-client.ts` |
| Change frontend authentication behavior | `frontend/src/lib/auth.ts`, `frontend/src/lib/supabase.ts`, `frontend/src/hooks/useAuth.ts`, and `AuthGuard.tsx` |
| Add/change an HTTP endpoint | `backend/app/api/v1/endpoints/`, then register its router in `backend/app/api/v1/router.py` |
| Change request or response shape | `backend/app/schemas/` and its endpoint/client types |
| Change business rules | Relevant `backend/app/services/` module or `backend/app/modules/` algorithm |
| Change a database entity | `backend/app/db/models/`, then add/apply an Alembic migration under `backend/migrations/versions/` |
| Change file storage | `backend/app/services/storage_service.py` and storage configuration in `backend/app/core/config.py` |
| Change AI provider selection | `backend/app/services/llm/` and relevant AI gateway/service call sites |
| Add automated checks | Add a focused test under `backend/tests/` or the frontend test structure, then run the corresponding test command. |

## 7. Notes about what is intentionally not listed

- `node_modules/`, `.next/`, Python virtual environments, caches, and generated build files are produced by tools and should not be edited as application source.
- `.env`, `.env.local`, API keys, database credentials, and Supabase service keys are deployment/local secrets; never paste them into this guide or commit them.
- A filename such as `test_*.py` may be an integration/diagnostic script rather than a unit test. Inspect its content and environment requirements before executing it.
- The profile route currently redirects to the dashboard. Its old page implementation is retained in the source tree temporarily, but it is not an active user-facing profile workflow.
