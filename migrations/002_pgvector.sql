CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE incidentrag_chunks
    ADD COLUMN IF NOT EXISTS embedding vector(256);

CREATE INDEX IF NOT EXISTS idx_incidentrag_chunks_embedding
    ON incidentrag_chunks USING hnsw (embedding vector_cosine_ops);
