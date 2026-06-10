from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_has_stronger_product_positioning():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "phone-first local application factory" in text
    assert "repo-owned app builder" in text
    assert "prompt -> approval -> approved local action" in text
    assert "Debug APK artifact builds through GitHub Actions" in text


def test_readme_security_positioning():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Secrets are reported by presence only, not printed" in text
    assert "AI-assisted drafts without trusting raw agent output" in text


def test_readme_has_no_banned_positioning_phrases():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    banned = ["google cloud style", "google cloud console", "cloud-console-style", "google-console", "google-style"]
    for phrase in banned:
        assert phrase not in text
