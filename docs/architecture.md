# VentureOS Architecture

## Phase 1+2 Architecture (Current)

```
Browser (Next.js)
       |
       | REST API
       v
FastAPI Backend
  GET /
  GET /health
```

## Target Architecture (Phase 7+)

```
Browser (Next.js)
       |
       | REST + WebSocket
       v
FastAPI Backend
       |
 ------+------
|             |
Orchestrator  Supabase
Agent         (PostgreSQL + pgvector)
|
+-- CEO Agent (Gemini)
+-- Market Agent (Gemini)
+-- Product Agent (Gemini)
+-- Marketing Agent (Gemini)
+-- Finance Agent (Gemini)
+-- Tech Agent (Gemini)
+-- Skeptic Agent (Gemini)
+-- Investment Agent (Gemini)
       |
Final Strategy Agent
       |
Venture Report
```
