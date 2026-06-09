
# Capability Matrix Standard

AI Workflow OS treats public tools, CLIs, APIs, agents, and local commands as scoped capabilities.

## Rules

- No broad permission mode.
- No token-in-URL mode.
- No environment dumps.
- Every capability has an install check.
- Every capability has a safe template.
- Every write-capable capability requires a task packet or explicit proof stage.
- Model CLIs enrich, classify, and assist; they are not treated as unrestricted shell owners.
