from __future__ import annotations

import argparse
import json
from pathlib import Path

from .approvals import create_manifest
from .core import scan_project, install_into_project, export_packet, catalog_json
from .executor import execute_plan
from .orchestrator import WorkflowAgent, save_plan
from .permissions import default_policy_json
from .providers import list_providers
from .runlog import list_runs
from .secrets import secret_status
from .tools import GhTool, GcloudTool, RepoInspector, tool_inventory


def cmd_doctor(args: argparse.Namespace) -> int:
    root = Path.cwd()
    required = ["README.md", "ai_workflow_os/core.py", "ai_workflow_os/server.py", "ai_workflow_os/cli.py", "ai_workflow_os/tools.py", "ai_workflow_os/approvals.py", "workflow/MASTER_AGENT_START_PROMPT.md", "standards/OMEGA_ALPHA_STANDARD.md"]
    missing = [p for p in required if not (root / p).exists()]
    print("AI Workflow OS doctor")
    print(f"root={root}")
    if missing:
        print("missing:")
        for item in missing:
            print(f"- {item}")
        return 1
    print("PASS: core files exist")
    return 0

def cmd_catalog(args): print(catalog_json()); return 0
def cmd_providers(args): print(json.dumps({"providers": list_providers()}, indent=2)); return 0
def cmd_permissions(args): print(json.dumps(default_policy_json(), indent=2)); return 0
def cmd_tools(args): print(json.dumps(tool_inventory(), indent=2)); return 0
def cmd_status(args): print(json.dumps(scan_project(Path(args.target)).__dict__, indent=2)); return 0
def cmd_inspect(args): print(json.dumps(RepoInspector().inspect(Path(args.target)), indent=2)); return 0
def cmd_runs(args): print(json.dumps({"runs": list_runs(Path.cwd())}, indent=2)); return 0
def cmd_secret_status(args): print(json.dumps(secret_status(args.secret, project_id=args.project), indent=2)); return 0
def cmd_gh_status(args): print(json.dumps(GhTool().status(Path.cwd(), execute=args.execute).to_dict(), indent=2)); return 0
def cmd_gcloud_project(args): print(json.dumps(GcloudTool().config_project(execute=args.execute).to_dict(), indent=2)); return 0

def cmd_init_project(args):
    print(json.dumps(install_into_project(Path(args.target), app_name=args.name), indent=2))
    return 0

def cmd_export(args):
    print(f"exported={export_packet(Path(args.target), Path(args.out))}")
    return 0

def cmd_agent_plan(args):
    plan = WorkflowAgent().create_app_plan(args.prompt, target=args.target, mode="dry_run")
    plan_path = save_plan(plan, Path(args.out))
    print(json.dumps({"plan_path": str(plan_path), "run_id": plan.run_id, "mode": plan.mode}, indent=2))
    return 0

def cmd_approve(args):
    path = create_manifest(args.run_id, Path(args.out), approved_by=args.by, notes=args.notes)
    print(json.dumps({"approval_file": str(path), "run_id": args.run_id}, indent=2))
    return 0

def cmd_agent_run(args):
    approval_file = Path(args.approval_file) if args.approval_file else None
    print(json.dumps(execute_plan(Path(args.plan), approve=args.approve, approval_file=approval_file), indent=2))
    return 0

def cmd_serve(args):
    from .server import run_server
    run_server(host=args.host, port=args.port)
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-workflow-os", description="AI Workflow OS CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("doctor"); p.set_defaults(func=cmd_doctor)
    p = sub.add_parser("catalog"); p.set_defaults(func=cmd_catalog)
    p = sub.add_parser("providers"); p.set_defaults(func=cmd_providers)
    p = sub.add_parser("permissions"); p.set_defaults(func=cmd_permissions)
    p = sub.add_parser("tools"); p.set_defaults(func=cmd_tools)
    p = sub.add_parser("runs"); p.set_defaults(func=cmd_runs)
    p = sub.add_parser("status"); p.add_argument("target", nargs="?", default="."); p.set_defaults(func=cmd_status)
    p = sub.add_parser("inspect"); p.add_argument("target", nargs="?", default="."); p.set_defaults(func=cmd_inspect)
    p = sub.add_parser("secret-status"); p.add_argument("secret"); p.add_argument("--project", default=None); p.set_defaults(func=cmd_secret_status)
    p = sub.add_parser("gh-status"); p.add_argument("--execute", action="store_true"); p.set_defaults(func=cmd_gh_status)
    p = sub.add_parser("gcloud-project"); p.add_argument("--execute", action="store_true"); p.set_defaults(func=cmd_gcloud_project)
    p = sub.add_parser("init-project"); p.add_argument("target"); p.add_argument("--name", default="REPLACE_ME"); p.set_defaults(func=cmd_init_project)
    p = sub.add_parser("export-packet"); p.add_argument("target"); p.add_argument("--out", default=str(Path.home() / "storage/downloads")); p.set_defaults(func=cmd_export)
    p = sub.add_parser("agent-plan"); p.add_argument("prompt"); p.add_argument("--target", default="."); p.add_argument("--out", default="runs"); p.set_defaults(func=cmd_agent_plan)
    p = sub.add_parser("approve-run"); p.add_argument("run_id"); p.add_argument("--out", default="approvals"); p.add_argument("--by", default="owner"); p.add_argument("--notes", default=""); p.set_defaults(func=cmd_approve)
    p = sub.add_parser("agent-run"); p.add_argument("plan"); p.add_argument("--approve", action="store_true"); p.add_argument("--approval-file", default=None); p.set_defaults(func=cmd_agent_run)
    p = sub.add_parser("serve"); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8765); p.set_defaults(func=cmd_serve)
    return parser

def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
