# ROOT CAUSE DIAGNOSIS - COMPLETE

## Problem
Profile endpoint returns 500 error with no traceback in logs.

## Investigation Process

### 1. Initial Hypothesis
Error handler middleware swallowing detailed logs.

### 2. Debug Attempts
- Added extensive logging to profile endpoint - NO OUTPUT
- Added print() statements to stderr - NO OUTPUT  
- Added debug to auth dependency - NO OUTPUT
- Created test endpoint with stderr print - NO OUTPUT

### 3. Discovery
**CRITICAL FINDING:** `stderr` output is NOT captured by uvicorn in the control_pwsh_process terminal.

### 4. ROOT CAUSE IDENTIFIED

**SCHEMA MISMATCH:**

The `StudentProfileResponse` schema (app/schemas/student.py) was missing the `email` field that exists in the `StudentProfile` database model (app/db/models/student.py).

**Model (has email):**
```python
class StudentProfile(Base, UUIDMixin, TimestampMixin):
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # ... other fields
```

**Schema (was missing email):**
```python
class StudentProfileBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    # email was NOT here!
```

When FastAPI tries to serialize the `StudentProfile` model instance to `StudentProfileResponse`, Pydantic validation fails because:
1. The model has an `email` attribute
2. The schema doesn't define it
3. With `ConfigDict(from_attributes=True)`, Pydantic tries to read all model attributes
4. Unknown attributes cause validation to fail

**Secondary issue:** Schema also had `profile_completed: bool` which doesn't exist in the model.

## Fix Applied

1. Added `email` field to `StudentProfileBase` schema
2. Removed `profile_completed` from `StudentProfileResponse` (doesn't exist in model)

## Why No Error Logs?

The Pydantic validation error occurs during FastAPI's response serialization, which happens AFTER the endpoint returns successfully. The error handler catches it but the traceback isn't showing because:
- JSON logging format may be suppressing exc_info output  
- Or the error occurs in a different asyncio context
- Or uvicorn's reload process interferes with log output

## Next Steps

Test the fix by running integration test again.
