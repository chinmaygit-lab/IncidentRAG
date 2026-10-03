# INC-2026-05 Search Index Saturation
service: search
severity: P2
http_status: 200
error_code: SEARCH_SLOW

Search latency increased during a concurrent index refresh and traffic peak. Throttling maintenance work restored latency. A capacity alert was added afterward.
