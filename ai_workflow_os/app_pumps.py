from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import json
import hashlib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + chr(10), encoding="utf-8")

def boundary_manifest() -> Dict[str, Any]:
    data = {"ok": True, "kind": "operating_boundary", "updated_at": now(), "os_role": "self-building application builder", "generated_app_role": "material app output with inherited guardrails", "inside_out": "OS standards generate app structure", "outside_in": "Observed app failures update OS knowledge and future templates", "backwards": "Failures become prevention rules", "must_not_shadow": ["ai_workflow_os/core.py with ai_workflow_os/core/"]}
    write_json(ROOT / "ai_workflow_os" / "registries" / "operating_boundary.json", data)
    return data

def pump_manifest() -> Dict[str, Any]:
    pumps = ["os.state", "events", "actions", "ui.buttons", "generated.apps", "tests", "knowledge.archive", "mistake.prevention", "libraries", "import.export"]
    data = {"ok": True, "kind": "pump_manifest", "updated_at": now(), "count": len(pumps), "pumps": pumps}
    write_json(ROOT / "ai_workflow_os" / "registries" / "pumps.json", data)
    return data

def standards_audit() -> Dict[str, Any]:
    required = ["NO_FRAGILE_PASTE_PROTOCOL.md", "AGENT_MISTAKE_REGISTRY.md", "OPERATING_SYSTEM_APP_BOUNDARY.md", "SELF_BUILDING_PUMP_STANDARD.md", "GENERATED_APP_INHERITANCE_STANDARD.md", "OPERATING_MEMORY_STANDARD.md", "NO_HEREDOC_CORE_BUILD_STANDARD.md"]
    items = []
    for name in required:
        path = ROOT / "docs" / "standards" / name
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        items.append({"path": str(path.relative_to(ROOT)), "exists": path.exists(), "hash": sha_text(text) if path.exists() else None})
    data = {"ok": all(i["exists"] for i in items), "kind": "standards_audit", "updated_at": now(), "items": items}
    write_json(ROOT / "ai_workflow_os" / "registries" / "standards.json", data)
    return data

def generated_app_preflight() -> Dict[str, Any]:
    roots = [ROOT / "generated_apps", ROOT / "apps"]
    apps: List[Dict[str, Any]] = []
    for base in roots:
        if not base.exists():
            continue
        for app in sorted([p for p in base.iterdir() if p.is_dir()]):
            files = [p.relative_to(app).as_posix() for p in app.rglob("*") if p.is_file()]
            apps.append({"name": app.name, "root": str(app.relative_to(ROOT)), "has_python_app": any(x.endswith("app.py") for x in files), "has_web_ui": any(x.startswith("web/") or x.endswith("index.html") for x in files), "has_test": any("test" in x.lower() for x in files), "file_count": len(files)})
    data = {"ok": True, "kind": "generated_app_preflight", "updated_at": now(), "generated_app_count": len(apps), "apps": apps, "inherited_rules": ["no fake proof", "no silent button failure", "no secret printing", "runtime proof required", "compile proof required", "no module package shadowing", "no heredoc core build"]}
    write_json(ROOT / "ai_workflow_os" / "registries" / "generated_app_preflight.json", data)
    return data

def mistake_prevention_manifest() -> Dict[str, Any]:
    rules = ["no heredoc for core builds", "no module package shadowing", "compile proof is not runtime proof", "registry button must have registered action", "no fake proof", "no silent failure", "no secret print or commit"]
    data = {"ok": True, "kind": "mistake_prevention_manifest", "updated_at": now(), "rules": rules}
    write_json(ROOT / "ai_workflow_os" / "registries" / "mistake_prevention.json", data)
    return data

def operating_memory_manifest() -> Dict[str, Any]:
    layers = ["current state", "event journal", "action result", "local persistence", "proof files", "audit judgment", "mistake registry", "generated app inheritance", "archived stale knowledge", "promoted current knowledge"]
    data = {"ok": True, "kind": "operating_memory_manifest", "updated_at": now(), "layers": layers}
    write_json(ROOT / "ai_workflow_os" / "registries" / "operating_memory.json", data)
    return data
