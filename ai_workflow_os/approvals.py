from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time
from typing import List


@dataclass
class ApprovalManifest:
    run_id: str
    approved_by: str
    approved_at: str
    allowed_action_types: List[str]
    notes: str


DEFAULT_APPROVED_ACTIONS = [
    "inspect_repo",
    "read_files",
    "create_plan",
    "write_files",
    "execute_shell",
    "git_commit",
]


def create_manifest(run_id: str, out_dir: Path, approved_by: str = "owner", notes: str = "") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = ApprovalManifest(
        run_id=run_id,
        approved_by=approved_by,
        approved_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        allowed_action_types=DEFAULT_APPROVED_ACTIONS,
        notes=notes or "Approval permits local file/write/shell/git commit actions only. No secret printing, git push, cloud write, live API, or deploy.",
    )
    path = out_dir / f"{run_id}.approval.json"
    path.write_text(json.dumps(asdict(manifest), indent=2))
    return path


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())


def action_is_approved(manifest: dict, action_type: str) -> bool:
    return action_type in manifest.get("allowed_action_types", [])
