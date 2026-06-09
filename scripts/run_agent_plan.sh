#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAN="${1:?plan json required}"
APPROVAL="${2:-}"
if [ -n "$APPROVAL" ]; then
  PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli agent-run "$PLAN" --approve --approval-file "$APPROVAL"
else
  PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli agent-run "$PLAN"
fi
