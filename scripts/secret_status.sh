#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SECRET="${1:?secret name required}"
PROJECT="${2:-}"
if [ -n "$PROJECT" ]; then
  PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli secret-status "$SECRET" --project "$PROJECT"
else
  PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli secret-status "$SECRET"
fi
