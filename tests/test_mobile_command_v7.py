
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_mobile_command_assets_are_wired():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert "/assets/mobile-command-v7.css" in html
    assert "/assets/mobile-command-v7.js" in html

def test_mobile_command_css_has_full_menu_and_motion():
    css = (ROOT / "web" / "assets" / "mobile-command-v7.css").read_text(encoding="utf-8")
    assert "AIWOS_MOBILE_COMMAND_V7" in css
    assert "mobile-menu-sheet" in css
    assert "mobile-menu-grid" in css
    assert "@keyframes v7-neon-breath" in css
    assert "@keyframes v7-card-enter" in css
    assert "@media(max-width:760px)" in css

def test_mobile_command_js_has_all_tab_menu():
    js = (ROOT / "web" / "assets" / "mobile-command-v7.js").read_text(encoding="utf-8")
    assert "AIWOS_MOBILE_COMMAND_V7_JS" in js
    assert "buildMobileCommandMenu" in js
    assert "data-mobile-tab" in js
    assert "runtime" in js
    assert "license" in js

def test_mobile_command_standard_exists():
    assert (ROOT / "docs" / "standards" / "MOBILE_COMMAND_SURFACE_V7_STANDARD.md").exists()
