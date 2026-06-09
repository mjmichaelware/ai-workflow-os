from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_real_apk_project_module_exists():
    text = (ROOT / "ai_workflow_os" / "real_apk_project.py").read_text(encoding="utf-8")
    assert "create_real_apk_project" in text
    assert "attempt_debug_apk_build" in text
    assert "WebView" in text
    assert "keys_printed" in text


def test_real_apk_build_proof_exists():
    assert (ROOT / "scripts" / "prove_real_apk_build.py").exists()
    assert (ROOT / "docs" / "standards" / "REAL_APK_BUILD_ATTEMPT_V1_STANDARD.md").exists()
