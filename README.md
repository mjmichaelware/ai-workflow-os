# AI Workflow OS

Reusable AI-agent workflow kit for creating and repairing applications.

This repo is generic. It must not contain app-specific missions, bug ledgers, patch plans, or handoff packets.

## Verify

bash scripts/verify_workflow_app.sh

## Run dashboard

bash scripts/run_dashboard.sh

## CLI

bin/ai-workflow-os doctor
bin/ai-workflow-os catalog
bin/ai-workflow-os init-project /path/to/app --name MyApp
bin/ai-workflow-os export-packet /path/to/app --out $HOME/storage/downloads

## Boundary

AI Workflow OS is the process engine. Each target app owns its own project data.
