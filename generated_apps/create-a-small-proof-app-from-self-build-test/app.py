from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
APP_NAME = 'create-a-small-proof-app-from-self-build-test'
PROMPT = 'Create a small proof app from self build test'
class Handler(BaseHTTPRequestHandler):
    def _send(self, data, status=200):
        raw = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        if self.path.startswith("/api/health"):
            self._send({"ok": True, "app": APP_NAME, "prompt": PROMPT})
        else:
            self._send({"ok": True, "app": APP_NAME, "endpoints": ["/api/health"]})
def main():
    ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
if __name__ == "__main__":
    main()
