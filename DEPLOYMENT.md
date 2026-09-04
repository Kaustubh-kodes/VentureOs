# VentureOS — Production Deployment Guide

This document outlines the exact production deployment architecture, configuration, and verification steps for VentureOS.

---

## Production Architecture

```
User (Browser)
     │
     ▼
Vercel (Next.js 14 Frontend)
     │
     ▼ HTTPS API
Railway (FastAPI Python Backend)
     │
     ├── Google Gen AI API (gemini-3.5-flash)
     │
     └── Supabase PostgreSQL
            ├── startup_sessions
            ├── agent_outputs (JSONB)
            ├── analysis_events
            ├── evaluation_runs
            └── pgvector (HNSW Cosine Similarity Search)
```

---

## 1. Backend Deployment (Railway)

### Service Configuration
- **Root Directory**: `backend` (or repository root using the root `Procfile`)
- **Builder**: `NIXPACKS` (detected automatically)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Healthcheck Path**: `/health`
- **Healthcheck Timeout**: `120s`

### Required Backend Environment Variables
Configure these in the **Railway Dashboard > Service Settings > Variables**:

| Variable Name | Description | Example / Format |
|---|---|---|
| `ENVIRONMENT` | Deployment environment | `production` |
| `GEMINI_API_KEY` | Google Gemini API Key (**Backend Only**) | `AQ.Ab8...` |
| `GEMINI_MODEL` | Preferred Gemini model | `gemini-3.5-flash` |
| `SUPABASE_URL` | Supabase project URL | `https://your-project.supabase.co` |
| `SUPABASE_KEY` | Supabase service role / anon key (**Backend Only**) | `sb_publishable_...` |
| `CORS_ORIGINS` | Allowed frontend domains (JSON or comma-separated) | `["https://your-ventureos.vercel.app", "http://localhost:3000"]` |
| `FRONTEND_URL` | Optional shorthand for production frontend | `https://frontend-amber-ten-59.vercel.app` |

> [!CAUTION]
> **Never** expose `GEMINI_API_KEY` or `SUPABASE_KEY` to the client. These must exist **only** on the Railway backend service.

---

## 2. Frontend Deployment (Vercel)

🌐 **Live Vercel Production URL:** [`https://frontend-amber-ten-59.vercel.app`](https://frontend-amber-ten-59.vercel.app)

### Project Configuration
- **Root Directory**: `frontend`
- **Framework Preset**: `Next.js`
- **Build Command**: `next build` (or `npm run build`)
- **Output Directory**: `.next`
- **Node Version**: `18.x` or `20.x`

### Required Frontend Environment Variables
Configure in **Vercel Project Settings > Environment Variables**:

| Variable Name | Description | Example / Target |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Public URL of the Railway backend | `https://your-backend.up.railway.app` |

---

## 3. Database Migrations (Supabase)

Before launching production analysis runs, ensure all 5 sequential migrations are applied in your **Supabase SQL Editor**:
1. `001_create_startup_sessions.sql` — Session tables and base schema
2. `002_create_rag_knowledge_base.sql` — Documents, chunks, pgvector extension, and `match_document_chunks` RPC
3. `003_add_multi_agent_support.sql` — Agent outputs schema
4. `004_add_analysis_events_and_durations.sql` — Duration columns and `analysis_events` table
5. `005_evaluation_runs_and_hardening.sql` — `evaluation_runs` table and performance indexes

---

## 4. Production Verification Checklist

1. **Backend Health Check**:
   ```bash
   curl -I https://YOUR-RAILWAY-DOMAIN/health
   # Expected: HTTP 200 OK {"status":"healthy","service":"ventureos-api","version":"0.9.0"}
   ```

2. **Frontend Loading**:
   - Open `https://YOUR-VERCEL-DOMAIN` in browser. Confirm homepage loads with zero console errors.

3. **CORS Validation**:
   - Verify network tab shows successful preflight `OPTIONS` and `GET/POST` requests without CORS blockage.

4. **Live Analysis Run**:
   - Submit a test venture on `/analyse`.
   - Verify that reactive 2-second polling displays agent progress, execution timeline, and durations.
   - Verify that the 20-section report renders completely upon synthesis completion.
   - Confirm session metrics appear on report (duration, agent count, chunks grounded).

5. **History & Navigation**:
   - Open `/history` and verify past sessions appear with investment scores and readiness verdicts.
