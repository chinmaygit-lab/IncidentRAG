# Operations

## Health

`/healthz` reports document/chunk counts and lightweight process telemetry. `/readyz` reports whether the application can serve requests.

## API authentication

Set `INCIDENTRAG_API_KEY` to require `X-API-Key` for versioned search/answer/metrics routes. Terminate TLS at a trusted reverse proxy in real deployments.

## Persistence

SQLite is suitable for demos and local evaluation. Use PostgreSQL for concurrent production-style workloads.

## Logging and secrets

Do not store incident credentials in the corpus. `redact_secrets()` can remove common token/password forms before logs, but it is not a comprehensive data-loss-prevention system.

## Thresholds

Recalibrate the abstention threshold after changing the corpus, embedder, fusion weights, reranker, or query distribution.
