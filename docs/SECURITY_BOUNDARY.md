# Security Boundary

The browser is an intent surface. The local runner performs approved work.

## Rules

- No arbitrary browser-to-shell endpoint.
- No secret values in responses.
- No public repository commits containing local runtime databases or logs.
- All material app generation must be repo-scoped.
- Button actions must map to proven endpoints.
