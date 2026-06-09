from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import tarfile
from typing import Dict, List

from .catalog import CATALOG


@dataclass
class ProjectStatus:
    root: str
    has_git: bool
    has_claude_dir: bool
    workflow_files: List[str]
    missing_core_files: List[str]


CORE_PROJECT_FILES = [
    ".claude/context/APP_MISSION.md",
    ".claude/context/SESSION_STATE.md",
    ".claude/context/BUG_LEDGER.md",
    ".claude/context/FINAL_PATCH_PLAN.md",
    ".claude/tasks/START_WITH_AI_WORKFLOW_OS.md",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, text: str) -> bool:
    ensure_dir(path.parent)
    if path.exists():
        return False
    path.write_text(text)
    return True


def scan_project(target: Path) -> ProjectStatus:
    target = target.resolve()
    workflow_files = []
    claude_dir = target / ".claude"
    if claude_dir.exists():
        for path in sorted(claude_dir.glob("**/*.md")):
            workflow_files.append(str(path.relative_to(target)))
    missing = [p for p in CORE_PROJECT_FILES if not (target / p).exists()]
    return ProjectStatus(
        root=str(target),
        has_git=(target / ".git").exists(),
        has_claude_dir=claude_dir.exists(),
        workflow_files=workflow_files,
        missing_core_files=missing,
    )


def install_into_project(target: Path, app_name: str = "REPLACE_ME") -> Dict[str, object]:
    target = target.resolve()
    ensure_dir(target / ".claude/context")
    ensure_dir(target / ".claude/tasks")
    ensure_dir(target / ".claude/scripts")
    created = []

    mission = f"# App Mission\n\nApp name: {app_name}\nOwner: REPLACE_ME\n\nMission: REPLACE_ME\n\nUsers: REPLACE_ME\n\nCore workflow: REPLACE_ME\n\nData sources: REPLACE_ME\n\nFrontend goals: REPLACE_ME\n\nBackend goals: REPLACE_ME\n\nSafety rules:\n- Do not print secrets.\n- Do not hardcode secrets.\n- Do not deploy unless explicitly authorized.\n- Do not patch blindly.\n"

    start = "# Start With AI Workflow OS\n\nRead these files first:\n\n1. .claude/context/APP_MISSION.md\n2. .claude/context/SESSION_STATE.md\n3. .claude/context/BUG_LEDGER.md\n4. .claude/context/FINAL_PATCH_PLAN.md\n\nThen inspect the current repository.\n\nDo not patch immediately.\nDo not deploy.\nDo not print secrets.\n\nFirst create or update:\n\n- .claude/context/CANONICAL_RESOLVED_SPEC.md\n- .claude/context/CURRENT_CODE_MAP.md\n- .claude/context/BUG_LEDGER.md\n- .claude/context/FINAL_PATCH_PLAN.md\n\nStop and report the plan before app logic edits.\n"

    session = "# Session State\n\nStatus: initialized by AI Workflow OS.\n\nCurrent task: define this app mission, inspect current code, create canonical spec, create bug ledger, create patch plan.\n\nRules:\n- Do not print secrets.\n- Do not deploy unless explicitly authorized.\n- Do not patch blindly.\n"

    bug = "# Bug Ledger\n\nNo confirmed defects yet.\n\nEvery defect must include:\n- file and function evidence\n- user impact\n- severity\n- proposed fix\n- proof command\n"

    plan = "# Final Patch Plan\n\nNo patch plan yet.\n\nBefore editing app logic:\n1. Inspect current code.\n2. Confirm the defect still exists.\n3. Patch surgically.\n4. Compile.\n5. Run safe proof.\n6. Run diff checks.\n7. Stop before deploy.\n"

    boundary = "# Generic Workflow Boundary\n\nThis target app owns its own mission, audit, bugs, and patch plan.\n\nAI Workflow OS is only the process engine.\nDo not copy another app mission into this app.\n"

    mapping = {
        ".claude/context/APP_MISSION.md": mission,
        ".claude/tasks/START_WITH_AI_WORKFLOW_OS.md": start,
        ".claude/context/SESSION_STATE.md": session,
        ".claude/context/BUG_LEDGER.md": bug,
        ".claude/context/FINAL_PATCH_PLAN.md": plan,
        ".claude/context/GENERIC_WORKFLOW_BOUNDARY.md": boundary,
    }
    for rel, text in mapping.items():
        if write_if_missing(target / rel, text):
            created.append(rel)
    return {"target": str(target), "created": created, "status": scan_project(target).__dict__}


def export_packet(target: Path, out_dir: Path) -> Path:
    target = target.resolve()
    out_dir = out_dir.resolve()
    ensure_dir(out_dir)
    packet_dir = out_dir / "ai_workflow_handoff_packet"
    if packet_dir.exists():
        for child in packet_dir.glob("*"):
            if child.is_file():
                child.unlink()
    ensure_dir(packet_dir)
    for rel in CORE_PROJECT_FILES:
        src = target / rel
        if src.exists():
            (packet_dir / Path(rel).name).write_text(src.read_text())
    archive = out_dir / "ai_workflow_handoff_packet.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(packet_dir, arcname="ai_workflow_handoff_packet")
    return archive


def catalog_json() -> str:
    return json.dumps(CATALOG, indent=2, sort_keys=True)
