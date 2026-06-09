# AI Workflow OS

[![CI](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/ci.yml/badge.svg)](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/ci.yml)
[![Public Hygiene](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/public-hygiene.yml/badge.svg)](https://github.com/mjmichaelware/ai-workflow-os/actions/workflows/public-hygiene.yml)

AI Workflow OS is a phone-first local application factory.

It starts on Android through Termux, but the architecture is designed to grow into desktop, SaaS, team, marketplace, and public-contributor workflows.

## Why this exists

Developer tooling still assumes a desktop-class setup. Many mobile apps expose only a limited subset of what the browser or desktop can do. AI Workflow OS starts from a different belief: the phone should be able to operate the build system.

## What it does now

- opens a local browser operator console
- accepts prompts from the phone
- uses approved local actions instead of raw browser shell
- detects installed CLI tools without printing secrets
- creates generated apps inside the repo
- runs compile and test proof
- exports a phone bundle to Downloads
- installs as a PWA with a real icon
- publishes clean source to GitHub

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

Open: http://127.0.0.1:8765

## Security

Secrets stay outside source. The app reports key presence only. It does not print or store key values.

## Status

Early public operator build. Phone-local first. Cross-device and SaaS paths are planned.
