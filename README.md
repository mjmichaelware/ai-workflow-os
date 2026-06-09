# AI Workflow OS

Reusable AI-agent workflow kit for carrying context, proof, patch plans, and handoffs across Claude, Codex, Gemini, ChatGPT, and future agents.

This is not a deployed app and does not require Google Cloud.

## What it is

- A GitHub-based workflow control plane.
- A reusable `.claude` / AI-agent handoff pattern.
- A way to prevent AI agents from guessing, losing context, or repeating audits.
- A portable handoff-packet exporter.

## What it is not

- Not a token bypass.
- Not a cloud service.
- Not a database project.
- Not tied to one app.

## Standard start prompt

Read `workflow/MASTER_AGENT_START_PROMPT.md` and follow it exactly.

## Core rules

- Do not print secrets.
- Do not hardcode secrets.
- Do not deploy unless explicitly authorized.
- Inspect current code before patching.
- Compile and proof before commit/deploy decisions.
- Do not use heredocs in user-facing terminal commands.
