
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_agent_builder_module_exists():
    text = (ROOT / "ai_workflow_os" / "agent_builder.py").read_text(encoding="utf-8")
    assert "route_prompt_to_agents" in text
    assert "attach_agent_route_to_manifest" in text
    assert "should_route_prompt_to_agents" in text
    assert "raw_shell_from_agents_executed" in text
    assert "keys_printed" in text

def test_operator_uses_agent_builder_safely():
    text = (ROOT / "ai_workflow_os" / "operator_console.py").read_text(encoding="utf-8")
    assert "route_prompt_to_agents" in text
    assert "skipped_agent_route" in text
    assert "failed_agent_route" in text
    assert "AGENT ROUTED BUILDER V1 OVERRIDE" in text

def test_agent_builder_docs_and_proof_exist():
    assert (ROOT / "scripts" / "prove_agent_routed_builder.py").exists()
    assert (ROOT / "docs" / "AGENT_ROUTED_BUILDER.md").exists()
    assert (ROOT / "docs" / "standards" / "AGENT_ROUTED_BUILDER_V1_STANDARD.md").exists()
