
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_capability_matrix_module_exists():
    text = (ROOT / "ai_workflow_os" / "capability_matrix.py").read_text(encoding="utf-8")
    assert "CAPABILITIES" in text
    assert "broad_permissions" in text
    assert "keys_printed" in text
    assert "token" in text.lower()


def test_capability_matrix_proof_exists():
    assert (ROOT / "scripts" / "prove_capability_matrix.py").exists()
    assert (ROOT / "docs" / "standards" / "CAPABILITY_MATRIX_STANDARD.md").exists()


def test_capability_matrix_json_after_generation():
    path = ROOT / "docs" / "capabilities" / "TOOL_AGENT_CAPABILITY_MATRIX.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["broad_permissions"] is False
        assert data["keys_printed"] is False
        assert len(data["capabilities"]) >= 8
