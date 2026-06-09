# AGENTS.md

AI Workflow OS is a phone-first local application factory. It starts on Termux Android ARM64 and stays portable to desktop, SaaS, and public contributor workflows.

## Rules

- Never print, commit, or hardcode secrets.
- Use existing CLI authentication only.
- No arbitrary browser-to-shell endpoint.
- Prompt-driven work must pass approval, repo-scoped action, compile, tests, proof, and audit.
- Keep public code clean, minimal, readable, and free of fake proof.

## Primary loop

prompt -> event -> approval -> action -> CLI capability -> material change -> compile -> test -> proof -> export -> publish
