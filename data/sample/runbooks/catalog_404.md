# Catalog 404 Cache Consistency Runbook
service: catalog
severity: P1
http_status: 404
error_code: STALE_CACHE

## Symptoms
Recent catalog items return 404 even though records exist in the database. The canonical error code is STALE_CACHE.

## Likely causes
The leading hypothesis is stale edge cache or delayed search index propagation. Confirm evidence before remediation.

## Investigation and remediation
- Check whether the catalog record exists in the source database.
- Verify cache age and index replication lag for the missing item.
- Invalidate the affected cache key before any broad cache purge.
- Compare item visibility across API and search after invalidation.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
