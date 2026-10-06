# INC-2026-03 Orders Pool Exhaustion
service: orders
severity: P1
http_status: 504
error_code: DB_POOL_EXHAUSTED

## Incident summary
During this historical incident, order creation times out with 504 while database pool wait time increases. Investigation showed pool exhaustion caused by slow queries or leaked connections.

## Evidence
The responders correlated deploy and dependency telemetry with the DB_POOL_EXHAUSTED failures. The incident timeline ruled out unrelated services.

## Resolution
Check database pool wait time and active connection counts. Restart only workers with confirmed leaked connections and preserved queue state. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
