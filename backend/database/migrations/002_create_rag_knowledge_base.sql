-- ============================================================================
-- VentureOS Phase 5 Migration: RAG Knowledge Base + pgvector
-- ============================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ----------------------------------------------------------------------------
-- 1. knowledge_documents Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES startup_sessions(id) ON DELETE SET NULL,
    user_id UUID,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    title TEXT,
    description TEXT,
    storage_path TEXT,
    status TEXT NOT NULL DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
    total_chunks INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- 2. document_chunks Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(768),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- 3. Indexes for Filtering & Vector Search (HNSW Cosine Similarity)
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_session_id ON knowledge_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_status ON knowledge_documents(status);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);

-- HNSW cosine similarity index for fast semantic vector search
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- ----------------------------------------------------------------------------
-- 4. Timestamp Auto-Update Trigger for knowledge_documents
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_knowledge_documents_updated_at ON knowledge_documents;
CREATE TRIGGER tr_knowledge_documents_updated_at
BEFORE UPDATE ON knowledge_documents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 5. Semantic Vector Search RPC Function
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.0,
    match_count int DEFAULT 5,
    filter_document_id uuid DEFAULT NULL,
    filter_session_id uuid DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    document_id uuid,
    chunk_index int,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        dc.metadata,
        (1 - (dc.embedding <=> query_embedding))::float AS similarity
    FROM document_chunks dc
    LEFT JOIN knowledge_documents kd ON dc.document_id = kd.id
    WHERE (filter_document_id IS NULL OR dc.document_id = filter_document_id)
      AND (filter_session_id IS NULL OR kd.session_id = filter_session_id)
      AND ((1 - (dc.embedding <=> query_embedding)) >= match_threshold)
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ----------------------------------------------------------------------------
-- 6. Row Level Security & Permissions
-- ----------------------------------------------------------------------------
ALTER TABLE knowledge_documents ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access to knowledge_documents" ON knowledge_documents;
CREATE POLICY "Allow full access to knowledge_documents" ON knowledge_documents FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access to document_chunks" ON document_chunks;
CREATE POLICY "Allow full access to document_chunks" ON document_chunks FOR ALL USING (true) WITH CHECK (true);

GRANT ALL ON TABLE knowledge_documents TO anon, authenticated, service_role;
GRANT ALL ON TABLE document_chunks TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION match_document_chunks TO anon, authenticated, service_role;
