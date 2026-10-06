# Profile 500 Serialization Runbook
service: profile
severity: P1
http_status: 500
error_code: SCHEMA_MISMATCH

## Symptoms
Profile reads return 500 after a deployment changes a response field. The canonical error code is SCHEMA_MISMATCH.

## Likely causes
The leading hypothesis is application schema mismatch between deployed versions. Confirm evidence before remediation.

## Investigation and remediation
- Check profile serialization errors and deployment version skew.
- Verify old and new profile schema versions are backward compatible.
- Rollback the incompatible profile deployment when mixed-version traffic is unsafe.
- Compare profile read success after versions converge.

## Guardrails
Do not execute destructive changes without the normal production approval path. Preserve evidence and correlate timestamps before escalation.
