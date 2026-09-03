-- ============================================================================
-- VentureOS Phase 8 + 9 Migration: Evaluation Runs, Observability & Hardening
-- ============================================================================

-- 1. Create evaluation_runs table for persisting benchmark and quality evaluation runs
CREATE TABLE IF NOT EXISTS evaluation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_type TEXT NOT NULL,
    status TEXT NOT NULL,
    summary JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

-- 2. Performance & Production Indexes
CREATE INDEX IF NOT EXISTS idx_startup_sessions_status ON startup_sessions(status);
CREATE INDEX IF NOT EXISTS idx_document_chunks_session_doc ON document_chunks(session_id, document_id);
CREATE INDEX IF NOT EXISTS idx_evaluation_runs_created_at ON evaluation_runs(created_at DESC);

-- 3. Row Level Security & Permissions
ALTER TABLE evaluation_runs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access to evaluation_runs" ON evaluation_runs;
CREATE POLICY "Allow full access to evaluation_runs" ON evaluation_runs FOR ALL USING (true) WITH CHECK (true);

GRANT ALL ON TABLE evaluation_runs TO anon, authenticated, service_role;
