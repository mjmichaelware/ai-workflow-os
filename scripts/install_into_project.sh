#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-.}"
NAME="${2:-REPLACE_ME}"
PYTHONPATH="$ROOT" python3 -m ai_workflow_os.cli init-project "$TARGET" --name "$NAME"
