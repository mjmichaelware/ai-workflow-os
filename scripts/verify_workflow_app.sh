#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
TMP_DIR="${TMPDIR:-$HOME/tmp}"
mkdir -p "$TMP_DIR"
python3 -m py_compile $(find ai_workflow_os -name "*.py" -type f)
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli doctor
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli tools > "$TMP_DIR/aiwos_tools_$$.json"
GEN_TARGET="$TMP_DIR/aiwos_generated_app_$$"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli create-app "Create a test app with UI and health endpoint" --target "$GEN_TARGET" --name test-generated --execute > "$TMP_DIR/aiwos_generated_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli test-app "$GEN_TARGET" > "$TMP_DIR/aiwos_generated_test_$$.json"
rm -rf "$GEN_TARGET" "$TMP_DIR"/aiwos_*_$$.json
echo "PASS: AI Workflow OS app verifies."
