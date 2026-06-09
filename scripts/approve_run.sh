#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="${1:?run id required}"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli approve-run "$RUN_ID" --out "$ROOT/approvals" --by owner
