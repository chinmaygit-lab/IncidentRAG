# Checkout 503 Runbook
service: checkout
http_status: 503
error_code: UPSTREAM_UNAVAILABLE

## Symptoms
Checkout requests return HTTP 503 shortly after a deployment. The API gateway may report upstream unavailable or connection failures.

## Checks
Confirm the checkout deployment is healthy, compare the rollout revision with the previous healthy revision, and verify downstream payment and inventory health. Inspect readiness probes before increasing traffic.

## Recovery
If failures correlate with the latest checkout rollout and readiness is degraded, follow the approved rollback procedure. Record the rollout revision and timestamps in the incident.
