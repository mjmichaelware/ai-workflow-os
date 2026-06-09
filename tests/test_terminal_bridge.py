
from pathlib import Path

from ai_workflow_os.terminal_bridge import list_terminal_commands, run_terminal_command

def test_terminal_commands_are_allowlisted():
    data = list_terminal_commands()
    assert data["ok"] is True
    ids = {x["id"] for x in data["commands"]}
    assert "os.doctor" in ids
    assert "registry.health" in ids
    assert "verify.compile" in ids

def test_terminal_unknown_command_rejected():
    result = run_terminal_command("danger.arbitrary.shell")
    assert result["ok"] is False

def test_terminal_pwd_creates_proof():
    result = run_terminal_command("pwd")
    assert result["ok"] is True
    assert Path(result["proof_path"]).exists()
