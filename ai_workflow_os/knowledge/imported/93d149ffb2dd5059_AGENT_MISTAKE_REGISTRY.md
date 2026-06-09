# Agent Mistake Registry\n\n## 2026-06-08 — Script path import failure

Failure:
- A generated script under `scripts/` imported `ai_workflow_os`.
- It was executed as `python3 scripts/registry_spine.py`.
- Python placed `scripts/` on `sys.path`, not the repo root.
- The script failed with `ModuleNotFoundError: No module named ai_workflow_os`.

Rule:
- Every generated executable Python script inside a subfolder must either:
  1. insert the repo root into `sys.path`, or
  2. be run with `PYTHONPATH="$PWD"`, or
  3. be installed as a package/module command.

Test:
- Run the script the exact way the user will run it.
- Do not count `py_compile` as proof that imports work at runtime.

Judgment:
- Compile proof is not runtime proof.
- Runtime invocation proof is required.
\n