from pathlib import Path
from ai_workflow_os.prompt_bridge import submit_prompt, approve_prompt
from ai_workflow_os.self_build_executor import self_build_manifest, run_next_self_build

def test_self_build_manifest_is_safe():
    data = self_build_manifest()
    assert data["ok"] is True
    assert data["raw_shell"] is False
    assert data["deploys"] is False

def test_run_next_self_build_materializes_generated_app():
    p = submit_prompt("Create a small proof app from self build test", source="test", target="self_build")
    approve_prompt(p["id"], True)
    result = run_next_self_build()
    assert result["ok"] is True
    app_dir = Path(result["plan"]["app_dir"])
    assert app_dir.joinpath("APP_MANIFEST.json").exists()
    assert app_dir.joinpath("app.py").exists()
