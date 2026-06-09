
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "research"
OUT.mkdir(parents=True, exist_ok=True)

QUERIES = [
    "topic:github-actions language:Python stars:>100",
    "topic:codeql stars:>100",
    "topic:devcontainer stars:>100",
    "topic:pwa stars:>100",
    "topic:termux stars:>50",
    "topic:agentic-ai stars:>10",
    "topic:ai-agents stars:>100",
    "claude code agent stars:>10",
    "codex cli agent stars:>10",
    "gemini cli stars:>10",
    "cline ai agent stars:>10",
    "continue dev ai stars:>10",
]

def run_gh(query: str) -> dict:
    if not shutil.which("gh"):
        return {"ok": False, "query": query, "error": "gh not installed"}
    cmd = ["gh", "api", "search/repositories", "-f", "q=" + query, "-f", "sort=stars", "-f", "order=desc", "-f", "per_page=5"]
    try:
        p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        if p.returncode != 0:
            return {"ok": False, "query": query, "error": p.stderr.strip()}
        data = json.loads(p.stdout)
        items = []
        for item in data.get("items", []):
            items.append({
                "full_name": item.get("full_name"),
                "html_url": item.get("html_url"),
                "description": item.get("description"),
                "stars": item.get("stargazers_count"),
                "language": item.get("language"),
                "topics": item.get("topics", []),
            })
        return {"ok": True, "query": query, "items": items}
    except Exception as exc:
        return {"ok": False, "query": query, "error": str(exc)}

def main() -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    rows = [run_gh(q) for q in QUERIES]
    raw = OUT / ("github_landscape_" + stamp + ".json")
    raw.write_text(json.dumps({"created_at": stamp, "queries": rows}, indent=2), encoding="utf-8")
    lines = [
        "# Public Landscape Snapshot",
        "",
        "Generated from GitHub repository search using gh api. This is a signal snapshot, not a claim of completeness.",
        "",
        "## What AI Workflow OS watches",
        "",
        "- GitHub Actions and CodeQL for contribution quality",
        "- Devcontainers and Codespaces for cross-device contributor onboarding",
        "- PWA and Termux for phone-first local execution",
        "- Agentic AI tools including Claude Code, Codex, Gemini CLI, Cline, Continue, and Copilot-compatible workflows",
        "",
    ]
    for row in rows:
        lines.append("## " + row["query"])
        if not row.get("ok"):
            lines.append("- ERROR: " + row.get("error", "unknown"))
            lines.append("")
            continue
        for item in row.get("items", []):
            lines.append("- " + item.get("full_name", "") + " — " + str(item.get("stars", 0)) + " stars — " + item.get("html_url", ""))
        lines.append("")
    (OUT / "PUBLIC_LANDSCAPE.md").write_text(chr(10).join(lines), encoding="utf-8")
    print(raw)
    print(OUT / "PUBLIC_LANDSCAPE.md")

if __name__ == "__main__":
    main()
