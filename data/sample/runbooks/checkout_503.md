# Checkout 503 Deployment Runbook
service: checkout
severity: P1
http_status: 503
error_code: UPSTREAM_UNAVAILABLE

## Symptoms
Checkout requests fail immediately after a deployment because readiness probes exclude healthy pods. The canonical error code is UPSTREAM_UNAVAILABLE.

## Likely causes
The leading hypothesis is a readiness regression or upstream connection failure. Confirm evidence before remediation.

## Investigation and remediation
- Check deployment events and readiness probe failures before changing traffic.
- Verify healthy checkout pods are registered behind the gateway.
- Rollback the latest checkout deployment when the readiness regression is confirmed.
- Compare error rate and readiness health after rollback.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
