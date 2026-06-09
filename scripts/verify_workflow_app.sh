#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
TMP_DIR="${TMPDIR:-$HOME/tmp}"
mkdir -p "$TMP_DIR"
TMP_FILE="$TMP_DIR/ai_workflow_os_catalog_$$.json"
python3 -m py_compile $(find ai_workflow_os -name "*.py" -type f)
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli doctor
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli catalog > "$TMP_FILE"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli providers > "$TMP_DIR/ai_workflow_os_providers_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli permissions > "$TMP_DIR/ai_workflow_os_permissions_$$.json"
test -s "$TMP_FILE"
rm -f "$TMP_FILE" "$TMP_DIR/ai_workflow_os_providers_$$.json" "$TMP_DIR/ai_workflow_os_permissions_$$.json"
echo "PASS: AI Workflow OS app verifies."
