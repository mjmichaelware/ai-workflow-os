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
test -s "$TMP_FILE"
rm -f "$TMP_FILE"
echo "PASS: AI Workflow OS app verifies."
