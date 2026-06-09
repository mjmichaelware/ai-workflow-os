from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
APP_NAME="Proof App"
APP_PROMPT="Create a proof app"
ROOT=Path(__file__).resolve().parent
def health_payload(): return {"ok": True, "app": APP_NAME, "prompt": APP_PROMPT}
class Handler(BaseHTTPRequestHandler):
    def send_json(self,payload,status=200):
        data=json.dumps(payload,indent=2).encode(); self.send_response(status); self.send_header("content-type","application/json"); self.send_header("content-length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def send_bytes(self,data,ctype,status=200):
        self.send_response(status); self.send_header("content-type",ctype); self.send_header("content-length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path=="/api/health": self.send_json(health_payload()); return
        if self.path.startswith("/static/"):
            rel=self.path.replace("/static/","",1); fp=ROOT/"web/static"/rel
            if fp.exists(): self.send_bytes(fp.read_bytes(), "text/css" if rel.endswith(".css") else "application/javascript"); return
        fp=ROOT/"web/index.html"; self.send_bytes(fp.read_bytes() if fp.exists() else ("<h1>"+APP_NAME+"</h1>").encode(), "text/html; charset=utf-8")
def run(host="127.0.0.1", port=8777):
    server=ThreadingHTTPServer((host,port),Handler); print(f"{APP_NAME}: http://{host}:{port}"); server.serve_forever()
if __name__=="__main__": run()
