from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
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
        return json.loads(self.rfile.read(length).decode()) if length > 0 else {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            self.send_bytes((ROOT / "web/index.html").read_bytes(), "text/html; charset=utf-8"); return
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
                name = data.get("name", "generated-app")
                target = ROOT / "generated_apps" / name
                self.send_json(create_generated_app(data.get("prompt", ""), target, name=name, execute=bool(data.get("execute", False)))); return
            if self.path == "/api/test-app":
                self.send_json(test_app_by_name(ROOT, data.get("name", ""))); return
            if self.path == "/api/export-app-downloads":
                self.send_json(export_app_to_downloads(ROOT, data.get("name", ""), DOWNLOADS)); return
            if self.path == "/api/android/native-target":
                self.send_json(create_native_android_target(ROOT, data.get("name", "generated-android-app"), data.get("prompt", ""))); return
            self.send_json({"error": "not_found", "path": self.path}, status=404)
        except Exception as exc:
            self.send_json({"error": "exception", "message": str(exc)}, status=500)

def run_server(host="127.0.0.1", port=8765):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"AI Workflow OS dashboard: http://{host}:{port}")
    server.serve_forever()
