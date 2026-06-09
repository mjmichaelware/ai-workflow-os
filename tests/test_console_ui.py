from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_console_ui_has_real_actions_and_pages():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    for item in [
        "data-action=\"build\"",
        "data-action=\"status\"",
        "data-action=\"export\"",
        "data-action=\"apps\"",
        "data-tab=\"overview\"",
        "data-tab=\"build\"",
        "data-tab=\"apps\"",
        "data-tab=\"about\"",
        "data-tab=\"privacy\"",
        "data-tab=\"license\"",
        "operator/run",
        "operator/apps",
        "phone/export",
        "operator/status",
    ]:
        assert item in html

def test_console_ui_is_brand_neutral_and_local_only():
    text = (ROOT / "web" / "index.html").read_text(encoding="utf-8").lower()
    banned = ["google-cloud-style", "google cloud style", "google cloud console", "google-console", "google-style"]
    for phrase in banned:
        assert phrase not in text
    assert "infrastructure-grade" in text
    assert "connect-src " in text
    assert "self" in text

def test_public_docs_exist():
    for rel in [
        "LICENSE",
        "PRIVACY.md",
        "docs/ABOUT.md",
        "docs/SECURITY_BOUNDARY.md",
        "docs/PRODUCT_REQUIREMENTS.md",
        "docs/UX_PRINCIPLES.md",
        "docs/standards/APP_FACTORY_CONTRACT_STANDARD.md",
    ]:
        assert (ROOT / rel).exists()
