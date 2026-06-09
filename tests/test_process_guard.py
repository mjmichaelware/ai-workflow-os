from ai_workflow_os.process_guard import pwa_ready, find_port_pids, find_named_server_pids

def test_process_guard_shapes():
    data = pwa_ready()
    assert "ok" in data
    assert "checks" in data

def test_pid_functions_return_lists():
    assert isinstance(find_port_pids(), list)
    assert isinstance(find_named_server_pids(), list)

