#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
TMP_DIR="${TMPDIR:-$HOME/tmp}"
mkdir -p "$TMP_DIR"
python3 -m py_compile $(find ai_workflow_os -name "*.py" -type f)
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli doctor
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli catalog > "$TMP_DIR/ai_workflow_os_catalog_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli providers > "$TMP_DIR/ai_workflow_os_providers_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli permissions > "$TMP_DIR/ai_workflow_os_permissions_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli tools > "$TMP_DIR/ai_workflow_os_tools_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli inspect . > "$TMP_DIR/ai_workflow_os_inspect_$$.json"
test -s "$TMP_DIR/ai_workflow_os_catalog_$$.json"
rm -f "$TMP_DIR"/ai_workflow_os_*_$$.json
echo "PASS: AI Workflow OS app verifies."
