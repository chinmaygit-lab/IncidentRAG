# Architecture

IncidentRAG separates retrieval, confidence, and generation so each layer can be tested independently.

## Retrieval

The local engine builds two indexes over the same chunks. BM25 captures exact operational vocabulary such as status codes and error identifiers. The hashing embedder captures a lightweight distributional signal without a model download. Reciprocal-rank fusion combines rank positions rather than assuming the two score scales are directly comparable. A final reranker adds title overlap and structured signal matches.

## Confidence and abstention

The top reranked score and top-two margin feed a small policy object. Threshold calibration is benchmark-driven. The packaged default is conservative for the included corpus, but deployments should recalibrate using representative answerable and no-answer incidents.

## Generation

The default generator is extractive: remediation sentences are selected from retrieved evidence and each line receives a source citation. The optional model-backed adapter receives only the incident and retrieved evidence. Its output must contain valid evidence citations.

## Storage

SQLite is the default to keep the project runnable anywhere. PostgreSQL SQL is supplied for weighted FTS and optional pgvector HNSW search. Database adapters do not change the citation model.
