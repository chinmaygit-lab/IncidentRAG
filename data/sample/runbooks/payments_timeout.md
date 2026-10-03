# Payments Timeout Runbook
service: payments
http_status: 504
error_code: PAYMENT_TIMEOUT

## Symptoms
Payment authorization requests exceed the gateway timeout and return HTTP 504. Application logs may contain PAYMENT_TIMEOUT.

## Checks
Inspect payment provider latency, connection pool saturation, retry volume and downstream error rate. Avoid multiplying retries when the provider is already slow.

## Recovery
Reduce retry amplification, follow the provider-degradation procedure, and enable the approved fallback only when its prerequisites are satisfied.
