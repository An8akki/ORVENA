# ORVENA Backend

FastAPI-based backend API for the ORVENA career intelligence platform.

## Technology Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Supabase Auth + JWT
- **AI Provider**: Gemini API (configurable)
- **Testing**: pytest + pytest-asyncio

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── config.py          # Settings and configuration
│   ├── logging.py         # Logging setup
│   ├── security.py        # Auth and token handling
│   ├── exceptions.py      # Custom exceptions
│   └── middleware.py      # Request/response middleware
├── api/
│   ├── dependencies.py    # Dependency injection
│   └── v1/
│       ├── router.py      # Main API router
│       └── endpoints/     # API endpoints (to be implemented)
├── db/
│   ├── base.py            # SQLAlchemy base and mixins
│   ├── session.py         # Database session management
│   └── models/            # SQLAlchemy models (to be implemented)
├── schemas/               # Pydantic schemas (to be implemented)
├── repositories/          # Data access layer (to be implemented)
├── services/              # Business logic (to be implemented)
├── modules/               # Feature modules (to be implemented)
├── integrations/          # External services (to be implemented)
└── utils/                 # Utilities (to be implemented)

migrations/                # Alembic migrations
tests/                     # Test suite
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`
- `LLM_API_KEY`: Gemini API key
- `SECRET_KEY`: Application secret key

### 3. Run Database Migrations

```bash
# Create a new migration (after model changes)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current
```

### 4. Run Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

API will be available at:
- http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Available Scripts

```bash
# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Type checking
mypy app

# Code formatting and linting
ruff check app
ruff format app
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user table"

# Create empty migration
alembic revision -m "Custom changes"
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade by number of revisions
alembic upgrade +2

# Downgrade by number of revisions
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123

# Show current version
alembic current

# Show migration history
alembic history
```

## Error Handling

The application uses a hierarchical exception system:

- `OrvenaDomainError`: Base for all domain errors
- `NotFoundError`: Resource not found (404)
- `PermissionDeniedError`: Access denied (403)
- `UnauthorizedError`: Authentication required (401)
- `ValidationDomainError`: Business validation failed (422)
- `ExternalServiceError`: Third-party service error (502)
- `RateLimitError`: Rate limit exceeded (429)

All errors return standardized JSON responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "request_id": "uuid",
    "details": {}
  }
}
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_api/test_auth.py

# Run specific test
pytest tests/test_api/test_auth.py::test_login_success

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf
```

## Docker

```bash
# Build image
docker build -t orvena-backend .

# Run container
docker run -p 8000:8000 --env-file .env orvena-backend

# Using docker-compose (from project root)
docker-compose up backend
```

## Code Quality

### Linting

```bash
# Check code
ruff check app

# Auto-fix issues
ruff check --fix app

# Format code
ruff format app
```

### Type Checking

```bash
# Run mypy
mypy app
```

## Security

- All secrets must be in environment variables
- Never commit `.env` files
- JWT tokens validated using Supabase JWT secret
- Password hashing using bcrypt
- Input validation via Pydantic
- SQL injection prevention via SQLAlchemy ORM
- CORS restricted to configured origins

## Next Steps

- [ ] Implement database models (Phase 2)
- [ ] Implement authentication endpoints
- [ ] Create student profile management
- [ ] Build career intelligence module
- [ ] Build resume intelligence module
- [ ] Build job intelligence module
- [ ] Build interview intelligence module
- [ ] Add comprehensive tests
- [ ] Implement LLM provider integration
- [ ] Setup CI/CD pipeline

## Development Guidelines

1. **Models**: Define in `app/db/models/`
2. **Schemas**: Create Pydantic schemas in `app/schemas/`
3. **Repositories**: Data access in `app/repositories/`
4. **Services**: Business logic in `app/services/`
5. **Endpoints**: API routes in `app/api/v1/endpoints/`
6. **Tests**: Mirror app structure in `tests/`
7. **Migrations**: Use Alembic for all schema changes
8. **Type Hints**: Use type annotations everywhere
9. **Documentation**: Document all public functions

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
python -c "from app.db.session import engine; print(engine)"

# Check PostgreSQL is running
pg_isready -h localhost -p 5432
```

### Migration Issues

```bash
# Reset migrations (development only!)
alembic downgrade base
alembic upgrade head

# Stamp database without running migrations
alembic stamp head
```

### Import Errors

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

---

Built with FastAPI and Python 3.11+
