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
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli research-queries "terminal app creator" > "$TMP_DIR/ai_workflow_os_research_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli self-bootstrap "Improve AI Workflow OS" --out "$TMP_DIR/self_bootstrap_$$" > "$TMP_DIR/ai_workflow_os_self_bootstrap_$$.json"
GEN_TARGET="$TMP_DIR/aiwos_generated_app_$$"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli create-app "Create a test app with UI and health endpoint" --target "$GEN_TARGET" --name test-generated --execute > "$TMP_DIR/ai_workflow_os_generated_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli test-app "$GEN_TARGET" > "$TMP_DIR/ai_workflow_os_generated_test_$$.json"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli export-app "$GEN_TARGET" --out "$TMP_DIR/ai_workflow_os_export_$$.json" >/dev/null
test -s "$TMP_DIR/ai_workflow_os_export_$$.json"
rm -rf "$GEN_TARGET" "$TMP_DIR"/ai_workflow_os_*_$$.json "$TMP_DIR/self_bootstrap_$$"
echo "PASS: AI Workflow OS app verifies."
