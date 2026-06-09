from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_recursive_inheritance_module_exists():
    text = (ROOT / "ai_workflow_os" / "recursive_inheritance.py").read_text(encoding="utf-8")
    assert "prove_grandchild_chain" in text
    assert "create_recursive_child" in text
    assert "ensure_generated_app_shell" in text
    assert "depth_proven" in text


def test_recursive_inheritance_proof_docs_exist():
    assert (ROOT / "scripts" / "prove_recursive_grandchild_inheritance.py").exists()
    assert (ROOT / "docs" / "RECURSIVE_GRANDCHILD_INHERITANCE.md").exists()
    assert (ROOT / "docs" / "standards" / "RECURSIVE_GRANDCHILD_INHERITANCE_V1_STANDARD.md").exists()
