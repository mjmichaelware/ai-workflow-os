from __future__ import annotations

from pathlib import Path
import json
import sqlite3
import subprocess
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "ai_workflow_os"
CORE = PKG / "core"
REG = PKG / "registries"
STATE = PKG / "persistence"
AUDIT = PKG / "audit"
PROOFS = PKG / "proofs"
KNOWLEDGE = PKG / "knowledge"
TESTS = ROOT / "tests"
DOCS = ROOT / "docs"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def write_json(path: Path, data: Any) -> None:
    write(path, json.dumps(data, indent=2, sort_keys=True) + "\n")

def sha(data: Any) -> str:
    raw = json.dumps(data, sort_keys=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()

def run(cmd: list[str]) -> dict[str, Any]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "ok": p.returncode == 0,
        "stdout": p.stdout[-4000:],
        "stderr": p.stderr[-4000:],
    }

def init_dirs() -> None:
    for d in [CORE, REG, STATE, AUDIT, PROOFS, KNOWLEDGE / "current", KNOWLEDGE / "archive", KNOWLEDGE / "imported", TESTS, DOCS]:
        d.mkdir(parents=True, exist_ok=True)
    write(CORE / "__init__.py", "")

def build_db() -> None:
    db_path = STATE / "workflow_os.sqlite3"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, type TEXT, payload_json TEXT, created_at TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS action_results (id INTEGER PRIMARY KEY AUTOINCREMENT, action_id TEXT, ok INTEGER, output_json TEXT, created_at TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS knowledge (id TEXT PRIMARY KEY, title TEXT, content_hash TEXT, status TEXT, created_at TEXT)")
        db.commit()

def build_core_module() -> None:
    write(CORE / "spine.py", r'''
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Callable
import hashlib
import json
import sqlite3
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "ai_workflow_os" / "persistence"
REG = ROOT / "ai_workflow_os" / "registries"
AUDIT = ROOT / "ai_workflow_os" / "audit"
PROOFS = ROOT / "ai_workflow_os" / "proofs"
KNOWLEDGE = ROOT / "ai_workflow_os" / "knowledge"
DB = STATE / "workflow_os.sqlite3"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def stable_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def append_jsonl(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, sort_keys=True, default=str) + "\n")

def ensure_store() -> None:
    for d in [STATE, REG, AUDIT, PROOFS, KNOWLEDGE / "current", KNOWLEDGE / "archive", KNOWLEDGE / "imported"]:
        d.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, type TEXT, payload_json TEXT, created_at TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS action_results (id INTEGER PRIMARY KEY AUTOINCREMENT, action_id TEXT, ok INTEGER, output_json TEXT, created_at TEXT)")
        db.execute("CREATE TABLE IF NOT EXISTS knowledge (id TEXT PRIMARY KEY, title TEXT, content_hash TEXT, status TEXT, created_at TEXT)")
        db.commit()

@dataclass
class Event:
    type: str
    payload: dict[str, Any]
    source: str = "system"
    id: str = ""
    created_at: str = ""

    def materialize(self) -> dict[str, Any]:
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = now()
        return asdict(self)

@dataclass
class ActionSpec:
    id: str
    label: str
    event_type: str
    permission: str
    description: str
    required: list[str]
    forbidden: list[str]
    material_effect: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

class Registry:
    def __init__(self) -> None:
        self.actions: dict[str, ActionSpec] = {}
        self.handlers: dict[str, Callable[[Event], dict[str, Any]]] = {}

    def register(self, spec: ActionSpec, handler: Callable[[Event], dict[str, Any]]) -> None:
        self.actions[spec.id] = spec
        self.handlers[spec.id] = handler

    def manifest(self) -> dict[str, Any]:
        return {
            "name": "action_registry",
            "updated_at": now(),
            "count": len(self.actions),
            "actions": [self.actions[k].to_dict() for k in sorted(self.actions)],
        }

    def validate(self, spec: ActionSpec, payload: dict[str, Any]) -> dict[str, Any]:
        missing = [k for k in spec.required if k not in payload]
        forbidden_present = [k for k in spec.forbidden if k in payload]
        return {
            "ok": not missing and not forbidden_present,
            "missing": missing,
            "forbidden_present": forbidden_present,
            "payload_hash": stable_hash(payload),
        }

    def dispatch(self, action_id: str, payload: dict[str, Any] | None = None, source: str = "registry") -> dict[str, Any]:
        ensure_store()
        payload = payload or {}

        if action_id not in self.actions:
            return {"ok": False, "action_id": action_id, "message": "unknown action", "known_actions": sorted(self.actions)}

        spec = self.actions[action_id]
        validation = self.validate(spec, payload)
        event = Event(spec.event_type, {"action_id": action_id, "payload": payload, "validation": validation}, source).materialize()

        append_jsonl(STATE / "events.jsonl", event)
        with sqlite3.connect(DB) as db:
            db.execute("INSERT OR REPLACE INTO events(id,type,payload_json,created_at) VALUES(?,?,?,?)",
                       (event["id"], event["type"], json.dumps(event["payload"], sort_keys=True), event["created_at"]))
            db.commit()

        if not validation["ok"]:
            audit = {"kind": "payload_rejected", "action_id": action_id, "event_id": event["id"], "validation": validation, "created_at": now()}
            append_jsonl(AUDIT / "audit.jsonl", audit)
            return {"ok": False, "action_id": action_id, "event_id": event["id"], "message": "payload rejected", "output": validation}

        try:
            output = self.handlers[action_id](Event(**event))
            proof = {"action": spec.to_dict(), "event": event, "output": output, "created_at": now()}
            proof_path = PROOFS / f"{now().replace(':','-')}_{action_id}.json"
            write_json(proof_path, proof)
            audit = {"kind": "action_completed", "action_id": action_id, "event_id": event["id"], "proof_path": str(proof_path), "created_at": now()}
            append_jsonl(AUDIT / "audit.jsonl", audit)
            result = {"ok": True, "action_id": action_id, "event_id": event["id"], "message": "action completed", "output": output, "proof_path": str(proof_path)}
        except Exception as e:
            audit = {"kind": "action_failed", "action_id": action_id, "event_id": event["id"], "error": str(e), "created_at": now()}
            append_jsonl(AUDIT / "audit.jsonl", audit)
            result = {"ok": False, "action_id": action_id, "event_id": event["id"], "message": "action failed", "output": {"error": str(e)}}

        with sqlite3.connect(DB) as db:
            db.execute("INSERT INTO action_results(action_id,ok,output_json,created_at) VALUES(?,?,?,?)",
                       (action_id, 1 if result["ok"] else 0, json.dumps(result, sort_keys=True, default=str), now()))
            db.commit()

        return result

def run_cmd(cmd: list[str]) -> dict[str, Any]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"cmd": cmd, "returncode": p.returncode, "ok": p.returncode == 0, "stdout": p.stdout[-4000:], "stderr": p.stderr[-4000:]}

def build_library_registry() -> dict[str, Any]:
    import importlib.metadata
    libs = []
    for dist in importlib.metadata.distributions():
        libs.append({"name": dist.metadata.get("Name") or "unknown", "version": dist.version, "ecosystem": "python"})
    data = {"name": "library_registry", "updated_at": now(), "python_count": len(libs), "python": sorted(libs, key=lambda x: x["name"].lower())}
    write_json(REG / "libraries.json", data)
    return data

def build_cli_registry() -> dict[str, Any]:
    import shutil
    commands = ["python3", "git", "gh", "gcloud", "node", "npm", "rg", "jq", "curl"]
    data = {"name": "cli_registry", "updated_at": now(), "commands": [{"name": c, "available": shutil.which(c) is not None, "path": shutil.which(c)} for c in commands]}
    write_json(REG / "cli.json", data)
    return data

def build_api_registry() -> dict[str, Any]:
    data = {
        "name": "api_registry",
        "updated_at": now(),
        "apis": [
            {"id": "local_sqlite", "kind": "free_local_database", "secret_policy": "no_plaintext_secrets"},
            {"id": "github", "kind": "developer_api", "secret_policy": "approved_auth_only"},
            {"id": "google_secret_manager", "kind": "secret_store", "secret_policy": "secret_values_never_printed"},
            {"id": "supabase", "kind": "free_database_option", "secret_policy": "keys_never_committed"},
        ],
    }
    write_json(REG / "apis.json", data)
    return data

def ingest_docs() -> dict[str, Any]:
    ensure_store()
    docs = ROOT / "docs"
    items = []
    for path in docs.rglob("*"):
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        if path.suffix.lower() not in {".md", ".txt", ".json"}:
            continue
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        target = KNOWLEDGE / "imported" / f"{digest[:16]}_{path.name}"
        if not target.exists():
            target.write_bytes(content)
        item = {"id": digest[:16], "title": path.name, "source_path": str(path), "stored_path": str(target), "content_hash": digest}
        items.append(item)
        with sqlite3.connect(DB) as db:
            db.execute("INSERT OR REPLACE INTO knowledge(id,title,content_hash,status,created_at) VALUES(?,?,?,?,?)",
                       (item["id"], item["title"], item["content_hash"], "imported", now()))
            db.commit()
    data = {"name": "knowledge_registry", "updated_at": now(), "count": len(items), "items": items}
    write_json(REG / "knowledge.json", data)
    return data

def build_registry() -> Registry:
    reg = Registry()
    forbidden = ["secret", "token", "password", "api_key"]

    reg.register(ActionSpec("system.health", "Health", "system.health.requested", "read", "Return OS state.", [], forbidden, "none"),
                 lambda event: {"ok": True, "service": "ai-workflow-os", "state": "local_first"})

    reg.register(ActionSpec("registry.rebuild", "Rebuild Registries", "registry.rebuild.requested", "local_write", "Rebuild all registries.", [], forbidden, "writes local registry files"),
                 lambda event: {"libraries": build_library_registry(), "cli": build_cli_registry(), "apis": build_api_registry(), "knowledge": ingest_docs()})

    reg.register(ActionSpec("verify.python", "Compile Python", "verify.python.requested", "local_execute", "Compile Python files.", [], forbidden, "runs compile check"),
                 lambda event: run_cmd(["python3", "-m", "compileall", "-q", "ai_workflow_os"]))

    reg.register(ActionSpec("verify.workflow", "Verify Workflow", "verify.workflow.requested", "local_execute", "Run workflow verification.", [], forbidden, "runs verify script"),
                 lambda event: run_cmd(["bash", "scripts/verify_workflow_app.sh"]))

    return reg

def dispatch(action_id: str, payload: dict[str, Any] | None = None, source: str = "api") -> dict[str, Any]:
    return build_registry().dispatch(action_id, payload or {}, source=source)

def rebuild() -> dict[str, Any]:
    reg = build_registry()
    write_json(REG / "actions.json", reg.manifest())
    return reg.dispatch("registry.rebuild", {}, source="bootstrap")
''')

def build_cli() -> None:
    write(ROOT / "scripts" / "registry_spine.py", '''#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from ai_workflow_os.registry_spine.spine import build_registry, dispatch, rebuild

def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"help", "--help", "-h"}:
        print("Commands: manifest, rebuild, dispatch <action_id> [json_payload]")
        return 0
    if args[0] == "manifest":
        print(json.dumps(build_registry().manifest(), indent=2, sort_keys=True))
        return 0
    if args[0] == "rebuild":
        print(json.dumps(rebuild(), indent=2, sort_keys=True))
        return 0
    if args[0] == "dispatch":
        if len(args) < 2:
            print("missing action_id", file=sys.stderr)
            return 2
        payload = json.loads(args[2]) if len(args) > 2 else {}
        print(json.dumps(dispatch(args[1], payload, source="cli"), indent=2, sort_keys=True))
        return 0
    print("unknown command", args[0], file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
''')
    (ROOT / "scripts" / "registry_spine.py").chmod(0o755)

def build_tests() -> None:
    write(TESTS / "test_registry_spine.py", '''
from pathlib import Path

from ai_workflow_os.registry_spine.spine import build_registry, dispatch, STATE, AUDIT, PROOFS

def test_manifest_has_actions():
    m = build_registry().manifest()
    ids = {a["id"] for a in m["actions"]}
    assert "system.health" in ids
    assert "registry.rebuild" in ids
    assert "verify.python" in ids
    assert "verify.workflow" in ids

def test_health_dispatch_creates_proof():
    result = dispatch("system.health", {}, source="test")
    assert result["ok"] is True
    assert Path(result["proof_path"]).exists()
    assert (STATE / "events.jsonl").exists()
    assert (AUDIT / "audit.jsonl").exists()
    assert PROOFS.exists()

def test_secret_payload_rejected():
    result = dispatch("system.health", {"api_key": "DO_NOT_PRINT"}, source="test")
    assert result["ok"] is False
    assert result["message"] == "payload rejected"
''')

def build_docs() -> None:
    write(DOCS / "AI_WORKFLOW_OS_REGISTRY_SPINE.md", """# AI Workflow OS Registry Spine

The registry spine encodes the operating loop:

current state -> event -> event bus -> registered action -> typed payload -> material effect -> persistence -> audit -> tests -> knowledge update.

## Registries

- actions
- CLI tools
- APIs
- libraries
- knowledge
- proofs
- audit

## Rules

- No giant fragile paste scripts for core builds.
- No base64 knowledge blobs.
- Store readable files plus hashes.
- Archive old knowledge.
- Never print secrets.
- Never commit secrets.
- Never send secret values to LLM APIs.
- Buttons must come from registered actions.
- A button without an action is not real.
- A result without proof is not proof.
""")

def main() -> int:
    init_dirs()
    build_db()
    build_core_module()
    build_cli()
    build_tests()
    build_docs()
    print("Built registry spine files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
