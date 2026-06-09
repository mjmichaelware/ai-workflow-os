# AI Workflow OS

[![CI](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/ci.yml/badge.svg)](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/ci.yml)
[![CodeQL](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/codeql.yml/badge.svg)](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/codeql.yml)
[![Public Hygiene](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/public-hygiene.yml/badge.svg)](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/public-hygiene.yml)

AI Workflow OS is a phone-first local application factory.

It starts on Android through Termux, but the architecture is designed to grow into desktop, SaaS, team, marketplace, and public-contributor workflows.

## Why this exists

Developer tooling still assumes a desktop-class setup. Mobile apps often expose only a limited subset of what browser and desktop workflows can do. AI Workflow OS starts from a different belief:

The phone should be able to operate the build system.

## What it does now

- Opens a local browser operator console
- Accepts prompts from the phone
- Uses approved local actions instead of raw browser shell
- Detects installed CLI tools without printing secrets
- Creates generated apps inside the repo
- Runs compile and test proof
- Exports a phone bundle to Downloads
- Installs as a PWA with a real icon
- Publishes clean source to GitHub

## Operator loop

prompt -> event -> approval -> action -> CLI capability -> material code change -> compile -> test -> proof -> export -> publish

## Supported agent surfaces

- Gemini CLI through GEMINI.md
- Claude Code through CLAUDE.md
- Codex CLI through CODEX.md and AGENTS.md
- GitHub Copilot through .github/copilot-instructions.md
- Cursor through .cursor/rules
- Cline through .clinerules
- Continue through .continue/rules

## Local launch

cd "$HOME/Workspaces/AI_Workflow_OS/ai-workflow-os"
bin/open-ai-workflow-os-phone

Open http://127.0.0.1:8765

## Security

Secrets stay outside source. The app reports key presence only. It does not print or store key values.

## Contributor paths

- Phone-first UX
- Termux ARM64 reliability
- Generated app templates
- Proof and audit reports
- Native Android packaging
- GitHub, Vercel, Supabase, Google Cloud, Gemini, Claude, Codex, Copilot, Cursor, Cline, and Continue integrations
- Desktop and SaaS runner paths

## Status

Early public operator build. Phone-local first. Cross-device and SaaS paths are planned.


## Console-grade direction

AI Workflow OS is being shaped as a cloud-console-style operating surface that runs anywhere: phone, tablet, desktop, Codespaces, local runners, and eventually SaaS.

The phone version is not a toy mode. It is the wedge. The long-term platform goal is a device-independent operating console where the browser is the intent surface and approved runners perform the work.

## Public research snapshots

The repository includes a public landscape research script:

python3 scripts/research_public_landscape.py

It snapshots public GitHub signals for Actions, CodeQL, devcontainers, PWA, Termux, local-first, and agentic coding tools.
