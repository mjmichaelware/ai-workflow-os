# Install Into Another Project

Copy the workflow files into a target repo:

```bash
mkdir -p .claude/context .claude/tasks .claude/scripts
cp workflow/*.md .claude/context/
cp scripts/export_handoff_packet.sh .claude/scripts/
```

Then adapt the project-specific files:

- SESSION_STATE.md
- BUG_LEDGER.md
- FINAL_PATCH_PLAN.md
- CANONICAL_RESOLVED_SPEC.md
