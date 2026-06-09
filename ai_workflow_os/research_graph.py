from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List

@dataclass
class ResearchNode:
    id: str
    kind: str
    label: str
    rationale: str

@dataclass
class ResearchEdge:
    source: str
    target: str
    relation: str

class MarketResearchGraph:
    def build_seed_graph(self, prompt: str) -> Dict[str, object]:
        text = prompt.strip()
        lower = text.lower()
        nodes: List[ResearchNode] = [
            ResearchNode("prompt", "seed", text, "Original user application prompt."),
            ResearchNode("ai_app_builder", "category", "AI app builders", "Systems that create runnable apps from intent."),
            ResearchNode("agent_os", "category", "Agent operating systems", "Tool, model, permission, and workflow orchestration layers."),
            ResearchNode("low_code", "category", "Low-code and no-code platforms", "Related systems that compose apps from high-level instructions."),
            ResearchNode("cloud_ide", "category", "Cloud IDE automation", "Systems connecting files, terminal, git, deploy, and previews."),
            ResearchNode("prompt_to_app", "category", "Prompt-to-app workflows", "Natural language converted into files, APIs, UI, tests, and deployment plans."),
            ResearchNode("provider_registry", "pattern", "Provider registry", "Every model, API, CLI, storage, and search tool must be a typed adapter."),
            ResearchNode("permission_gate", "pattern", "Permission gates", "Dangerous actions require explicit approval manifests."),
            ResearchNode("self_inspection", "pattern", "Self inspection", "The app can inspect its own repo and generate improvement plans."),
            ResearchNode("recursive_bootstrap", "pattern", "Recursive bootstrap", "The system can apply its own workflow to improve itself."),
            ResearchNode("proof_first", "pattern", "Proof first execution", "Compile and proof gates precede commits and deployments."),
        ]
        if "phone" in lower or "termux" in lower or "terminal" in lower:
            nodes.append(ResearchNode("mobile_terminal", "constraint", "Mobile terminal first", "The system must work from Android Termux."))
        if "secret" in lower or "credential" in lower or "api" in lower:
            nodes.append(ResearchNode("secret_manager", "constraint", "Secret Manager first", "Credentials must be referenced safely and never printed."))
        if "offline" in lower:
            nodes.append(ResearchNode("offline_adapter", "constraint", "Offline model adapter", "Offline mode requires local model runtimes, not cloud APIs."))
        edges = [ResearchEdge("prompt", node.id, "suggests") for node in nodes if node.id != "prompt"]
        return {
            "prompt": text,
            "mode": "offline_seed_graph",
            "limitation": "This is a bounded research graph. Live market research requires approved adapters.",
            "nodes": [asdict(node) for node in nodes],
            "edges": [asdict(edge) for edge in edges],
        }

def build_research_queries(prompt: str, max_depth: int = 2) -> Dict[str, object]:
    base = prompt.strip()
    return {
        "prompt": base,
        "max_depth": max_depth,
        "queries": [
            base,
            "AI app builder agent platform terminal CLI",
            "prompt to app generator architecture",
            "agent operating system tool registry permission model",
            "low code AI app generation workflow",
            "self improving software agent repository inspection",
            "mobile terminal development workflow Termux AI agent",
            "application generator import export internal testing architecture",
        ],
        "execution": "planned_only",
        "approval_required_for_live_web": True,
    }
