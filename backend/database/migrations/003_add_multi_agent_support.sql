-- ============================================================================
-- VentureOS Phase 6 Migration: Multi-Agent Support & Execution Logs
-- ============================================================================

-- 1. Update startup_sessions status check constraint to include 'partially_completed'
ALTER TABLE startup_sessions DROP CONSTRAINT IF EXISTS startup_sessions_status_check;
ALTER TABLE startup_sessions 
ADD CONSTRAINT startup_sessions_status_check 
CHECK (status IN ('created', 'processing', 'completed', 'failed', 'partially_completed'));

-- 2. agent_execution_logs Table for Observability & Live Progress
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES startup_sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_agent_execution_logs_session_id ON agent_execution_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_execution_logs_created_at ON agent_execution_logs(created_at ASC);

-- 4. Row Level Security & Permissions
ALTER TABLE agent_execution_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access to agent_execution_logs" ON agent_execution_logs;
CREATE POLICY "Allow full access to agent_execution_logs" ON agent_execution_logs FOR ALL USING (true) WITH CHECK (true);

GRANT ALL ON TABLE agent_execution_logs TO anon, authenticated, service_role;
