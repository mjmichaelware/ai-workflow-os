from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


DEFAULT_RULES: Dict[str, str] = {
    "inspect_repo": "auto",
    "read_files": "auto",
    "write_files": "approval",
    "create_plan": "auto",
    "read_secret": "approval",
    "execute_shell": "approval",
    "live_api_call": "approval",
    "git_commit": "approval",
    "git_push": "approval",
    "cloud_write": "approval",
    "deploy": "approval",
}


@dataclass
class ActionRequest:
    kind: str
    description: str
    command: str = ""


class PermissionPolicy:
    def __init__(self, mode: str = "dry_run", rules: Dict[str, str] | None = None) -> None:
        self.mode = mode
        self.rules = dict(DEFAULT_RULES)
        if rules:
            self.rules.update(rules)

    def requirement(self, kind: str) -> str:
        return self.rules.get(kind, "approval")

    def allowed(self, request: ActionRequest, approved: bool = False) -> bool:
        requirement = self.requirement(request.kind)
        if self.mode == "dry_run":
            return False
        if requirement == "auto":
            return True
        return approved

    def explain(self) -> Dict[str, object]:
        return {
            "mode": self.mode,
            "rules": self.rules,
            "safety": "dry_run blocks side effects; approval is required for secrets, shell execution, live APIs, git push, cloud writes, and deploys",
        }


def default_policy_json() -> Dict[str, object]:
    return PermissionPolicy().explain()
