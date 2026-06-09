
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_editorial_assets_are_wired():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert "/assets/editorial-ux-v6.css" in html
    assert "/assets/editorial-pages.js" in html
    assert "/assets/native-app-mode.js" in html

def test_editorial_data_is_not_repeated_filler():
    data = json.loads((ROOT / "web" / "assets" / "page-content-v2.data.json").read_text(encoding="utf-8"))
    for key, minimum in [("about", 18), ("privacy", 18), ("license", 8)]:
        items = data[key]
        titles = [item["title"] for item in items]
        bodies = [item["body"] for item in items]
        assert len(items) >= minimum
        assert len(set(titles)) == len(titles)
        assert len(set(bodies)) == len(bodies)

def test_editorial_standard_exists():
    assert (ROOT / "docs" / "standards" / "EDITORIAL_UX_V6_STANDARD.md").exists()
