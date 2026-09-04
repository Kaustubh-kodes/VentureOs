# VentureOS — Autonomous Multi-Agent Venture Studio & Startup Intelligence Engine

Pitch a startup idea and upload raw founder documents. Seven specialized AI agents — Strategy CEO, Market Researcher, Product Architect, Growth Marketer, CFO, an adversarial Investment VC, and a Synthesis Director — dissect your venture across seven structured phases, grounded in real founder documents via pgvector semantic search. 

The committee challenges TAM claims, calculates unit economics, stress-tests critical failure modes, and synthesizes a comprehensive 20-section investor-grade venture blueprint with live telemetry.

**Live demo:** [https://frontend-amber-ten-59.vercel.app/](https://frontend-amber-ten-59.vercel.app/)  
**Live API:** [https://capable-unity-production.up.railway.app](https://capable-unity-production.up.railway.app)  
**Interactive API Docs:** [https://capable-unity-production.up.railway.app/docs](https://capable-unity-production.up.railway.app/docs)  
**Sample Completed Session:** [https://frontend-amber-ten-59.vercel.app/analyse?session=7a340771-ae5c-4ce4-9a1f-fd8fe4bb4979](https://frontend-amber-ten-59.vercel.app/analyse?session=7a340771-ae5c-4ce4-9a1f-fd8fe4bb4979)

---

## Why this exists

Most "AI startup analysis" tools generate vague, cheerleading pitch summaries using a single generic LLM prompt that hallucinates market data and accepts every founder claim at face value.

VentureOS runs an autonomous, multi-agent venture evaluation committee. Instead of an ungrounded essay, seven specialized agents with conflicting priors challenge each other: the Investment VC actively stress-tests the CEO's moat assumptions, the Finance Agent computes unit economics against the Product roadmap, and the Synthesis Agent reconciles contrarian friction into an actionable 20-section blueprint.

The output isn't free-form text parsed after the fact. Every agent emits a Pydantic-validated schema; JSONB outputs are persisted transactionally in PostgreSQL, and every factual claim is grounded in founder documents via pgvector semantic search.

---

## Highlights

* **7 stable-lens agents.** CEO / Strategy, Market Research, Product Architect, GTM & Marketing, Finance & Unit Economics, Investment / VC (adversarial red-team), and Final Synthesis.
* **Sequential intelligence pipeline.** Each agent consumes structured predecessor outputs rather than raw transcripts, accumulating insights while avoiding context bloat.
* **Grounded RAG with pgvector.** Pitch decks, whitepapers, and financials (PDF, DOCX, TXT, MD) are chunked into 768-dimensional embeddings and matched via native HNSW cosine similarity search.
* **Real-time execution telemetry.** A live terminal displays granular event streams (`agent_started`, `retrieval_completed`, `llm_started`, `validation_passed`, `agent_completed`) with millisecond execution timers.
* **Quantitative venture scoring.** The Investment Agent calculates a calibrated 0–100 venture readiness score, identifies fatal dealbreakers, and rates team, market, and execution risks.
* **20-section investor-grade blueprint.** Executive summary, TAM/SAM/SOM sizing, ICP personas, technical architecture, CAC/LTV model, 12-month runway, moat matrix, contrarian friction, and 30/90-day execution roadmaps.
* **Complete persistence & replay.** Every session and agent output is stored in Supabase PostgreSQL; reload and review any past analysis from the History dashboard.
* **Built-in evaluation suite.** Automated test harnesses benchmark RAG Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and agent schema validation.

---

## What it looks like

* **Left pane — The Strategy Room.** Color-coded agent cards reflect real-time execution states (`pending` &rarr; `processing` &rarr; `completed`), live duration timers, and a streaming terminal detailing RAG retrieval queries and reasoning steps.
* **Right pane — The Venture Blueprint.** A 20-section interactive report rendered from validated Pydantic schemas, complete with citation badges referencing grounded document pages, financial projection cards, and risk matrices.
* **Knowledge Data Room.** Drag-and-drop founder documents with instant chunking, embedding generation, and vector index verification.
* **Session History.** Browse past analyses with progress indicators, industry badges, and one-click re-runs.

---

## Architecture

```
User (Browser)
     │
     ▼
Next.js 14 Frontend (Vercel)
     │
     ▼ HTTPS / REST Polling
FastAPI Python Backend (Railway)
     │
     ├── Google Gemini API (gemini-3.5-flash / gemini-embedding-001)
     │
     └── Supabase PostgreSQL
            ├── startup_sessions (State & Metadata)
            ├── agent_outputs (Validated JSONB Deliverables)
            ├── agent_execution_logs (Real-Time Observability Events)
            ├── knowledge_documents & document_chunks (pgvector HNSW)
            └── ventureos-documents (Storage Bucket)
```

---

## The agents

| Agent | Role | Focus / Core Deliverable | Grounding & Tools |
| :--- | :--- | :--- | :--- |
| **CEO / Strategy** | Sets venture direction, mission, and moat | Core thesis, value prop, defensive barriers | Founder inputs + RAG |
| **Market Research** | Validates market opportunity and audience | TAM/SAM/SOM calculation, ICP personas, competitors | RAG context retrieval |
| **Product & Tech** | Defines product scope and engineering architecture | Core feature set, technical stack, MVP roadmap | Predecessor context + RAG |
| **Marketing / GTM** | Builds acquisition loops and positioning | Distribution channels, viral loops, CAC estimates | Market findings + RAG |
| **Finance** | Projects financial viability and runway | Unit economics (CAC, LTV, payback), burn rate | Product roadmap + GTM |
| **Investment / VC** | Adversarial red-team stress-testing all claims | 0–100 venture score, dealbreakers, assumption audit | All predecessor outputs |
| **Final Synthesis** | Consolidates all deliverables into one blueprint | 20-section unified report, friction resolution | Complete committee synthesis |

---

## The orchestration loop

```python
# Sequential handoff: clean schema handoff with zero prompt bloat
session = session_repository.get_session(session_id)
orchestrator.initialize_pipeline_records(session_id)

for agent in ["ceo", "market", "product", "marketing", "finance", "investment", "synthesis"]:
    log_event(agent, "agent_started")
    rag_context = rag_service.retrieve_context(agent.query(startup_context))
    
    # Structured Pydantic execution with 60s timeout & automatic retry
    output = await agent.execute(startup_context, rag_context, predecessor_context)
    
    # Persist validated JSONB with execution duration & metadata
    agent_output_repository.save(session_id, agent.name, output, duration_ms)
    log_event(agent, "agent_completed")
    
session_repository.update_session_status(session_id, "completed")
```

### Why the design choices:
* **Sequential intelligence over unstructured free-for-all:** Open chat rooms drift into repetitive arguments. A directed sequence gives each specialist the exact structured context it needs to build upon or challenge previous conclusions.
* **Grounded RAG over hallucinated benchmarks:** Instead of guessing industry metrics, agents retrieve factual snippets from the founder's uploaded pitch decks and financial sheets using 768-dimensional cosine similarity.
* **Pydantic schemas over raw markdown:** Free-form LLM output is brittle. Every agent validates against explicit Pydantic models before persisting to the database.
* **Resilient metadata fallback:** Timing and execution metrics are embedded inside JSONB `_meta` structures, ensuring zero data loss even if database columns are unmigrated.
* **Graceful degradation:** If an individual agent encounters an issue, the pipeline records the failure, notifies the terminal, and allows single-click retries without restarting the entire run.

---

## Quick start

### Prerequisites
* Python 3.11+ (Python 3.12 recommended) and Node.js 18+
* A Google Gemini API Key — [Google AI Studio](https://aistudio.google.com/)
* A Supabase Project — [supabase.com](https://supabase.com)

### 1. Clone Repository
```bash
git clone https://github.com/Kaustubh-kodes/VentureOs.git
cd VentureOs
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and supply GEMINI_API_KEY, SUPABASE_URL, and SUPABASE_KEY

# Start FastAPI backend
uvicorn app.main:app --reload --port 8000
```
Interactive API docs will be live at: `http://localhost:8000/docs`

### 3. Frontend Setup
In a second terminal:
```bash
cd frontend
npm install

# Configure local backend URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start Next.js development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Deploying (Vercel + Railway + Supabase)

The live production deployment splits the stack across three purpose-built platforms:

```
Vercel (Frontend) ──▶ Railway (FastAPI Backend) ──▶ Supabase (PostgreSQL + pgvector)
```

1. **Database &rarr; Supabase:**
   - Create a free project at [supabase.com](https://supabase.com).
   - In the **SQL Editor**, execute the migration scripts in `backend/database/migrations/` (`001` through `005`) to create the session tables, pgvector HNSW index, and `match_document_chunks` RPC.
   - Create a public storage bucket named `ventureos-documents` under **Storage**.
   - Copy your **Project URL** and **Service Role Key** from **Project Settings &rarr; API**.

2. **Backend &rarr; Railway:**
   - Import `Kaustubh-kodes/VentureOs` on [railway.app](https://railway.app).
   - The root `railway.json` automatically configures the Nixpacks build and start command (`cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`).
   - Set Environment Variables: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `PORT=8000`, `ENVIRONMENT=production`, and `CORS_ORIGINS=["https://<your-vercel-domain>.vercel.app", "http://localhost:3000"]`.
   - In **Settings &rarr; Networking**, click **Generate Domain** (e.g. `capable-unity-production.up.railway.app`).

3. **Frontend &rarr; Vercel:**
   - Import `Kaustubh-kodes/VentureOs` on [vercel.com](https://vercel.com).
   - Set **Root Directory** to `frontend`.
   - Add Environment Variable: `NEXT_PUBLIC_API_URL=https://<your-railway-domain>.up.railway.app`.
   - Click **Deploy**. Next.js is automatically built and served globally on the Edge Network.

---

## Configuration (.env)

### Backend (`backend/.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | — | **Required.** Google Gemini API Key |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Gemini model for reasoning & structured output |
| `SUPABASE_URL` | — | **Required.** Supabase Project URL |
| `SUPABASE_KEY` | — | **Required.** Supabase service role or anon key |
| `SUPABASE_STORAGE_BUCKET` | `ventureos-documents` | Storage bucket for uploaded founder documents |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend domains (JSON array or comma-separated) |
| `PORT` | `8000` | Server listening port |
| `ENVIRONMENT` | `development` | Environment mode (`development` or `production`) |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Base URL of the FastAPI backend (set to Railway URL in production) |

---

## API Surface

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check endpoint (Railway monitoring) |
| `POST` | `/api/analysis/start` | Creates a new session, pre-seeds 7 agent records, starts pipeline in background |
| `POST` | `/api/analysis/{id}/run` | Triggers sequential pipeline for an existing session |
| `GET` | `/api/analysis/{id}/status` | Polls real-time progress percentage, current agent, and agent statuses |
| `GET` | `/api/analysis/{id}/logs` | Retrieves chronological execution telemetry events |
| `POST` | `/api/analysis/{id}/retry/{agent}` | Re-runs a specific agent step with fresh predecessor context |
| `POST` | `/api/documents/upload` | Uploads, parses, chunks, and embeds founder documents into pgvector |
| `GET` | `/api/sessions` | Lists paginated historical analysis sessions |
| `GET` | `/api/sessions/{id}` | Fetches full session details and all 7 JSONB deliverables |

---

## Repository layout

```
ventureos/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application & CORS configuration
│   │   ├── config.py                # Pydantic settings & production validation
│   │   ├── agents/                  # 7 specialized LLM agent implementations
│   │   │   ├── base_agent.py        # Abstract agent class with RAG & reasoning contract
│   │   │   ├── ceo_agent.py         # Strategy, vision & moat analysis
│   │   │   ├── market_agent.py      # Market sizing, ICP personas & competitors
│   │   │   ├── product_agent.py     # MVP feature cut & technical architecture
│   │   │   ├── marketing_agent.py   # GTM loops, positioning & channel strategy
│   │   │   ├── finance_agent.py     # Unit economics, burn rate & runway model
│   │   │   ├── investment_agent.py  # Adversarial VC evaluation & 0-100 venture score
│   │   │   └── synthesis_agent.py   # 20-section unified venture blueprint compiler
│   │   ├── api/                     # REST route handlers
│   │   │   ├── analysis.py          # Pipeline launch, status polling & log events
│   │   │   ├── documents.py         # Document upload, extraction & chunking
│   │   │   └── evaluation.py        # Automated benchmark runner endpoints
│   │   ├── evaluation/              # RAG & agent quality evaluation suite
│   │   │   ├── rag_evaluator.py     # Precision@K, Recall@K, MRR evaluation
│   │   │   ├── agent_evaluator.py   # Schema compliance & hallucination check
│   │   │   └── run_evaluation.py    # Automated CLI benchmark runner
│   │   ├── repositories/            # Database access layer (Supabase PostgreSQL)
│   │   │   ├── session_repository.py       # Session CRUD & status transitions
│   │   │   ├── agent_output_repository.py  # Resilient JSONB deliverables & metadata
│   │   │   ├── execution_log_repository.py # Real-time telemetry event logger
│   │   │   └── document_repository.py      # pgvector chunk storage & queries
│   │   ├── schemas/                 # Pydantic validation models
│   │   └── services/                # Core business logic (RAG, Gemini SDK, Chunking)
│   ├── database/migrations/         # 5 sequential SQL migrations for Supabase
│   ├── requirements.txt             # Python dependencies
│   └── .env.example                 # Template environment variables
├── frontend/                        # Next.js 14 App Router frontend
│   ├── app/                         # App Router pages (/, /analyse, /history, /knowledge)
│   ├── components/                  # Strategy Room, Progress Board, Terminal & Report views
│   ├── lib/                         # API client & data utilities
│   ├── public/                      # Static assets & branding
│   └── package.json                 # Frontend dependencies
├── railway.json                     # Railway deployment specification
├── Procfile                         # Process start command
└── README.md                        # Documentation
```

---

## Verification & testing

Run the automated evaluation suite against benchmark cases:

```bash
# Run RAG & agent evaluation harness
python backend/app/evaluation/run_evaluation.py
```
* **RAG Retrieval Quality**: Evaluates Precision@5, Recall@5, and MRR against ground truth documents.
* **Schema Conformance**: Asserts 100% Pydantic validation across all 7 agent schemas.
* **Observability Verification**: Confirms all 7 execution events stream to `agent_execution_logs`.

---

## License & Author

Crafted by **Kaustubh Tiwari** as part of the **VentureOS Multi-Agent Intelligence Initiative**.  
Licensed under the [MIT License](LICENSE).
