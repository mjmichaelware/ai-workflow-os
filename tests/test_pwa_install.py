import json
from pathlib import Path

def test_pwa_manifest_exists_and_is_installable():
    p = Path("web/manifest.webmanifest")
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["display"] == "standalone"
    assert data["start_url"].startswith("/")
    assert any(icon.get("sizes") == "512x512" for icon in data["icons"])

def test_pwa_icons_and_service_worker_exist():
    assert Path("web/sw.js").exists()
    assert Path("web/icons/ai-workflow-os-192.png").exists()
    assert Path("web/icons/ai-workflow-os-512.png").exists()
    assert Path("web/icons/ai-workflow-os-maskable-512.png").exists()

def test_index_links_manifest_and_service_worker():
    html = Path("web/index.html").read_text()
    js_path = Path("web/assets/console.js")
    js = js_path.read_text() if js_path.exists() else ""
    assert "/manifest.webmanifest" in html
    assert "navigator.serviceWorker.register" in (html + js)
