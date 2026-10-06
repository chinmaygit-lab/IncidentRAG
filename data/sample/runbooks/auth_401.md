# Auth 401 Token Validation Runbook
service: auth
severity: P1
http_status: 401
error_code: TOKEN_EXPIRED

## Symptoms
Valid users receive 401 because token validation rejects recently issued tokens. The canonical error code is TOKEN_EXPIRED.

## Likely causes
The leading hypothesis is clock skew, stale signing keys, or token expiry configuration. Confirm evidence before remediation.

## Investigation and remediation
- Check clock skew across auth nodes and identity provider hosts.
- Verify the active signing key set matches the identity provider JWKS.
- Restore time synchronization before rotating keys.
- Compare token validation success after synchronization.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
