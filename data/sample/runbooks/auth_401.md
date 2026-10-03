# Authentication 401 Runbook
service: auth
http_status: 401
error_code: TOKEN_INVALID

## Symptoms
Clients receive HTTP 401 and token validation errors. TOKEN_INVALID may appear after key rotation or issuer configuration changes.

## Checks
Verify signing-key availability, issuer and audience configuration, token clock skew, and recent authentication deployments.

## Recovery
Restore the last known-good key/configuration only through the controlled authentication change process.
