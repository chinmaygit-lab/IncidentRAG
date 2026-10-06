# Shipping 503 Carrier Runbook
service: shipping
severity: P1
http_status: 503
error_code: CARRIER_UNAVAILABLE

## Symptoms
Shipping quote requests return 503 when the primary carrier api is unavailable. The canonical error code is CARRIER_UNAVAILABLE.

## Likely causes
The leading hypothesis is carrier outage or exhausted carrier client connections. Confirm evidence before remediation.

## Investigation and remediation
- Check primary carrier availability and client timeout metrics.
- Verify the fallback carrier supports the affected regions.
- Disable the primary carrier route only after fallback validation succeeds.
- Compare quote success and latency after traffic shifts.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
