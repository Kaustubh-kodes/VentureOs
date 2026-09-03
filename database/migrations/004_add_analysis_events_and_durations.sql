-- ============================================================================
-- VentureOS Phase 7 Migration: Analysis Events, Execution Durations & History
-- ============================================================================

-- 1. Extend agent_outputs with execution duration tracking
ALTER TABLE agent_outputs ADD COLUMN IF NOT EXISTS duration_ms INTEGER;
ALTER TABLE agent_outputs ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ;
ALTER TABLE agent_outputs ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

-- 2. Create primary analysis_events table (Single source of truth for execution observability)
CREATE TABLE IF NOT EXISTS analysis_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES startup_sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Composite & Ordering Indexes for live polling performance
CREATE INDEX IF NOT EXISTS idx_analysis_events_session_id ON analysis_events(session_id);
CREATE INDEX IF NOT EXISTS idx_analysis_events_created_at ON analysis_events(created_at ASC);
CREATE INDEX IF NOT EXISTS idx_agent_outputs_session_agent ON agent_outputs(session_id, agent_name);
CREATE INDEX IF NOT EXISTS idx_startup_sessions_created_at ON startup_sessions(created_at DESC);

-- 4. Row Level Security & Access Permissions
ALTER TABLE analysis_events ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access to analysis_events" ON analysis_events;
CREATE POLICY "Allow full access to analysis_events" ON analysis_events FOR ALL USING (true) WITH CHECK (true);

GRANT ALL ON TABLE analysis_events TO anon, authenticated, service_role;

-- 5. Backwards-compatibility alias/sync with agent_execution_logs if exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'agent_execution_logs') THEN
        INSERT INTO analysis_events (session_id, agent_name, event_type, message, metadata, created_at)
        SELECT session_id, agent_name, event_type, message, metadata, created_at
        FROM agent_execution_logs;
    END IF;
END $$;
