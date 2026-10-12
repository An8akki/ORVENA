# ORVENA Deployment Guide

## Deployment Architecture

```
GitHub Repository
       ↓
   ┌───────────────────────┐
   │                       │
   ↓                       ↓
Vercel (Frontend)    Render (Backend)
   ↓                       ↓
   └─────→ Supabase ←──────┘
       (Database + Auth + Storage)
```

## Prerequisites

- GitHub account
- Vercel account (free tier)
- Render account (free tier)
- Supabase project
- Domain (optional)
- Gemini API key

## Phase 1: Supabase Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Fill in details:
   - **Name**: orvena-production
   - **Database Password**: Generate strong password
   - **Region**: Choose closest to users
4. Wait for project initialization (~2 minutes)

### 2. Configure Database

```bash
# Get connection details from Supabase dashboard
# Settings → Database → Connection string

# Format:
postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```

### 3. Enable Required Extensions

```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
```

### 4. Setup Storage Bucket

1. Go to Storage in Supabase dashboard
2. Create new bucket: `resumes`
3. Set bucket to **Private**
4. Configure policies:

```sql
-- Allow authenticated users to upload their own files
CREATE POLICY "Users can upload own resumes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Allow users to read their own files
CREATE POLICY "Users can read own resumes"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'resumes' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

### 5. Configure Auth

1. Go to Authentication → Providers
2. Enable Email provider
3. Configure email templates (optional)
4. Set Site URL to your production frontend URL
5. Add redirect URLs:
   - `https://your-domain.com/auth/callback`
   - `http://localhost:3000/auth/callback` (for local dev)

### 6. Get API Keys

Save these from Settings → API:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` (public, safe for frontend)
- `SUPABASE_SERVICE_ROLE_KEY` (secret, backend only)

Also get from Settings → Auth:
- `SUPABASE_JWT_SECRET`

## Phase 2: Backend Deployment (Render)

### 1. Prepare Backend for Deployment

Ensure these files exist in `backend/`:

#### `requirements.txt`
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
asyncpg==0.29.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
google-generativeai==0.3.2
supabase==2.3.0
httpx==0.26.0
python-dotenv==1.0.0
PyMuPDF==1.23.8
python-docx==1.1.0
ruff==0.1.11
pytest==7.4.4
pytest-asyncio==0.23.3
```

#### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Deploy to Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: orvena-api
   - **Region**: Choose closest to Supabase region
   - **Branch**: main
   - **Root Directory**: backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - **Plan**: Free

### 3. Configure Environment Variables

In Render dashboard → Environment:

```bash
# Application
APP_ENV=production
APP_NAME=ORVENA
DEBUG=false
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=[SUPABASE_CONNECTION_STRING]

# Supabase
SUPABASE_URL=[YOUR_SUPABASE_URL]
SUPABASE_ANON_KEY=[YOUR_ANON_KEY]
SUPABASE_SERVICE_ROLE_KEY=[YOUR_SERVICE_ROLE_KEY]
SUPABASE_JWT_SECRET=[YOUR_JWT_SECRET]
SUPABASE_JWT_ISSUER=[YOUR_SUPABASE_URL]/auth/v1
SUPABASE_STORAGE_BUCKET=resumes

# LLM Provider
LLM_PROVIDER=gemini
LLM_API_KEY=[YOUR_GEMINI_API_KEY]
LLM_MODEL=gemini-1.5-flash
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=3
LLM_MAX_TOKENS=2048

# Security
SECRET_KEY=[GENERATE_RANDOM_SECRET]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_ORIGIN=[YOUR_VERCEL_URL]
CORS_ORIGINS=[YOUR_VERCEL_URL]
CORS_ALLOW_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
MAX_UPLOAD_SIZE_MB=5

# Features
ENABLE_API_DOCS=false
ENABLE_CAREER_DISCOVERY=true
ENABLE_RESUME_ANALYSIS=true
ENABLE_JOB_MATCHING=true
ENABLE_INTERVIEW_PREP=true
```

### 4. Deploy

1. Click "Create Web Service"
2. Wait for build and deployment (~5-10 minutes)
3. Test health endpoint: `https://your-app.onrender.com/health`

### 5. Run Database Migrations

```bash
# Option 1: Via Render Shell
# Go to Render dashboard → Shell
alembic upgrade head

# Option 2: Locally against production DB
# (Not recommended for production)
DATABASE_URL=[PRODUCTION_URL] alembic upgrade head
```

## Phase 3: Frontend Deployment (Vercel)

### 1. Prepare Frontend

Ensure these files exist in `frontend/`:

#### `package.json`
```json
{
  "name": "orvena-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.49.3",
    "zod": "^3.22.4",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-toast": "^1.1.5",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.309.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.5",
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3"
  }
}
```

#### `frontend/next.config.js`
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  },
  images: {
    domains: ['your-supabase-url.supabase.co'],
  },
}

module.exports = nextConfig
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3. Configure Environment Variables

In Vercel → Settings → Environment Variables:

```bash
# Public variables (safe to expose)
NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com
NEXT_PUBLIC_SUPABASE_URL=[YOUR_SUPABASE_URL]
NEXT_PUBLIC_SUPABASE_ANON_KEY=[YOUR_ANON_KEY]
```

### 4. Deploy

1. Click "Deploy"
2. Wait for build (~3-5 minutes)
3. Test at your Vercel URL

### 5. Configure Custom Domain (Optional)

1. Go to Vercel → Settings → Domains
2. Add your domain
3. Configure DNS records as shown
4. Wait for SSL certificate provisioning

## Phase 4: Post-Deployment Configuration

### 1. Update CORS Origins

Update backend environment variable:
```bash
CORS_ORIGINS=https://your-vercel-app.vercel.app,https://your-custom-domain.com
FRONTEND_ORIGIN=https://your-vercel-app.vercel.app
```

### 2. Update Supabase Auth URLs

In Supabase → Authentication → URL Configuration:
- **Site URL**: `https://your-vercel-app.vercel.app`
- **Redirect URLs**: Add production URLs

### 3. Verify Integrations

Test these workflows:
- [ ] User registration
- [ ] User login
- [ ] Profile update
- [ ] Resume upload
- [ ] Resume download
- [ ] Career discovery
- [ ] Job search

## Monitoring and Maintenance

### Health Checks

**Backend Health:**
```bash
curl https://your-app.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "version": "1.0.0"
}
```

### Logging

**Render Logs:**
- Dashboard → Logs tab
- View real-time and historical logs

**Vercel Logs:**
- Dashboard → Functions → Logs
- View serverless function invocations

**Supabase Logs:**
- Dashboard → Database → Logs
- View query performance and errors

### Database Backups

Supabase automatically backs up:
- **Point-in-time recovery**: Last 7 days (paid plans)
- **Daily backups**: Automated (all plans)

**Manual Backup:**
```bash
pg_dump [SUPABASE_CONNECTION_STRING] > backup.sql
```

**Restore from Backup:**
```bash
psql [SUPABASE_CONNECTION_STRING] < backup.sql
```

### Performance Monitoring

**Key Metrics to Track:**
- API response times
- Database query performance
- LLM API latency
- Error rates
- User activity patterns

**Tools:**
- Render: Built-in metrics
- Vercel: Analytics dashboard
- Supabase: Database insights

## Scaling Considerations

### Free Tier Limits

**Vercel Free:**
- 100 GB bandwidth/month
- Unlimited deployments
- No custom domains limit

**Render Free:**
- 750 hours/month
- Services sleep after 15 min inactivity
- 512 MB RAM
- Shared CPU

**Supabase Free:**
- 500 MB database
- 1 GB file storage
- 50,000 monthly active users
- 2 GB bandwidth

### Upgrade Path

When hitting limits:

1. **Backend Performance Issues:**
   - Upgrade Render plan ($7/month)
   - Add database indexes
   - Implement caching

2. **Database Growth:**
   - Upgrade Supabase plan ($25/month)
   - Archive old data
   - Optimize queries

3. **Storage Growth:**
   - Upgrade storage plan
   - Implement file cleanup policies
   - Compress files

## Rollback Procedure

### Backend Rollback

1. Go to Render dashboard
2. Navigate to your service
3. Go to "Events" tab
4. Click "Rollback" on previous successful deploy

### Frontend Rollback

1. Go to Vercel dashboard
2. Navigate to "Deployments"
3. Find previous successful deployment
4. Click "..." → "Promote to Production"

### Database Rollback

```bash
# Downgrade one migration
alembic downgrade -1

# Downgrade to specific version
alembic downgrade [revision_id]
```

## Security Checklist

- [ ] All secrets in environment variables (not in code)
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Database RLS policies active
- [ ] File storage is private
- [ ] JWT validation working
- [ ] API docs disabled in production
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies updated

## Troubleshooting

### Common Issues

**1. Backend Won't Start**
```bash
# Check Render logs
# Verify DATABASE_URL is correct
# Ensure migrations ran successfully
# Check for missing environment variables
```

**2. CORS Errors**
```bash
# Verify CORS_ORIGINS includes frontend URL
# Check FRONTEND_ORIGIN is set
# Ensure credentials are enabled
```

**3. Database Connection Fails**
```bash
# Verify connection string
# Check IP allowlist (Supabase)
# Confirm database is active
# Test connection locally
```

**4. Authentication Not Working**
```bash
# Verify JWT_SECRET matches Supabase
# Check token expiration settings
# Confirm redirect URLs are configured
# Test with Supabase Auth UI
```

**5. File Uploads Fail**
```bash
# Check storage bucket exists
# Verify RLS policies
# Confirm SERVICE_ROLE_KEY is set
# Test file size limits
```

## Continuous Deployment

### Automatic Deploys

Both Vercel and Render auto-deploy on push to main branch.

**Disable auto-deploy:**
- Render: Settings → Disable "Auto-Deploy"
- Vercel: Settings → Git → Disable

### Deployment Workflow

```
Code Push → GitHub
    ↓
Vercel Build (Frontend)
    ↓
Deploy to Production
    ↓
Render Build (Backend)
    ↓
Run Migrations
    ↓
Deploy to Production
```

## Support and Resources

- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**Deployment Version**: 1.0  
**Last Updated**: 2024  
**Status**: Production Ready
