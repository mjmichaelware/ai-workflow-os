from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_github_actions_apk_workflow_exists():
    workflow = ROOT / ".github" / "workflows" / "android-debug-apk.yml"
    assert workflow.exists()
    text = workflow.read_text(encoding="utf-8")
    assert "Build Android Debug APK" in text
    assert "scripts/prove_real_apk_build.py" in text
    assert "actions/upload-artifact@v4" in text


def test_github_actions_apk_docs_exist():
    doc = ROOT / "docs" / "apk" / "GITHUB_ACTIONS_APK_BUILD.md"
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "No signing secrets" in text
    assert "GitHub Actions" in text
