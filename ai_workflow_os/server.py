from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import urllib.parse

from .app_builder import create_generated_app
from .catalog import CATALOG
from .core import scan_project
from .permissions import default_policy_json
from .providers import list_providers
from .research_graph import MarketResearchGraph, build_research_queries
from .self_bootstrap import save_self_bootstrap_plan

try:
    from .runlog import list_runs
    from .tools import tool_inventory
except Exception:
    list_runs = None
    tool_inventory = None

ROOT = Path(__file__).resolve().parents[1]

class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        data = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_bytes(self, data, content_type, status=200):
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("content-length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode())

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/":
            self.send_bytes((ROOT / "web/index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if path.startswith("/static/"):
            rel = path.replace("/static/", "", 1)
            file_path = ROOT / "web/static" / rel
            if file_path.exists() and file_path.is_file():
                ctype = "text/css" if rel.endswith(".css") else "application/javascript" if rel.endswith(".js") else "text/plain"
                self.send_bytes(file_path.read_bytes(), ctype)
                return
        if path == "/api/health": self.send_json({"ok": True, "service": "ai-workflow-os"}); return
        if path == "/api/catalog": self.send_json(CATALOG); return
        if path == "/api/providers": self.send_json({"providers": list_providers()}); return
        if path == "/api/permissions": self.send_json(default_policy_json()); return
        if path == "/api/tools": self.send_json(tool_inventory() if tool_inventory else {"tools_module": False}); return
        if path == "/api/runs": self.send_json({"runs": list_runs(ROOT) if list_runs else []}); return
        if path == "/api/research-capabilities": self.send_json({"offline_seed_graph": True, "live_web_research": "requires approved adapter", "self_bootstrap": True, "claims_entire_web": False}); return
        if path == "/api/workflow-files":
            files = []
            for base in ["workflow", "standards", "docs", "scripts", "ai_workflow_os", "policies", "web"]:
                folder = ROOT / base
                if folder.exists():
                    for item in sorted(folder.glob("**/*")):
                        if item.is_file(): files.append(str(item.relative_to(ROOT)))
            self.send_json({"files": files}); return
        if path == "/api/status":
            query = urllib.parse.parse_qs(parsed.query)
            self.send_json(scan_project(Path(query.get("target", ["."])[0])).__dict__); return
        self.send_json({"error": "not_found", "path": path}, status=404)

    def do_POST(self):
        try:
            data = self.read_json()
            if self.path == "/api/research-graph":
                self.send_json(MarketResearchGraph().build_seed_graph(data.get("prompt", ""))); return
            if self.path == "/api/research-queries":
                self.send_json(build_research_queries(data.get("prompt", ""), max_depth=int(data.get("depth", 2)))); return
            if self.path == "/api/self-bootstrap":
                out = ROOT / "runs/self_bootstrap_ui"
                self.send_json({"self_bootstrap_plan": str(save_self_bootstrap_plan(ROOT, data.get("prompt", ""), out))}); return
            if self.path == "/api/create-app":
                prompt = data.get("prompt", "")
                name = data.get("name", "")
                target = Path(data.get("target") or str(ROOT / "generated_apps" / "generated-app"))
                self.send_json(create_generated_app(prompt, target, name=name, execute=bool(data.get("execute", False)))); return
            self.send_json({"error": "not_found", "path": self.path}, status=404)
        except Exception as exc:
            self.send_json({"error": "exception", "message": str(exc)}, status=500)

def run_server(host="127.0.0.1", port=8765):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"AI Workflow OS dashboard: http://{host}:{port}")
    server.serve_forever()
