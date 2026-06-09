
# Agent-Routed Builder

Agent-Routed Builder v1 routes a user prompt to installed local model CLIs when they support non-interactive prompt mode.

The route saves draft plans under `agent_drafts/`, records `AGENT_ROUTE.json`, then keeps the normal AI Workflow OS safety path: generated app shell, manifest, tests, proof packet, child builder, and Android wrapper scaffold.

This is not unrestricted agent shell execution.
