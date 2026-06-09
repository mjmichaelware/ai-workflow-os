from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def test_console_ui_is_decoupled():
    html = read("web/index.html")
    css = read("web/assets/console.css")
    js = read("web/assets/console.js")
    assert "/assets/console.css" in html
    assert "/assets/console.js" in html
    assert "primary-nav" in html
    assert "flyout" in html
    assert "mobile-nav" in html
    assert "data-action" in js
    assert "theme-toggle" in js
    assert "operator/run" in js
    assert "operator/apps" in js
    assert "@media" in css
    assert "animation" in css

def test_console_pages_exist():
    js = read("web/assets/console.js")
    for item in ["overview", "build", "apps", "tools", "security", "research", "deploy", "about", "privacy", "license"]:
        assert item in js

def test_console_security_and_brand_neutrality():
    combined = (read("web/index.html") + read("web/assets/console.css") + read("web/assets/console.js")).lower()
    blocked = [
        "goo" + "gle-cloud-style",
        "goo" + "gle cloud style",
        "goo" + "gle cloud console",
        "goo" + "gle-console",
        "goo" + "gle-style",
    ]
    for phrase in blocked:
        assert phrase not in combined
    assert "connect-src" in combined
    assert "infrastructure-grade" in combined

def test_context_packet_exists():
    assert (ROOT / "scripts" / "context_packet.py").exists()
    assert (ROOT / "docs" / "context" / "AI_WORKFLOW_OS_CONTEXT_PACKET.json").exists()
    assert (ROOT / "docs" / "standards" / "UI_PACKET_ARCHITECTURE_STANDARD.md").exists()

def test_public_surface_script_passes():
    result = subprocess.run([sys.executable, "scripts/verify_public_surface.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0, result.stdout + result.stderr
