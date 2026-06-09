from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
# REGISTRY_BUTTONS_PATCH_V1
from .registry_spine import build_registry, dispatch
from .terminal_bridge import list_terminal_commands, run_terminal_command
from .prompt_bridge import bridge_manifest, submit_prompt, approve_prompt, complete_prompt, list_prompts, next_approved_prompt
from .self_build_executor import self_build_manifest, run_next_self_build
from .phone_wrapper import phone_manifest, phone_status, export_phone_bundle, create_launcher
from .operator_console import operator_manifest, operator_status, operator_run, operator_publish, operator_apps, operator_apps
from .runtime_console import runtime_console_payload
import urllib.parse

from .android_builder import android_status, create_native_android_target
from .app_builder import create_generated_app
from .app_index import list_generated_apps, test_app_by_name, export_app_to_downloads
from .catalog import CATALOG
from .core import scan_project
from .permissions import default_policy_json
from .providers import list_providers
from .research_graph import MarketResearchGraph, build_research_queries
from .self_bootstrap import save_self_bootstrap_plan
from .tools import tool_inventory

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path.home() / "storage/downloads"


# REGISTRY_DASHBOARD_INJECTOR_V1
def _registry_panel_html() -> str:
    return """
<section id="registry-actions-panel" style="border:1px solid #555;padding:12px;margin:12px 0;border-radius:12px">
  <h2>Registry Actions</h2>
  <p>These buttons are loaded from the action registry. A button without a registered action is not real.</p>
  <div id="registry-action-buttons"></div>
  <pre id="registry-action-output">Registry action panel waiting...</pre>
</section>
<script>
(function(){
  async function registryLoad(){
    const out = document.getElementById("registry-action-output");
    const box = document.getElementById("registry-action-buttons");
    if(!out || !box) return;
    out.textContent = "Loading registry actions...";
    try {
      const r = await fetch("/api/actions", {cache:"no-store"});
      const data = await r.json();
      box.innerHTML = "";
      (data.actions || []).forEach(action => {
        const b = document.createElement("button");
        b.textContent = action.label || action.id;
        b.dataset.actionId = action.id;
        b.style.margin = "4px";
        b.onclick = async () => {
          out.textContent = "Running " + action.id + "...";
          const rr = await fetch("/api/actions/run", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({action_id: action.id, payload: {}})
          });
          const result = await rr.json();
          out.textContent = JSON.stringify(result, null, 2);
        };
        box.appendChild(b);
      });
      out.textContent = "Registry buttons loaded: " + (data.actions || []).length;
    } catch(e) {
      out.textContent = "Registry button load failed: " + e.message;
    }
  }
  window.addEventListener("DOMContentLoaded", registryLoad);
})();
</script>
"""

def _inject_registry_panel(html: str) -> str:
    if not isinstance(html, str):
        return html
    if "registry-action-buttons" in html:
        return html
    panel = _registry_panel_html()
    lower = html.lower()
    idx = lower.rfind("</body>")
    if idx >= 0:
        return html[:idx] + panel + "\n" + html[idx:]
    return html + "\n" + panel

class Handler(BaseHTTPRequestHandler):
    def _no_cache_headers(self):
        self.send_header("cache-control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("pragma", "no-cache")
        self.send_header("expires", "0")
        self.send_header("x-aiwos-build", "no-cache-stage")

    def send_json(self, payload, status=200):
        data = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(data)))
        self._no_cache_headers()
        self.end_headers()
        self.wfile.write(data)

    def send_bytes(self, data, content_type, status=200):
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(data)))
        self._no_cache_headers()
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("content-length", "0"))
        return json.loads(self.rfile.read(length).decode()) if length > 0 else {}

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path == "/legacy-dashboard.html":
            self.send_bytes((ROOT / "web" / "legacy-dashboard.html").read_bytes(), "text/html; charset=utf-8")
            return
        if path == "/manifest.webmanifest":
            self.send_bytes((ROOT / "web" / "manifest.webmanifest").read_bytes(), "application/manifest+json; charset=utf-8")
            return

        if path.startswith("/assets/"):
            asset = (ROOT / "web" / path.lstrip("/")).resolve()
            web_root = (ROOT / "web").resolve()
            if str(asset).startswith(str(web_root)) and asset.exists() and asset.is_file():
                if asset.suffix == ".css":
                    self.send_bytes(asset.read_bytes(), "text/css; charset=utf-8")
                    return
                if asset.suffix == ".js":
                    self.send_bytes(asset.read_bytes(), "application/javascript; charset=utf-8")
                    return
                if asset.suffix == ".json":
                    self.send_bytes(asset.read_bytes(), "application/json; charset=utf-8")
                    return
        if path == "/sw.js":
            self.send_bytes((ROOT / "web" / "sw.js").read_bytes(), "application/javascript; charset=utf-8")
            return

        if path.startswith("/icons/"):
            icon_path = (ROOT / "web" / path.lstrip("/"))
            if icon_path.exists() and icon_path.is_file():
                self.send_bytes(icon_path.read_bytes(), "image/png")
                return

        if path == "/api/operator/manifest":
            self.send_json(operator_manifest())
            return

        if path == "/api/runtime/console":
            self.send_json(runtime_console_payload())
            return

        if path == "/api/operator/apps":
            self.send_json(operator_apps())
            return

        if path == "/api/operator/status":
            self.send_json(operator_status())
            return
        if path == "/api/phone/manifest":
            self.send_json(phone_manifest())
            return

        if path == "/api/phone/status":
            self.send_json(phone_status())
            return
        if path == "/api/self-build/manifest":
            self.send_json(self_build_manifest())
            return
        if path == "/api/prompts":
            self.send_json(list_prompts())
            return

        if path == "/api/prompts/manifest":
            self.send_json(bridge_manifest())
            return

        if path == "/api/prompts/next-approved":
            self.send_json(next_approved_prompt())
            return
        if path == "/api/terminal/commands":
            self.send_json(list_terminal_commands())
            return
        if path == "/api/actions":
            registry = build_registry()
            self.send_json(registry.manifest())
            return

        if path == "/api/action-events":
            from pathlib import Path
            root = Path(__file__).resolve().parents[1]
            events = root / "ai_workflow_os" / "persistence" / "events.jsonl"
            audit = root / "ai_workflow_os" / "audit" / "audit.jsonl"
            self.send_json({
                "ok": True,
                "events_path": str(events),
                "audit_path": str(audit),
                "events_exists": events.exists(),
                "audit_exists": audit.exists(),
                "events_tail": events.read_text(encoding="utf-8").splitlines()[-20:] if events.exists() else [],
                "audit_tail": audit.read_text(encoding="utf-8").splitlines()[-20:] if audit.exists() else [],
            })
            return


        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            self.send_bytes((ROOT / "web/index.html").read_bytes(), "text/html; charset=utf-8"); return
        if path == "/sw.js":
            self.send_bytes((ROOT / "web" / "sw.js").read_bytes(), "application/javascript; charset=utf-8")
            return

        if path.startswith("/icons/"):
            icon_path = (ROOT / "web" / path.lstrip("/"))
            if icon_path.exists() and icon_path.is_file():
                self.send_bytes(icon_path.read_bytes(), "image/png")
                return
        if path == "/manifest.webmanifest":
            self.send_bytes((ROOT / "web/manifest.webmanifest").read_bytes(), "application/manifest+json"); return
        if path == "/service-worker.js":
            self.send_bytes((ROOT / "web/service-worker.js").read_bytes(), "application/javascript"); return
        if path.startswith("/static/"):
            rel = path.replace("/static/", "", 1)
            fp = ROOT / "web/static" / rel
            if fp.exists():
                ctype = "text/css" if rel.endswith(".css") else "application/javascript"
                self.send_bytes(fp.read_bytes(), ctype); return
        if path == "/api/health": self.send_json({"ok": True, "service": "ai-workflow-os"}); return
        if path == "/api/catalog": self.send_json(CATALOG); return
        if path == "/api/providers": self.send_json({"providers": list_providers()}); return
        if path == "/api/permissions": self.send_json(default_policy_json()); return
        if path == "/api/tools": self.send_json(tool_inventory()); return
        if path == "/api/generated-apps": self.send_json(list_generated_apps(ROOT)); return
        if path == "/api/android/status": self.send_json(android_status()); return
        if path == "/api/status": self.send_json(scan_project(ROOT).__dict__); return
        self.send_json({"error": "not_found", "path": path}, status=404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]

        if path == "/api/operator/run":
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                body = json.loads(raw or "{}")
                self.send_json(operator_run(body.get("prompt", ""), bool(body.get("publish", False))))
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return

        if path == "/api/operator/publish":
            try:
                self.send_json(operator_publish("Operator build"))
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return
        if path == "/api/phone/export":
            try:
                self.send_json(export_phone_bundle())
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return

        if path == "/api/phone/create-launcher":
            try:
                self.send_json(create_launcher())
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return
        if path == "/api/self-build/run-next":
            try:
                self.send_json(run_next_self_build())
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return
        if path == "/api/prompts/submit":
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                body = json.loads(raw or "{}")
                self.send_json(submit_prompt(body.get("prompt", ""), body.get("source", "dashboard"), body.get("target", "self_build")))
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return

        if path == "/api/prompts/approve":
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                body = json.loads(raw or "{}")
                self.send_json(approve_prompt(body.get("prompt_id", ""), bool(body.get("approved", True))))
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return

        if path == "/api/prompts/complete":
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                body = json.loads(raw or "{}")
                self.send_json(complete_prompt(body.get("prompt_id", ""), body.get("result", {})))
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return
        if path == "/api/terminal/run":
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                body = json.loads(raw or "{}")
                command_id = body.get("command_id")
                if not command_id:
                    self.send_json({"ok": False, "error": "missing command_id"}, status=400)
                    return
                self.send_json(run_terminal_command(command_id))
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return
        if path == "/api/actions/run":
            try:
                length = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                body = json.loads(raw or "{}")
                action_id = body.get("action_id")
                payload = body.get("payload") or {}
                if not action_id:
                    self.send_json({"ok": False, "error": "missing action_id"}, status=400)
                    return
                result = dispatch(action_id, payload, source="dashboard")
                self.send_json(result)
                return
            except Exception as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=500)
                return


        try:
            path = urllib.parse.urlparse(self.path).path
            data = self.read_json()
            if path == "/api/research-graph":
                self.send_json(MarketResearchGraph().build_seed_graph(data.get("prompt", ""))); return
            if path == "/api/research-queries":
                self.send_json(build_research_queries(data.get("prompt", ""), max_depth=int(data.get("depth", 2)))); return
            if path == "/api/self-bootstrap":
                out = ROOT / "runs/self_bootstrap_ui"
                self.send_json({"self_bootstrap_plan": str(save_self_bootstrap_plan(ROOT, data.get("prompt", ""), out))}); return
            if path == "/api/create-app":
                name = data.get("name", "generated-app")
                target = ROOT / "generated_apps" / name
                self.send_json(create_generated_app(data.get("prompt", ""), target, name=name, execute=bool(data.get("execute", False)))); return
            if path == "/api/test-app":
                self.send_json(test_app_by_name(ROOT, data.get("name", ""))); return
            if path == "/api/export-app-downloads":
                self.send_json(export_app_to_downloads(ROOT, data.get("name", ""), DOWNLOADS)); return
            if path == "/api/android/native-target":
                self.send_json(create_native_android_target(ROOT, data.get("name", "generated-android-app"), data.get("prompt", ""))); return
            self.send_json({"error": "not_found", "path": path}, status=404)
        except Exception as exc:
            self.send_json({"error": "exception", "message": str(exc)}, status=500)

def run_server(host="127.0.0.1", port=8765):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"AI Workflow OS dashboard: http://{host}:{port}")
    server.serve_forever()

# Registry action panel marker installed; HTML injection target not found.
