# Notifications 500 Provider Runbook
service: notifications
severity: P1
http_status: 500
error_code: SMTP_PROVIDER_ERROR

## Symptoms
Email notification jobs fail with 500 while provider delivery errors rise. The canonical error code is SMTP_PROVIDER_ERROR.

## Likely causes
The leading hypothesis is provider outage, rejected credentials, or API quota failure. Confirm evidence before remediation.

## Investigation and remediation
- Check provider status and notification delivery error codes.
- Verify provider credentials are valid without logging secret values.
- Switch to the approved backup provider when the primary provider is unavailable.
- Compare queue drain rate and delivery success after failover.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
