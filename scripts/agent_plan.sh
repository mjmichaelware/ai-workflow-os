#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT="${1:-Create an app from a simple prompt using AI Workflow OS.}"
TARGET="${2:-.}"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli agent-plan "$PROMPT" --target "$TARGET" --out "$ROOT/runs"
