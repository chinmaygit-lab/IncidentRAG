# INC-2026-09 Checkout Readiness Regression
service: checkout
severity: P1
http_status: 503
error_code: UPSTREAM_UNAVAILABLE

## Incident summary
During this historical incident, checkout requests fail immediately after a deployment because readiness probes exclude healthy pods. Investigation showed a readiness regression or upstream connection failure.

## Evidence
The responders correlated deploy and dependency telemetry with the UPSTREAM_UNAVAILABLE failures. The incident timeline ruled out unrelated services.

## Resolution
Check deployment events and readiness probe failures before changing traffic. Rollback the latest checkout deployment when the readiness regression is confirmed. The team monitored recovery and documented the result.

## Learning
Prefer reversible changes, explicit evidence, and service-specific validation during incident response.
