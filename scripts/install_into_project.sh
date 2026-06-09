#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-.}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$TARGET/.claude/context" "$TARGET/.claude/tasks" "$TARGET/.claude/scripts"
cp -f "$ROOT/workflow/"*.md "$TARGET/.claude/context/" 2>/dev/null || true
cp -f "$ROOT/standards/"*.md "$TARGET/.claude/context/" 2>/dev/null || true
cp -f "$ROOT/scripts/export_handoff_packet.sh" "$TARGET/.claude/scripts/" 2>/dev/null || true
cp -f "$ROOT/workflow/MASTER_AGENT_START_PROMPT.md" "$TARGET/.claude/tasks/" 2>/dev/null || true
echo "AI Workflow OS installed into $TARGET"
