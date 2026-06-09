from __future__ import annotations

from pathlib import Path
import json

from .approvals import action_is_approved, load_manifest
from .permissions import ActionRequest, PermissionPolicy
from .runlog import RunLog
from .tools import FileTool, GitTool, RepoInspector, ShellTool


def _run_dir_for_plan(plan_path: Path) -> Path:
    return plan_path.resolve().parent


def execute_plan(plan_path: Path, approve: bool = False, approval_file: Path | None = None) -> dict:
    plan_path = plan_path.resolve()
    data = json.loads(plan_path.read_text())
    run_dir = _run_dir_for_plan(plan_path)
    log = RunLog(run_dir)
    manifest = load_manifest(approval_file.resolve()) if approval_file else None
    policy = PermissionPolicy(mode="live" if approve else "dry_run")
    target = Path(data.get("target", ".")).resolve()
    results = []
    log.append("run_start", "agent run started", {"plan": str(plan_path), "approve": approve, "target": str(target)})

    inspector = RepoInspector()
    file_tool = FileTool()
    shell = ShellTool()
    git = GitTool()

    for step in data.get("steps", []):
        action_type = step.get("action_type", "unknown")
        request = ActionRequest(kind=action_type, description=step.get("description", ""))
        manifest_ok = action_is_approved(manifest, action_type) if manifest else False
        allowed = policy.allowed(request, approved=bool(approve and manifest_ok))
        executed = False
        output = {}

        if action_type == "inspect_repo" and allowed:
            output = inspector.inspect(target)
            (run_dir / "repo_inspection.json").write_text(json.dumps(output, indent=2))
            executed = True
        elif action_type == "write_files" and allowed:
            safe_note = run_dir / f"{step.get(id, step)}_write_note.md"
            result = file_tool.write_text(safe_note, "# Approved Write Placeholder\n\nThis run stage was approved. Concrete app writes are added by stage-specific adapters, not by generic guesses.\n", execute=True)
            output = result.to_dict()
            executed = result.executed
        elif action_type == "execute_shell" and allowed:
            result = shell.run(["python3", "-m", "py_compile"] + [str(p) for p in sorted(Path.cwd().glob("ai_workflow_os/*.py"))], cwd=Path.cwd(), execute=True)
            output = result.to_dict()
            executed = result.executed
        elif action_type == "git_commit" and allowed:
            status = git.status(Path.cwd(), execute=True)
            diff = git.diff_stat(Path.cwd(), execute=True)
            output = {"status": status.to_dict(), "diff": diff.to_dict(), "commit_not_executed": "generic executor does not auto-commit without a dedicated commit command"}
            executed = True
        else:
            output = {"skipped": True, "reason": "not approved, dry-run, or no concrete safe adapter for this action type"}

        item = {
            "step": step.get("id"),
            "title": step.get("title"),
            "action_type": action_type,
            "would_run": True,
            "executed": executed,
            "allowed_by_policy": allowed,
            "manifest_ok": manifest_ok,
            "output": output,
        }
        results.append(item)
        log.append("step", step.get("title", "step"), item)

    log.append("run_complete", "agent run completed", {"steps": len(results)})
    summary = {"plan": str(plan_path), "approved": approve, "approval_file": str(approval_file) if approval_file else None, "events": str(log.path), "results": results}
    (run_dir / "result.json").write_text(json.dumps(summary, indent=2))
    return summary
