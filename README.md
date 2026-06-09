# AI Workflow OS

Reusable AI-agent workflow control plane and terminal-first application creator.

This repo is generic. It must not contain target-app missions, bug ledgers, patch plans, proof reports, or app handoff packets.

## Capabilities

- Python CLI
- Interactive browser dashboard
- Provider registry
- Permission model
- Google Secret Manager reference checks
- Dry-run agent planning
- Approval manifests
- Run logs
- Tool adapters for repo inspection, files, shell, git, gh, and gcloud status
- Market research seed graphs
- Recursive self-bootstrap planning
- Local app generator
- Generated-app import/export/test layer
- Target-project installer
- Handoff packet exporter

## Verify

bash scripts/verify_workflow_app.sh

## Run dashboard

bash scripts/run_dashboard.sh

Open http://127.0.0.1:8765 in the browser.

## Create an app

bin/ai-workflow-os create-app "Create an app that does X" --target generated_apps/demo --name demo --execute
bin/ai-workflow-os test-app generated_apps/demo
bin/ai-workflow-os export-app generated_apps/demo --out runs/demo_manifest.json

## Safety

- Secret values are never printed.
- Dry-run is the default for agent runs.
- Approval is required for side effects.
- Git push, cloud writes, live APIs, and deploys are not part of default approval.
- Entire-web research is implemented as bounded recursive research graphs, not fake infinite crawling.
