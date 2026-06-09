from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import urllib.parse

from .catalog import CATALOG
from .core import scan_project
from .permissions import default_policy_json
from .providers import list_providers

ROOT = Path(__file__).resolve().parents[1]

class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        data = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_text(self, text, status=200):
        data = text.encode()
        self.send_response(status)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/":
            index = ROOT / "web/index.html"
            self.send_text(index.read_text() if index.exists() else "<h1>AI Workflow OS</h1>")
            return
        if path == "/api/health":
            self.send_json({"ok": True, "service": "ai-workflow-os"})
            return
        if path == "/api/catalog":
            self.send_json(CATALOG)
            return
        if path == "/api/providers":
            self.send_json({"providers": list_providers()})
            return
        if path == "/api/permissions":
            self.send_json(default_policy_json())
            return
        if path == "/api/workflow-files":
            files = []
            for base in ["workflow", "standards", "docs", "scripts", "ai_workflow_os"]:
                folder = ROOT / base
                if folder.exists():
                    for item in sorted(folder.glob("**/*")):
                        if item.is_file():
                            files.append(str(item.relative_to(ROOT)))
            self.send_json({"files": files})
            return
        if path == "/api/status":
            query = urllib.parse.parse_qs(parsed.query)
            target = Path(query.get("target", ["."])[0])
            self.send_json(scan_project(target).__dict__)
            return
        self.send_json({"error": "not_found", "path": path}, status=404)

def run_server(host="127.0.0.1", port=8765):
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"AI Workflow OS dashboard: http://{host}:{port}")
    server.serve_forever()
