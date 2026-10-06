# Orders 504 Database Pool Runbook
service: orders
severity: P1
http_status: 504
error_code: DB_POOL_EXHAUSTED

## Symptoms
Order creation times out with 504 while database pool wait time increases. The canonical error code is DB_POOL_EXHAUSTED.

## Likely causes
The leading hypothesis is pool exhaustion caused by slow queries or leaked connections. Confirm evidence before remediation.

## Investigation and remediation
- Check database pool wait time and active connection counts.
- Inspect slow order queries before increasing the pool size.
- Restart only workers with confirmed leaked connections and preserved queue state.
- Compare order latency and pool utilization after remediation.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
