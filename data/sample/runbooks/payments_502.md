# Payments 502 Provider Timeout Runbook
service: payments
severity: P1
http_status: 502
error_code: PAYMENT_GATEWAY_TIMEOUT

## Symptoms
Payment authorization returns 502 while the external gateway latency spikes. The canonical error code is PAYMENT_GATEWAY_TIMEOUT.

## Likely causes
The leading hypothesis is provider latency or an exhausted outbound connection pool. Confirm evidence before remediation.

## Investigation and remediation
- Check provider latency and timeout metrics for the payment gateway.
- Verify outbound connection pool saturation before restarting workers.
- Disable the degraded provider route only when the approved failover path is healthy.
- Compare authorization success rate after failover.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
