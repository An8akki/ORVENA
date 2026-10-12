# ORVENA Testing Guide

## Testing Strategy

ORVENA employs a multi-layered testing approach:

1. **Unit Tests**: Individual functions and classes
2. **Integration Tests**: API endpoints with database
3. **Component Tests**: React components in isolation
4. **End-to-End Tests**: Complete user workflows
5. **Performance Tests**: Response time and load testing
6. **Security Tests**: Auth, authorization, and data protection

## Backend Testing

### Setup

```bash
cd backend

# Install test dependencies
pip install -r requirements-test.txt

# Create test database
createdb orvena_test

# Set test environment
export APP_ENV=test
export DATABASE_URL=postgresql://localhost/orvena_test
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_career_service.py

# Run specific test
pytest tests/test_career_service.py::test_generate_recommendations

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "career"
```

### Test Structure

```
backend/tests/
├── conftest.py                 # Pytest fixtures
├── test_api/
│   ├── test_auth.py
│   ├── test_career.py
│   ├── test_resume.py
│   ├── test_jobs.py
│   └── test_interviews.py
├── test_services/
│   ├── test_career_service.py
│   ├── test_resume_service.py
│   └── test_job_service.py
├── test_repositories/
│   ├── test_student_repo.py
│   ├── test_resume_repo.py
│   └── test_job_repo.py
├── test_integrations/
│   ├── test_llm_provider.py
│   ├── test_storage.py
│   └── test_document_parser.py
└── test_utils/
    └── test_validators.py
```

### Test Fixtures

**conftest.py:**
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.core.config import settings

# In-memory database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def mock_llm_provider():
    return MockLLMProvider()

@pytest.fixture
def test_user(db_session):
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password=get_password_hash("testpass123")
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_student_profile(db_session, test_user):
    profile = StudentProfile(
        user_id=test_user.id,
        full_name="Test Student",
        email="test@example.com",
        graduation_year=2024
    )
    db_session.add(profile)
    db_session.commit()
    return profile

@pytest.fixture
def auth_headers(client, test_user):
    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Unit Test Examples

**test_career_service.py:**
```python
import pytest
from app.services.career_service import CareerService
from app.schemas.career import CareerRecommendationRequest

class TestCareerService:
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(
        self,
        db_session,
        test_student_profile,
        mock_llm_provider
    ):
        # Arrange
        service = CareerService(
            db=db_session,
            llm_provider=mock_llm_provider
        )
        
        request = CareerRecommendationRequest(
            max_recommendations=3
        )
        
        # Act
        recommendations = await service.generate_recommendations(
            student_id=test_student_profile.id,
            request=request
        )
        
        # Assert
        assert len(recommendations) > 0
        assert len(recommendations) <= 3
        assert all(0 <= r.fit_score <= 1 for r in recommendations)
        assert all(len(r.reasoning) > 0 for r in recommendations)
    
    @pytest.mark.asyncio
    async def test_create_roadmap(
        self,
        db_session,
        test_student_profile
    ):
        # Arrange
        service = CareerService(db=db_session)
        career_goal = await service.create_goal(
            student_id=test_student_profile.id,
            title="Become Full-Stack Developer"
        )
        
        # Act
        roadmap = await service.create_roadmap(
            career_goal_id=career_goal.id,
            target_duration_weeks=12
        )
        
        # Assert
        assert roadmap.career_goal_id == career_goal.id
        assert roadmap.target_duration_weeks == 12
        assert len(roadmap.milestones) > 0
```

### Integration Test Examples

**test_api/test_resume.py:**
```python
import pytest
from io import BytesIO

class TestResumeAPI:
    
    def test_upload_resume_success(self, client, auth_headers):
        # Arrange
        pdf_content = b"%PDF-1.4 fake pdf content"
        files = {
            "file": ("resume.pdf", BytesIO(pdf_content), "application/pdf")
        }
        data = {"title": "My Resume"}
        
        # Act
        response = client.post(
            "/api/v1/resumes",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 202
        assert response.json()["status"] == "processing"
        assert "id" in response.json()
    
    def test_upload_invalid_file_type(self, client, auth_headers):
        # Arrange
        files = {
            "file": ("malware.exe", BytesIO(b"content"), "application/exe")
        }
        data = {"title": "Resume"}
        
        # Act
        response = client.post(
            "/api/v1/resumes",
            files=files,
            data=data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 422
        assert "Invalid file type" in response.json()["detail"]
    
    def test_get_resume_unauthorized(self, client):
        # Act
        response = client.get("/api/v1/resumes/some-uuid")
        
        # Assert
        assert response.status_code == 401
    
    def test_get_other_user_resume(self, client, auth_headers, db_session):
        # Arrange - create resume for different user
        other_user = User(email="other@example.com")
        other_profile = StudentProfile(user_id=other_user.id)
        resume = Resume(student_profile_id=other_profile.id)
        db_session.add_all([other_user, other_profile, resume])
        db_session.commit()
        
        # Act
        response = client.get(
            f"/api/v1/resumes/{resume.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 403
```

### Performance Tests

```python
import pytest
import time

class TestPerformance:
    
    @pytest.mark.performance
    def test_career_recommendations_latency(
        self,
        client,
        auth_headers,
        test_student_profile
    ):
        # Act
        start = time.time()
        response = client.post(
            "/api/v1/career/recommendations",
            json={"max_recommendations": 5},
            headers=auth_headers
        )
        duration = time.time() - start
        
        # Assert
        assert response.status_code == 200
        assert duration < 10.0  # Should complete in under 10 seconds
    
    @pytest.mark.performance
    def test_database_query_performance(self, db_session):
        # Arrange - create test data
        for i in range(100):
            job = JobListing(
                title=f"Job {i}",
                company_name=f"Company {i}",
                description="Description"
            )
            db_session.add(job)
        db_session.commit()
        
        # Act
        start = time.time()
        jobs = db_session.query(JobListing)\
            .filter(JobListing.status == "active")\
            .limit(20)\
            .all()
        duration = time.time() - start
        
        # Assert
        assert len(jobs) == 20
        assert duration < 0.1  # Query should be fast
```

## Frontend Testing

### Setup

```bash
cd frontend

# Install dependencies
npm install

# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest @vitejs/plugin-react jsdom
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- src/components/ui/Button.test.tsx
```

### Test Structure

```
frontend/src/
├── __tests__/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   └── utils/
├── components/
│   └── ui/
│       ├── Button.tsx
│       └── Button.test.tsx
└── features/
    └── career/
        ├── components/
        │   ├── CareerCard.tsx
        │   └── CareerCard.test.tsx
        └── hooks/
            ├── useCareerRecommendations.ts
            └── useCareerRecommendations.test.ts
```

### Component Test Examples

**Button.test.tsx:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from './Button'

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
  
  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>)
    const button = screen.getByText('Click me')
    
    expect(button).toBeDisabled()
  })
  
  it('shows loading state', () => {
    render(<Button loading>Click me</Button>)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })
})
```

**CareerCard.test.tsx:**
```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { CareerCard } from './CareerCard'

describe('CareerCard', () => {
  const mockCareer = {
    id: '123',
    name: 'Full-Stack Developer',
    category: 'Software Engineering',
    fit_score: 0.85,
    strengths: ['Strong coding skills', 'Project experience'],
    gaps: ['Limited system design experience']
  }
  
  it('renders career information', () => {
    render(<CareerCard career={mockCareer} />)
    
    expect(screen.getByText('Full-Stack Developer')).toBeInTheDocument()
    expect(screen.getByText('Software Engineering')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
  })
  
  it('displays strengths and gaps', () => {
    render(<CareerCard career={mockCareer} />)
    
    expect(screen.getByText('Strong coding skills')).toBeInTheDocument()
    expect(screen.getByText('Limited system design experience')).toBeInTheDocument()
  })
})
```

### Hook Test Examples

**useCareerRecommendations.test.ts:**
```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { useCareerRecommendations } from './useCareerRecommendations'

describe('useCareerRecommendations', () => {
  it('fetches recommendations successfully', async () => {
    const mockRecommendations = [
      { id: '1', name: 'Developer', fit_score: 0.85 },
      { id: '2', name: 'Designer', fit_score: 0.75 }
    ]
    
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ recommendations: mockRecommendations })
      })
    )
    
    const { result } = renderHook(() => useCareerRecommendations())
    
    await waitFor(() => {
      expect(result.current.recommendations).toHaveLength(2)
      expect(result.current.loading).toBe(false)
    })
  })
  
  it('handles error state', async () => {
    global.fetch = vi.fn(() => Promise.reject(new Error('API Error')))
    
    const { result } = renderHook(() => useCareerRecommendations())
    
    await waitFor(() => {
      expect(result.current.error).toBeTruthy()
      expect(result.current.loading).toBe(false)
    })
  })
})
```

## End-to-End Tests

### Setup Playwright

```bash
cd frontend

# Install Playwright
npm install --save-dev @playwright/test

# Install browsers
npx playwright install
```

### E2E Test Structure

```
frontend/e2e/
├── auth/
│   ├── login.spec.ts
│   └── registration.spec.ts
├── career/
│   ├── discovery.spec.ts
│   └── recommendations.spec.ts
├── resume/
│   ├── upload.spec.ts
│   └── analysis.spec.ts
└── jobs/
    ├── search.spec.ts
    └── application.spec.ts
```

### E2E Test Examples

**career/discovery.spec.ts:**
```typescript
import { test, expect } from '@playwright/test'

test.describe('Career Discovery', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000')
    
    // Login
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="password"]', 'testpass123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
  })
  
  test('complete career discovery flow', async ({ page }) => {
    // Start discovery
    await page.click('text=Start Career Discovery')
    await expect(page).toHaveURL('/career/discovery')
    
    // Answer first question
    await page.fill('textarea[name="response"]', 'I enjoy building web applications')
    await page.click('text=Next')
    
    // Answer second question
    await page.fill('textarea[name="response"]', 'Python and JavaScript')
    await page.click('text=Next')
    
    // Continue through more questions
    for (let i = 0; i < 5; i++) {
      await page.fill('textarea[name="response"]', `Response ${i}`)
      await page.click('text=Next')
    }
    
    // Complete discovery
    await page.click('text=Generate Recommendations')
    
    // Verify recommendations appear
    await expect(page.locator('.career-card')).toHaveCount(3, {
      timeout: 15000
    })
    
    // Select a recommendation
    await page.click('.career-card:first-child button:has-text("View Details")')
    
    // Verify career details page
    await expect(page.locator('h1')).toContainText('Full-Stack Developer')
    await expect(page.locator('.fit-score')).toBeVisible()
  })
  
  test('save and resume discovery session', async ({ page }) => {
    await page.click('text=Start Career Discovery')
    
    // Answer some questions
    await page.fill('textarea[name="response"]', 'First response')
    await page.click('text=Next')
    
    // Save progress
    await page.click('text=Save Progress')
    await expect(page.locator('text=Progress saved')).toBeVisible()
    
    // Navigate away
    await page.goto('/dashboard')
    
    // Return to discovery
    await page.click('text=Resume Discovery')
    
    // Verify session resumed
    await expect(page.locator('text=Continue where you left off')).toBeVisible()
  })
})
```

**resume/upload.spec.ts:**
```typescript
import { test, expect } from '@playwright/test'
import path from 'path'

test.describe('Resume Upload', () => {
  test('upload and analyze resume', async ({ page }) => {
    await page.goto('http://localhost:3000/resumes/upload')
    
    // Upload file
    const filePath = path.join(__dirname, 'fixtures', 'sample-resume.pdf')
    await page.setInputFiles('input[type="file"]', filePath)
    
    // Fill title
    await page.fill('[name="title"]', 'Software Engineer Resume')
    
    // Submit
    await page.click('button:has-text("Upload")')
    
    // Wait for processing
    await expect(page.locator('text=Processing...')).toBeVisible()
    await expect(page.locator('text=Processing...')).not.toBeVisible({
      timeout: 30000
    })
    
    // Verify extraction
    await expect(page.locator('text=Confirm Extracted Information')).toBeVisible()
    
    // Confirm extraction
    await page.click('button:has-text("Confirm")')
    
    // Request analysis
    await page.click('button:has-text("Analyze Resume")')
    
    // Verify analysis results
    await expect(page.locator('.resume-score')).toBeVisible({ timeout: 20000 })
    await expect(page.locator('.finding-card')).toHaveCount(greaterThan(0))
  })
})
```

## Security Tests

```python
class TestSecurity:
    
    def test_sql_injection_prevention(self, client, auth_headers):
        # Attempt SQL injection in search
        response = client.get(
            "/api/v1/jobs?title=' OR '1'='1",
            headers=auth_headers
        )
        assert response.status_code in [200, 422]
        # Should not return all jobs or cause error
    
    def test_xss_prevention(self, client, auth_headers):
        # Attempt XSS in profile update
        response = client.patch(
            "/api/v1/profile",
            json={"bio": "<script>alert('xss')</script>"},
            headers=auth_headers
        )
        assert response.status_code == 200
        # Script tags should be escaped or stripped
    
    def test_authentication_required(self, client):
        # Test protected endpoints without auth
        endpoints = [
            "/api/v1/profile",
            "/api/v1/resumes",
            "/api/v1/career/recommendations"
        ]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
    
    def test_ownership_enforcement(self, client, auth_headers, db_session):
        # Create resource owned by different user
        other_user = User(email="other@example.com")
        other_profile = StudentProfile(user_id=other_user.id)
        resume = Resume(student_profile_id=other_profile.id)
        db_session.add_all([other_user, other_profile, resume])
        db_session.commit()
        
        # Attempt to access other user's resource
        response = client.get(
            f"/api/v1/resumes/{resume.id}",
            headers=auth_headers
        )
        assert response.status_code == 403
```

## Test Coverage Requirements

### Minimum Coverage Targets

- **Backend Overall**: 80%
- **Business Logic (Services)**: 90%
- **API Routes**: 85%
- **Critical Paths**: 100%

### Measuring Coverage

```bash
# Backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
npm run test:coverage
open coverage/index.html
```

## Continuous Integration

### GitHub Actions Workflow

**.github/workflows/test.yml:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm test
      
      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright test
```

## Pre-Deployment Testing

### Smoke Tests

Run these manually before deploying:

- [ ] User can register
- [ ] User can login
- [ ] User can update profile
- [ ] User can start career discovery
- [ ] User can upload resume
- [ ] User can search jobs
- [ ] User can save a job
- [ ] User can track an application
- [ ] All critical API endpoints respond
- [ ] Database migrations work
- [ ] File uploads work
- [ ] AI integrations work

---

**Testing Version**: 1.0  
**Last Updated**: 2024  
**Coverage Target**: 80%+
