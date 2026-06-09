from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_final_release_hardening_files_exist():
    assert (ROOT / "scripts" / "final_release_hardening.py").exists()
    assert (ROOT / "docs" / "release" / "RELEASE_NOTES_V1.md").exists()
    assert (ROOT / "docs" / "standards" / "FINAL_RELEASE_HARDENING_V1_STANDARD.md").exists()


def test_final_release_mentions_core_capabilities():
    text = (ROOT / "docs" / "release" / "RELEASE_NOTES_V1.md").read_text(encoding="utf-8")
    assert "Agent-routed builder" in text
    assert "Recursive app factory proof to depth 4" in text
    assert "APK build/sign scaffold" in text
