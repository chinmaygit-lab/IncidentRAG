# INC-2026-08 Payment Provider Latency
service: payments
severity: P1
http_status: 504
error_code: PAYMENT_TIMEOUT

A payment provider slowdown caused gateway timeouts. Excess retries increased load. The incident was mitigated by reducing retries and applying the approved provider-degradation fallback.
