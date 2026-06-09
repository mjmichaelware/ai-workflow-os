
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_runtime_console_assets_exist():
    for rel in [
        "ai_workflow_os/runtime_console.py",
        "web/assets/runtime-console.js",
        "web/assets/ux-density-v5.css",
        "web/assets/verbose-pages.data.json",
        "docs/standards/RUNTIME_CONSOLE_UX_DENSITY_STANDARD.md",
    ]:
        assert (ROOT / rel).exists()

def test_runtime_console_is_wired():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "web" / "assets" / "console.js").read_text(encoding="utf-8")
    runtime = (ROOT / "web" / "assets" / "runtime-console.js").read_text(encoding="utf-8")
    assert "/assets/runtime-console.js" in html
    assert "/assets/ux-density-v5.css" in html
    assert "id:\"runtime\"" in js
    assert "AIWOS_RUNTIME_CONSOLE_V1" in runtime
    assert "/api/runtime/console" in runtime

def test_verbose_pages_are_large_enough():
    data = json.loads((ROOT / "web" / "assets" / "verbose-pages.data.json").read_text(encoding="utf-8"))
    assert len(data["about"]) >= 50
    assert len(data["privacy"]) >= 50
    assert len(data["license"]) >= 35
