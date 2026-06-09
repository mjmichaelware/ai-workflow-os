# AI Workflow OS

Reusable AI-agent workflow control plane for creating and repairing applications.

This repo is generic. It must not contain target-app missions, bug ledgers, patch plans, proof reports, or app handoff packets.

## Current capabilities

- Python CLI
- Local dashboard
- Provider registry
- Permission model
- Google Secret Manager reference layer
- Dry-run agent planning
- Target-project installer
- Handoff packet exporter

## Verify

bash scripts/verify_workflow_app.sh

## Dashboard

bash scripts/run_dashboard.sh

## CLI

bin/ai-workflow-os doctor
bin/ai-workflow-os catalog
bin/ai-workflow-os providers
bin/ai-workflow-os permissions
bin/ai-workflow-os secret-status SECRET_NAME --project PROJECT_ID
bin/ai-workflow-os agent-plan "Create an app that does X" --target /path/to/app
bin/ai-workflow-os agent-run runs/RUN_ID/plan.json

## Boundary

AI Workflow OS is the process engine. Each target app owns its own project data.

Secret values are never printed and never committed.
