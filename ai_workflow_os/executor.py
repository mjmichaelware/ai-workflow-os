from __future__ import annotations

from pathlib import Path
import json

from .permissions import ActionRequest, PermissionPolicy


def execute_plan(plan_path: Path, approve: bool = False) -> dict:
    data = json.loads(plan_path.read_text())
    policy = PermissionPolicy(mode="live" if approve else "dry_run")
    results = []
    for step in data.get("steps", []):
        request = ActionRequest(kind=step.get("action_type", "unknown"), description=step.get("description", ""))
        allowed = policy.allowed(request, approved=approve)
        results.append({
            "step": step.get("id"),
            "title": step.get("title"),
            "action_type": request.kind,
            "would_run": True,
            "executed": False,
            "allowed_by_policy": allowed,
            "reason": "Stage 2 executor records and gates actions. Stage 3 adds concrete tool execution adapters.",
        })
    return {"plan": str(plan_path), "approved": approve, "results": results}
