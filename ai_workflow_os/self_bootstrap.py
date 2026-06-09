from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time
from typing import Dict, List

from .research_graph import MarketResearchGraph, build_research_queries

@dataclass
class BootstrapStage:
    id: str
    title: str
    purpose: str
    approval_required: bool

class SelfBootstrapPlanner:
    def create_plan(self, repo_root: Path, prompt: str) -> Dict[str, object]:
        repo_root = repo_root.resolve()
        stages: List[BootstrapStage] = [
            BootstrapStage("B0", "Declare boundary", "Improve AI Workflow OS only. Do not contaminate target apps.", False),
            BootstrapStage("B1", "Inspect self", "Inspect repo, CLI, dashboard, docs, adapters, and proof scripts.", False),
            BootstrapStage("B2", "Build research graph", "Map market categories, patterns, APIs, CLIs, and app-builder ideas.", False),
            BootstrapStage("B3", "Design next adapters", "Plan approved web, GitHub, package, model, and local-runtime adapters.", True),
            BootstrapStage("B4", "Generate self patch plan", "Write an evidence-backed plan for improving this OS.", True),
            BootstrapStage("B5", "Patch self", "Apply approved improvements to this repo only.", True),
            BootstrapStage("B6", "Proof self", "Compile, verify CLI, verify UI endpoints, and write proof report.", True),
            BootstrapStage("B7", "Commit self", "Commit proven self improvements.", True),
        ]
        return {
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "repo_root": str(repo_root),
            "prompt": prompt,
            "principle": "The app creator can create and improve itself through the same gated workflow it applies to target apps.",
            "hard_limits": [
                "No fake claim of searching the entire web without approved live research adapters.",
                "No secret values are printed.",
                "No cloud writes or deploys without explicit approval.",
                "Target app data never belongs in the generic OS repo.",
            ],
            "research_graph": MarketResearchGraph().build_seed_graph(prompt),
            "research_queries": build_research_queries(prompt, max_depth=3),
            "bootstrap_stages": [asdict(stage) for stage in stages],
        }

def save_self_bootstrap_plan(repo_root: Path, prompt: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    plan = SelfBootstrapPlanner().create_plan(repo_root, prompt)
    path = out_dir / "self_bootstrap_plan.json"
    path.write_text(json.dumps(plan, indent=2))
    md = ["# Self Bootstrap Plan", "", plan["principle"], "", "Prompt:", "", prompt, "", "Stages:"]
    for stage in plan["bootstrap_stages"]:
        gate = "approval required" if stage["approval_required"] else "auto"
        md.append("- " + stage["id"] + " " + stage["title"] + " [" + gate + "]: " + stage["purpose"])
    (out_dir / "self_bootstrap_plan.md").write_text("\n".join(md) + "\n")
    return path
