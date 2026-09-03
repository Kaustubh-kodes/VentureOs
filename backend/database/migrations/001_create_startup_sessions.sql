-- ============================================================================
-- VentureOS Phase 4 Migration: Startup Sessions & Agent Outputs
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- 1. startup_sessions Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS startup_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    startup_idea TEXT NOT NULL,
    target_audience TEXT NOT NULL,
    industry TEXT NOT NULL,
    budget TEXT NOT NULL,
    timeline TEXT NOT NULL,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'created' CHECK (status IN ('created', 'processing', 'completed', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- 2. agent_outputs Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agent_outputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES startup_sessions(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    output_json JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- 3. Indexes for Query Performance
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_startup_sessions_status ON startup_sessions(status);
CREATE INDEX IF NOT EXISTS idx_startup_sessions_created_at ON startup_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_outputs_session_id ON agent_outputs(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_outputs_agent_name ON agent_outputs(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_outputs_status ON agent_outputs(status);

-- ----------------------------------------------------------------------------
-- 4. Timestamp Auto-Update Trigger
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_startup_sessions_updated_at ON startup_sessions;
CREATE TRIGGER tr_startup_sessions_updated_at
BEFORE UPDATE ON startup_sessions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS tr_agent_outputs_updated_at ON agent_outputs;
CREATE TRIGGER tr_agent_outputs_updated_at
BEFORE UPDATE ON agent_outputs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 5. Row Level Security (RLS) Policies for Backend Access
-- ----------------------------------------------------------------------------
ALTER TABLE startup_sessions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access to startup_sessions" ON startup_sessions;
CREATE POLICY "Allow full access to startup_sessions" ON startup_sessions FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE agent_outputs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access to agent_outputs" ON agent_outputs;
CREATE POLICY "Allow full access to agent_outputs" ON agent_outputs FOR ALL USING (true) WITH CHECK (true);
