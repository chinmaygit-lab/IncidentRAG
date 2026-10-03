# INC-2026-07 Authentication Key Rotation
service: auth
severity: P2
http_status: 401
error_code: TOKEN_INVALID

An incomplete signing-key rotation caused token validation failures. Restoring the previous valid key set recovered authentication while the configuration was corrected.
