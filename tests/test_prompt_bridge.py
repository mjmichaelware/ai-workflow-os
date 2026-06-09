from ai_workflow_os.prompt_bridge import bridge_manifest, submit_prompt, approve_prompt, next_approved_prompt, complete_prompt, list_prompts

def test_prompt_bridge_manifest_has_endpoints():
    data = bridge_manifest()
    assert data["ok"] is True
    assert "POST /api/prompts/submit" in data["endpoints"]
    assert data["raw_shell"] is False

def test_prompt_lifecycle():
    submitted = submit_prompt("Build a safe generated app with tests", source="test", target="self_build")
    assert submitted["ok"] is True
    approved = approve_prompt(submitted["id"], True)
    assert approved["ok"] is True
    nxt = next_approved_prompt()
    assert nxt["ok"] is True
    assert nxt["prompt"] is not None
    done = complete_prompt(submitted["id"], {"ok": True, "proof": "test"})
    assert done["ok"] is True
    listed = list_prompts()
    assert listed["ok"] is True
