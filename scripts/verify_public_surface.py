from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BROWSER_FILES = ["web/index.html", "web/assets/console.css", "web/assets/console.js", "web/assets/visual-system-v3.css", "web/assets/visual-max-v4.css", "web/assets/ux-density-v5.css", "web/assets/editorial-ux-v6.css", "web/assets/endpoint-graph.js", "web/assets/endpoint-graph.data.json", "web/assets/final-proof-dashboard.js", "web/assets/final-proof-dashboard.data.json", "web/assets/final-proof-dashboard.meta.json", "web/assets/runtime-console.js", "web/assets/editorial-pages.js", "web/assets/native-app-mode.js", "web/assets/verbose-pages.data.json", "web/assets/page-content-v2.data.json", "web/sw.js"]
PYTHON_FILES = ["ai_workflow_os/server.py", "ai_workflow_os/operator_console.py", "scripts/prove_operator_button_flow.py", "scripts/context_packet.py"]
SECRET_RE = re.compile(r"AIza[0-9A-Za-z_-]{20,}|sk-[0-9A-Za-z_-]{20,}|ghp_[0-9A-Za-z_]{20,}")
BROWSER_EXTERNAL_RE = re.compile(r"https?://|fonts\\.googleapis|cdn\\.jsdelivr|unpkg|cdnjs", re.I)
BANNED = ["goo" + "gle-cloud-style", "goo" + "gle cloud style", "goo" + "gle cloud console", "goo" + "gle-console", "goo" + "gle-style"]

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")

def main() -> int:
    failures = []
    for rel in BROWSER_FILES + PYTHON_FILES:
        path = ROOT / rel
        if not path.exists():
            failures.append("missing surface: " + rel)
            continue
        text = read(rel)
        lower = text.lower()
        for phrase in BANNED:
            if phrase in lower:
                failures.append("brand phrase in " + rel)
        if SECRET_RE.search(text):
            failures.append("secret-like token pattern in " + rel)
    for rel in BROWSER_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        text = read(rel)
        for match in BROWSER_EXTERNAL_RE.finditer(text):
            line_start = text.rfind(chr(10), 0, match.start()) + 1
            line_end = text.find(chr(10), match.start())
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end].strip()
            failures.append("browser external network reference in " + rel + ": " + line[:180])
    if failures:
        print("FAIL: public surface hygiene failed")
        for item in failures:
            print(item)
        return 1
    print("PASS: browser assets are local-only; executable surfaces are brand-neutral and secret-clean")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
