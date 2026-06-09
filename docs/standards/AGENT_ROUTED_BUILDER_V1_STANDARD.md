
# Agent-Routed Builder v1 Standard

AI Workflow OS may use installed local model CLIs as scoped planning engines for generated apps.

## Rules

- Save agent outputs as drafts, not as immediately trusted executable shell.
- Do not execute shell commands returned by an agent.
- Do not print secrets.
- Do not put tokens in URLs.
- Do not request broad permissions.
- Every generated app still receives the inherited shell and proof packet.
- Agent routing must remain optional when a CLI is missing.
