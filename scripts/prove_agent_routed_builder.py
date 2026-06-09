
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = Path.home() / "tmp"


def request_json(path: str, payload: dict | None = None) -> dict:
    url = "http://127.0.0.1:8765" + path
    if payload is None:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    prompt = (
        "Create an agent-routed proof app named agent-routed-proof-" + stamp + ". "
        "Use Gemini and Claude local model CLIs if installed to draft a safe implementation plan. "
        "Save drafts. Do not print secrets. Do not request broad permissions. "
        "Keep the generated app inspectable and shell-inherited."
    )
    build = request_json("/api/operator/run", {"prompt": prompt, "publish": False})
    apps = build.get("created_apps", [])
    if not build.get("ok") or not apps:
        print(json.dumps({"ok": False, "stage": "operator_run", "build": build}, indent=2))
        return 1

    app = Path(apps[0]["path"])
    route_path = app / "agent_drafts" / "AGENT_ROUTE.json"
    manifest_path = app / "APP_MANIFEST.json"
    route = json.loads(route_path.read_text(encoding="utf-8")) if route_path.exists() else {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    installed_prompt_agents = [
        item.get("tool")
        for item in route.get("agents", [])
        if item.get("tool") in {"gemini", "claude"} and item.get("installed")
    ]
    used_agents = route.get("used_agents", [])

    archive = ARCHIVE_ROOT / ("aiwos_agent_routed_builder_proof_" + stamp)
    archive.mkdir(parents=True, exist_ok=True)

    result = {
        "ok": bool(
            route_path.exists()
            and manifest_path.exists()
            and route.get("ok")
            and manifest.get("agent_routed_builder_v1", {}).get("ok")
            and (not installed_prompt_agents or bool(used_agents))
        ),
        "generated_app": apps[0].get("name"),
        "route_file": str(route_path),
        "installed_prompt_agents": installed_prompt_agents,
        "used_agents": used_agents,
        "successful_agents": route.get("successful_agents", []),
        "agent_count": len(route.get("agents", [])),
        "keys_printed": False,
        "broad_permissions": False,
        "archive": str(archive),
    }
    if app.exists():
        shutil.move(str(app), str(archive / app.name))
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
