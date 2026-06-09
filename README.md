# AI Workflow OS

Reusable AI-agent workflow control plane for creating and repairing applications from terminal-first workflows.

This repo is generic. It must not contain target-app missions, bug ledgers, patch plans, proof reports, or app handoff packets.

## Capabilities

- Python CLI
- Local dashboard
- Provider registry
- Permission model
- Google Secret Manager reference checks
- Dry-run agent planning
- Approval manifests
- Run logs
- Tool adapters for repo inspection, files, shell, git, gh, and gcloud status
- Target-project installer
- Handoff packet exporter

## Verify

bash scripts/verify_workflow_app.sh

## Dashboard

bash scripts/run_dashboard.sh

## Create an app plan

bin/ai-workflow-os agent-plan "Create an app that does X" --target /path/to/app --out runs

## Approve and run

bin/ai-workflow-os approve-run RUN_ID --out approvals
bin/ai-workflow-os agent-run runs/RUN_ID/plan.json --approve --approval-file approvals/RUN_ID.approval.json

## Safety

- Secret values are never printed.
- Dry-run is the default.
- Approval is required for side effects.
- Git push, cloud writes, live APIs, and deploys are not part of default approval.
