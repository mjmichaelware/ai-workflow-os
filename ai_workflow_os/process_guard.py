
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import os
import signal
import time
import urllib.request

PORT = 8765
ROOT = Path(__file__).resolve().parents[1]
PIDFILE = Path.home() / "tmp" / "ai_workflow_os_dashboard.pid"

def _read(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""

def _cmdline(pid: int) -> str:
    try:
        return Path("/proc", str(pid), "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", "ignore")
    except Exception:
        return ""

def _socket_inodes_for_port(port: int) -> set[str]:
    want = format(port, "04X")
    inodes: set[str] = set()
    for table in [Path("/proc/net/tcp"), Path("/proc/net/tcp6")]:
        text = _read(table)
        for line in text.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 10:
                continue
            local = parts[1]
            state = parts[3]
            inode = parts[9]
            if local.endswith(":" + want) and state == "0A":
                inodes.add(inode)
    return inodes

def _pids_for_socket_inodes(inodes: set[str]) -> List[int]:
    found: set[int] = set()
    me = os.getpid()
    parent = os.getppid()
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        pid = int(proc.name)
        if pid in {me, parent}:
            continue
        fd_dir = proc / "fd"
        if not fd_dir.exists():
            continue
        for fd in fd_dir.iterdir():
            try:
                target = os.readlink(fd)
            except Exception:
                continue
            if target.startswith("socket:[") and target[8:-1] in inodes:
                found.add(pid)
    return sorted(found)

def find_port_pids(port: int = PORT) -> List[int]:
    return _pids_for_socket_inodes(_socket_inodes_for_port(port))

def find_named_server_pids() -> List[int]:
    found: set[int] = set()
    me = os.getpid()
    parent = os.getppid()
    needles = [
        "bin/ai-workflow-os serve",
        "ai_workflow_os.cli",
        "ai-workflow-os serve",
    ]
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        pid = int(proc.name)
        if pid in {me, parent}:
            continue
        cmd = _cmdline(pid)
        if any(n in cmd for n in needles):
            found.add(pid)
    return sorted(found)

def kill_servers() -> Dict[str, Any]:
    pids = sorted(set(find_port_pids(PORT) + find_named_server_pids()))
    killed: List[int] = []
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except Exception:
            pass
    time.sleep(1)
    for pid in sorted(set(find_port_pids(PORT) + find_named_server_pids())):
        try:
            os.kill(pid, signal.SIGKILL)
            if pid not in killed:
                killed.append(pid)
        except Exception:
            pass
    try:
        PIDFILE.unlink()
    except FileNotFoundError:
        pass
    return {"ok": True, "port": PORT, "killed": sorted(set(killed))}

def http_ok(path: str) -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:%s%s" % (PORT, path), timeout=3) as r:
            return 200 <= r.status < 300
    except Exception:
        return False

def pwa_ready() -> Dict[str, Any]:
    checks = {
        "root": http_ok("/"),
        "operator": http_ok("/api/operator/status"),
        "manifest": http_ok("/manifest.webmanifest"),
        "service_worker": http_ok("/sw.js"),
        "icon": http_ok("/icons/ai-workflow-os-192.png"),
    }
    return {"ok": all(checks.values()), "checks": checks}

def main() -> None:
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "kill-server":
        print(json.dumps(kill_servers(), indent=2))
        return
    if len(sys.argv) > 1 and sys.argv[1] == "pwa-ready":
        print(json.dumps(pwa_ready(), indent=2))
        return
    print(json.dumps({"ok": True, "port_pids": find_port_pids(), "named_pids": find_named_server_pids(), "ready": pwa_ready()}, indent=2))

if __name__ == "__main__":
    main()
