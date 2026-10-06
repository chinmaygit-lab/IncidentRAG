CREATE TABLE IF NOT EXISTS incidentrag_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(text, '')), 'B') ||
        setweight(to_tsvector('simple', coalesce(metadata::text, '')), 'C')
    ) STORED
);

CREATE INDEX IF NOT EXISTS idx_incidentrag_chunks_fts
    ON incidentrag_chunks USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_incidentrag_chunks_document
    ON incidentrag_chunks(document_id, position);
