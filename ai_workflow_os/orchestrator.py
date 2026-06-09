from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time
from typing import List


@dataclass
class PlanStep:
    id: str
    title: str
    action_type: str
    description: str
    approval_required: bool
    command_hint: str = ""


@dataclass
class AgentPlan:
    run_id: str
    prompt: str
    target: str
    mode: str
    steps: List[PlanStep]

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "prompt": self.prompt,
            "target": self.target,
            "mode": self.mode,
            "steps": [asdict(step) for step in self.steps],
        }


class WorkflowAgent:
    def create_app_plan(self, prompt: str, target: str = ".", mode: str = "dry_run") -> AgentPlan:
        run_id = "run_" + time.strftime("%Y%m%d_%H%M%S")
        steps = [
            PlanStep("S0", "Create run folder", "write_files", "Create an isolated run record under runs/.", True),
            PlanStep("S1", "Inspect target repository", "inspect_repo", "Inspect files, routes, configs, package manifests, and existing workflow context.", False),
            PlanStep("S2", "Write app mission", "write_files", "Create or update app-specific APP_MISSION inside the target app, not inside AI Workflow OS.", True),
            PlanStep("S3", "Create canonical spec", "write_files", "Create canonical requirements and reconcile contradictions.", True),
            PlanStep("S4", "Create code map", "write_files", "Map frontend, backend, data flow, provider registry, auth, secrets, and deploy surfaces.", True),
            PlanStep("S5", "Create bug ledger", "write_files", "Record evidence-backed defects only.", True),
            PlanStep("S6", "Create patch plan", "write_files", "Plan patches before code edits.", True),
            PlanStep("S7", "Patch app", "execute_shell", "Patch surgically with approvals and proof gates.", True),
            PlanStep("S8", "Compile and proof", "execute_shell", "Compile and run safe local proof.", True),
            PlanStep("S9", "Commit proven work", "git_commit", "Commit only after proof passes.", True),
            PlanStep("S10", "Export handoff", "write_files", "Export handoff packet to a local output path.", True),
        ]
        return AgentPlan(run_id=run_id, prompt=prompt, target=str(Path(target).resolve()), mode=mode, steps=steps)


def save_plan(plan: AgentPlan, out_dir: Path) -> Path:
    run_dir = out_dir / plan.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = run_dir / "plan.json"
    plan_path.write_text(json.dumps(plan.to_dict(), indent=2))
    md = ["# Agent Run Plan", "", "Run ID: " + plan.run_id, "", "Prompt:", "", plan.prompt, "", "Steps:"]
    for step in plan.steps:
        approval = "approval required" if step.approval_required else "auto"
        md.append("- " + step.id + " " + step.title + " [" + approval + "]: " + step.description)
    (run_dir / "plan.md").write_text("\\n".join(md) + "\\n")
    return plan_path
