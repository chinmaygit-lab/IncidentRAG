# INC-2026-01 Catalog Cache Staleness
service: catalog
severity: P1
http_status: 404
error_code: STALE_CACHE

## Incident summary
During this historical incident, recent catalog items return 404 even though records exist in the database. Investigation showed stale edge cache or delayed search index propagation.

## Evidence
The responders correlated deploy and dependency telemetry with the STALE_CACHE failures. The incident timeline ruled out unrelated services.

## Resolution
Check whether the catalog record exists in the source database. Invalidate the affected cache key before any broad cache purge. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
