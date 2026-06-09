from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone
import json
import os
import re
import sqlite3
import uuid

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "ai_workflow_os" / "prompt_bridge"
DB = STORE / "prompt_bridge.sqlite3"
JOURNAL = STORE / "prompt_events.jsonl"

SECRET_PATTERNS = [
    re.compile("sk-[A-Za-z0-9_\\-]{12,}"),
    re.compile("sk-proj-[A-Za-z0-9_\\-]{12,}"),
    re.compile("ghp_[A-Za-z0-9_]{12,}"),
    re.compile("gsk_[A-Za-z0-9_]{12,}"),
    re.compile("vcp_[A-Za-z0-9_]{12,}"),
    re.compile("tgp_v1_[A-Za-z0-9_\\-]{12,}"),
    re.compile("AIza[A-Za-z0-9_\\-]{12,}"),
    re.compile("postgresql://[^\\s]+", re.IGNORECASE),
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def redact(text: str) -> str:
    out = text or ""
    for pattern in SECRET_PATTERNS:
        out = pattern.sub("[REDACTED_SECRET]", out)
    for name, value in os.environ.items():
        if any(x in name.upper() for x in ["KEY", "TOKEN", "SECRET", "PASSWORD"]) and value:
            out = out.replace(value, "[REDACTED_ENV]")
    return out

def ensure_store() -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS prompts (id TEXT PRIMARY KEY, prompt TEXT NOT NULL, source TEXT NOT NULL, target TEXT NOT NULL, status TEXT NOT NULL, approved INTEGER NOT NULL, result_json TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
        db.commit()

def append_event(event: Dict[str, Any]) -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + chr(10))

def submit_prompt(prompt: str, source: str = "dashboard", target: str = "self_build") -> Dict[str, Any]:
    ensure_store()
    cleaned = redact(prompt).strip()
    if not cleaned:
        return {"ok": False, "error": "empty prompt"}
    prompt_id = str(uuid.uuid4())
    ts = now()
    with sqlite3.connect(DB) as db:
        db.execute("INSERT INTO prompts(id,prompt,source,target,status,approved,result_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)", (prompt_id, cleaned, source, target, "pending_approval", 0, None, ts, ts))
        db.commit()
    event = {"ok": True, "event": "prompt.submitted", "id": prompt_id, "source": source, "target": target, "created_at": ts}
    append_event(event)
    return {"ok": True, "id": prompt_id, "status": "pending_approval", "target": target, "prompt": cleaned}

def approve_prompt(prompt_id: str, approved: bool = True) -> Dict[str, Any]:
    ensure_store()
    status = "approved_for_self_build" if approved else "rejected"
    ts = now()
    with sqlite3.connect(DB) as db:
        cur = db.execute("UPDATE prompts SET approved=?, status=?, updated_at=? WHERE id=?", (1 if approved else 0, status, ts, prompt_id))
        db.commit()
        if cur.rowcount == 0:
            return {"ok": False, "error": "unknown prompt_id"}
    append_event({"ok": True, "event": "prompt.approved" if approved else "prompt.rejected", "id": prompt_id, "updated_at": ts})
    return {"ok": True, "id": prompt_id, "status": status, "approved": approved}

def complete_prompt(prompt_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    ensure_store()
    ts = now()
    safe_result = json.loads(redact(json.dumps(result, default=str)))
    with sqlite3.connect(DB) as db:
        cur = db.execute("UPDATE prompts SET status=?, result_json=?, updated_at=? WHERE id=?", ("completed", json.dumps(safe_result, sort_keys=True), ts, prompt_id))
        db.commit()
        if cur.rowcount == 0:
            return {"ok": False, "error": "unknown prompt_id"}
    append_event({"ok": True, "event": "prompt.completed", "id": prompt_id, "updated_at": ts})
    return {"ok": True, "id": prompt_id, "status": "completed", "result": safe_result}

def list_prompts(limit: int = 50) -> Dict[str, Any]:
    ensure_store()
    with sqlite3.connect(DB) as db:
        rows = db.execute("SELECT id,prompt,source,target,status,approved,result_json,created_at,updated_at FROM prompts ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    items: List[Dict[str, Any]] = []
    for row in rows:
        items.append({"id": row[0], "prompt": row[1], "source": row[2], "target": row[3], "status": row[4], "approved": bool(row[5]), "result": json.loads(row[6]) if row[6] else None, "created_at": row[7], "updated_at": row[8]})
    return {"ok": True, "count": len(items), "items": items}

def next_approved_prompt() -> Dict[str, Any]:
    ensure_store()
    with sqlite3.connect(DB) as db:
        row = db.execute("SELECT id,prompt,source,target,status,approved,created_at,updated_at FROM prompts WHERE approved=1 AND status=? ORDER BY created_at ASC LIMIT 1", ("approved_for_self_build",)).fetchone()
    if not row:
        return {"ok": True, "prompt": None}
    return {"ok": True, "prompt": {"id": row[0], "prompt": row[1], "source": row[2], "target": row[3], "status": row[4], "approved": bool(row[5]), "created_at": row[6], "updated_at": row[7]}}

def bridge_manifest() -> Dict[str, Any]:
    return {"ok": True, "name": "prompt_bridge", "purpose": "dashboard prompts become approved events for self-build executor and phone wrapper", "local_only": True, "raw_shell": False, "endpoints": ["GET /api/prompts", "GET /api/prompts/manifest", "GET /api/prompts/next-approved", "POST /api/prompts/submit", "POST /api/prompts/approve", "POST /api/prompts/complete"], "flow": {"command_1": "prompt bridge API", "command_2": "approval-gated self-build executor API", "command_3": "phone wrapper export API"}}
