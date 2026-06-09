from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manual_apk_builder_module_exists():
    text = (ROOT / "ai_workflow_os" / "manual_apk_builder.py").read_text(encoding="utf-8")
    assert "build_manual_debug_apk" in text
    assert "aapt2" in text
    assert "d8" in text
    assert "apksigner" in text
    assert "keys_printed" in text


def test_manual_apk_build_proof_exists():
    assert (ROOT / "scripts" / "prove_manual_apk_build.py").exists()
    assert (ROOT / "docs" / "standards" / "TERMUX_NATIVE_MANUAL_APK_V1_STANDARD.md").exists()
