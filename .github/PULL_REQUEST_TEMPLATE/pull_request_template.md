## Summary

Describe what changed and why.

## Proof

python3 -m py_compile $(find ai_workflow_os -name "*.py" -type f)
PYTHONPATH="$PWD" python3 -m pytest -q
bash scripts/verify_workflow_app.sh

## Safety

- [ ] No secrets were added, printed, or committed.
- [ ] Browser-to-shell boundary remains allowlisted.
- [ ] Runtime files were not committed unless intentionally snapshotted.

## Phone-first impact

Explain how this helps someone build from a phone instead of needing a desktop.
