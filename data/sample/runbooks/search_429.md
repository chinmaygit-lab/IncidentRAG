# Search 429 Capacity Runbook
service: search
severity: P1
http_status: 429
error_code: RATE_LIMITED

## Symptoms
Search traffic receives 429 during a demand spike. The canonical error code is RATE_LIMITED.

## Likely causes
The leading hypothesis is rate limiter saturation or insufficient query capacity. Confirm evidence before remediation.

## Investigation and remediation
- Check rate-limit counters and search worker saturation.
- Verify the traffic spike is legitimate before raising limits.
- Drain overloaded search workers only after replacement capacity is ready.
- Compare p95 latency and 429 rate after capacity changes.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
