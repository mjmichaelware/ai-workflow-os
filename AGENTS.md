# AGENTS.md

AI Workflow OS is a phone-first local operating agent for building applications from Termux on Android ARM64, designed to grow into desktop, SaaS, and public-contributor workflows.

## Non-negotiable rules

- Never commit, print, or hardcode secrets.
- Use existing CLI authentication and environment variables only.
- No arbitrary browser-to-shell execution.
- Prompt-driven changes pass through approval, repo-scoped actions, compile, tests, proof, and audit.
- Generated apps inherit standards, manifests, tests, proof, and export behavior.
- Public code must be clean, readable, minimal, and free of fake proof.
- Runtime memory is snapshotted intentionally, not dumped into source commits.

## Archetypal loop

prompt -> event -> approval -> action -> Termux CLI capability -> material code change -> compile -> test -> proof -> export -> GitHub publish

## Product direction

Start phone-local. Preserve paths to desktop, SaaS, teams, marketplace, and contributor-led expansion.

