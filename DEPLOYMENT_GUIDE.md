# 🚀 ORVENA Zero-Cost & Zero-Headache Deployment Guide

This guide deploys ORVENA on the **100% free tier** using the industry-standard stack for Next.js + FastAPI:
- **Frontend:** [Vercel](https://vercel.com) (Free, native Next.js hosting, automated SSL, global CDN)
- **Backend:** [Render](https://render.com) (Free Web Service, native Python FastAPI, automated HTTPS)
- **Database:** [Supabase](https://supabase.com) (Free PostgreSQL, already connected and migrated)

---

## Part 1: Deploy Backend to Render (5 Minutes)

1. **Push your code to GitHub:**
   ```powershell
   git add .
   git commit -m "feat: complete Launchpad and Guide with deployment config"
   git push origin main
   ```

2. **Create Web Service on Render:**
   - Go to [dashboard.render.com](https://dashboard.render.com) and log in with GitHub.
   - Click **New +** $\to$ **Web Service**.
   - Select your repository (`ORVENA`).
   - Fill in the basic settings:
     - **Name:** `orvena-backend`
     - **Root Directory:** `backend`
     - **Runtime:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `alembic upgrade 20261022_launchpad_guide && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Instance Type:** `Free`

3. **Add Environment Variables on Render:**
   Under the **Environment Variables** section, copy these exact values from your local `backend/.env`:
   - `DATABASE_URL`: `postgresql+asyncpg://postgres.awysaiowibawcsmngoch:Orvena%40mycareer_profile@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres`
   - `SUPABASE_URL`: `https://awysaiowibawcsmngoch.supabase.co`
   - `SUPABASE_ANON_KEY`: *(from backend/.env)*
   - `SUPABASE_SERVICE_ROLE_KEY`: *(from backend/.env)*
   - `SUPABASE_JWT_SECRET`: *(from backend/.env)*
   - `SUPABASE_JWT_ISSUER`: `https://awysaiowibawcsmngoch.supabase.co/auth/v1`
   - `LLM_PROVIDER`: `gemini`
   - `LLM_API_KEY`: *(from backend/.env)*
   - `SECRET_KEY`: `orvena-production-secret-key-super-secure-jwt-2026`
   - `APP_ENV`: `production`
   - `DEBUG`: `false`

4. Click **Create Web Service**.
   - Render will build and launch your backend at `https://orvena-backend.onrender.com` (or similar).
   - Test it by visiting: `https://<your-render-url>/health` $\to$ returns `{"status":"healthy"}`.

---

## Part 2: Deploy Frontend to Vercel (3 Minutes)

1. **Go to Vercel:**
   - Visit [vercel.com](https://vercel.com) and sign in with GitHub.
   - Click **Add New...** $\to$ **Project**.
   - Import your `ORVENA` repository.

2. **Configure Project:**
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Click **Edit** and select **`frontend`**.

3. **Add Environment Variables on Vercel:**
   Add these 3 environment variables:
   - `NEXT_PUBLIC_API_URL`: `https://<your-render-backend-url>` (e.g. `https://orvena-backend.onrender.com`)
   - `NEXT_PUBLIC_SUPABASE_URL`: `https://awysaiowibawcsmngoch.supabase.co`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: *(your Supabase anon key)*

4. Click **Deploy**.
   - Vercel will build and launch your frontend in under 60 seconds!
   - You will get a live URL (e.g. `https://orvena.vercel.app`).

5. **Configure Supabase authentication redirects:**
   - In Supabase, open **Authentication → URL Configuration**.
   - Set **Site URL** to the exact Vercel production URL.
   - Add `https://<your-vercel-domain>/auth/login?confirmed=1` to **Redirect URLs**.
   - Keep `http://localhost:3000/auth/login?confirmed=1` only for local development.
   - Redeploy after changing Vercel environment variables. Never copy `.env.local` into the Vercel project.

---

## ✅ Post-Deployment Verification

1. Open your live Vercel URL.
2. Sign in with your existing account (`anu8akkirj`).
3. Click **Project Launchpad** on the sidebar $\to$ verify your detected resume projects appear.
4. Click **Orvena Guide** (bottom right) $\to$ type `"hi"` to see the personalized greeting.
5. All database operations, evaluations, and roadmap milestones are live on production!

If a deployed page tries `localhost:8000`, `NEXT_PUBLIC_API_URL` is missing from the
Vercel **Production** environment. Add it and redeploy; the application now uses the
Render service URL as a safe production fallback, but the environment variable remains
the authoritative setting for custom Render domains.
