from __future__ import annotations

from pathlib import Path
import datetime
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ("GitHub Actions workflow syntax", "https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax"),
    ("Code scanning", "https://docs.github.com/en/code-security/concepts/code-scanning/code-scanning"),
    ("Repository custom instructions", "https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions"),
    ("Dependabot alerts", "https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-alerts"),
]

def fetch_title(url: str) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Workflow-OS-Research"})
        with urllib.request.urlopen(req, timeout=12) as response:
            text = response.read(120000).decode("utf-8", errors="replace")
        start = text.lower().find("<title>")
        end = text.lower().find("</title>", start)
        title = text[start + 7:end].strip() if start != -1 and end != -1 else ""
        return {"ok": True, "url": url, "title": title}
    except Exception as exc:
        return {"ok": False, "url": url, "error": str(exc)}

def main() -> int:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows = [{"name": name, **fetch_title(url)} for name, url in SOURCES]
    data = {"ok": True, "created_at": now, "sources": rows, "direction": ["Small explicit workflows", "Code security by default", "Repository instructions for agents", "Dependency risk visibility", "Agentic proof loops", "Local-first generated-app inheritance"]}
    out_json = ROOT / "docs" / "research" / "developer_direction_2026.json"
    out_md = ROOT / "docs" / "research" / "DEVELOPER_DIRECTION_2026.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    lines = ["# Developer Direction 2026", "", "This snapshot is generated from terminal-side research. Browser UI remains local-only.", "", "## Direction", ""]
    for item in data["direction"]:
        lines.append("- " + item)
    lines += ["", "## Source checks", ""]
    for row in rows:
        lines.append("- " + row["name"] + ": " + ("ok" if row["ok"] else "unavailable"))
    out_md.write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    print(json.dumps({"ok": True, "created_at": now, "sources_checked": len(rows), "json": str(out_json), "markdown": str(out_md)}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
