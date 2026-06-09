from __future__ import annotations

import argparse
import json
from pathlib import Path

from .app_builder import create_generated_app, test_generated_app
from .core import scan_project, install_into_project, export_packet, catalog_json
from .import_export import export_app_manifest, import_app_manifest
from .permissions import default_policy_json
from .providers import list_providers
from .research_graph import MarketResearchGraph, build_research_queries
from .secrets import secret_status
from .self_bootstrap import save_self_bootstrap_plan

try:
    from .approvals import create_manifest
    from .executor import execute_plan
    from .orchestrator import WorkflowAgent, save_plan
    from .runlog import list_runs
    from .tools import GhTool, GcloudTool, RepoInspector, tool_inventory
except Exception:
    create_manifest = None
    execute_plan = None
    WorkflowAgent = None
    save_plan = None
    list_runs = None
    GhTool = None
    GcloudTool = None
    RepoInspector = None
    tool_inventory = None

def dump(obj): print(json.dumps(obj, indent=2))

def cmd_doctor(args):
    root = Path.cwd()
    required = ["README.md", "ai_workflow_os/core.py", "ai_workflow_os/server.py", "ai_workflow_os/cli.py", "ai_workflow_os/app_builder.py", "ai_workflow_os/import_export.py", "web/index.html", "web/static/app.js", "web/static/app.css"]
    missing = [p for p in required if not (root / p).exists()]
    print("AI Workflow OS doctor")
    print(f"root={root}")
    if missing:
        print("missing:")
        for item in missing: print(f"- {item}")
        return 1
    print("PASS: core files exist")
    return 0

def cmd_catalog(args): print(catalog_json()); return 0
def cmd_providers(args): dump({"providers": list_providers()}); return 0
def cmd_permissions(args): dump(default_policy_json()); return 0
def cmd_tools(args): dump(tool_inventory() if tool_inventory else {"tools_module": False}); return 0
def cmd_runs(args): dump({"runs": list_runs(Path.cwd()) if list_runs else []}); return 0
def cmd_status(args): dump(scan_project(Path(args.target)).__dict__); return 0
def cmd_inspect(args): dump(RepoInspector().inspect(Path(args.target)) if RepoInspector else {"inspect_module": False}); return 0
def cmd_secret_status(args): dump(secret_status(args.secret, project_id=args.project)); return 0
def cmd_gh_status(args): dump(GhTool().status(Path.cwd(), execute=args.execute).to_dict() if GhTool else {"gh_tool": False}); return 0
def cmd_gcloud_project(args): dump(GcloudTool().config_project(execute=args.execute).to_dict() if GcloudTool else {"gcloud_tool": False}); return 0
def cmd_research_graph(args): dump(MarketResearchGraph().build_seed_graph(args.prompt)); return 0
def cmd_research_queries(args): dump(build_research_queries(args.prompt, max_depth=args.depth)); return 0
def cmd_init_project(args): dump(install_into_project(Path(args.target), app_name=args.name)); return 0
def cmd_export_packet(args): print(f"exported={export_packet(Path(args.target), Path(args.out))}"); return 0
def cmd_export_app(args): print(f"exported={export_app_manifest(Path(args.target), Path(args.out))}"); return 0
def cmd_import_app(args): dump(import_app_manifest(Path(args.manifest), Path(args.target), execute=args.execute)); return 0
def cmd_create_app(args): dump(create_generated_app(args.prompt, Path(args.target), name=args.name, execute=args.execute)); return 0
def cmd_test_app(args): dump(test_generated_app(Path(args.target))); return 0
def cmd_self_bootstrap(args): dump({"self_bootstrap_plan": str(save_self_bootstrap_plan(Path.cwd(), args.prompt, Path(args.out))) }); return 0

def cmd_agent_plan(args):
    if WorkflowAgent is None or save_plan is None:
        dump({"error": "agent planner modules not installed"})
        return 1
    plan = WorkflowAgent().create_app_plan(args.prompt, target=args.target, mode="dry_run")
    plan_path = save_plan(plan, Path(args.out))
    dump({"plan_path": str(plan_path), "run_id": plan.run_id, "mode": plan.mode})
    return 0

def cmd_approve(args):
    if create_manifest is None:
        dump({"error": "approval module not installed"})
        return 1
    dump({"approval_file": str(create_manifest(args.run_id, Path(args.out), approved_by=args.by, notes=args.notes)), "run_id": args.run_id})
    return 0

def cmd_agent_run(args):
    if execute_plan is None:
        dump({"error": "executor module not installed"})
        return 1
    dump(execute_plan(Path(args.plan), approve=args.approve, approval_file=Path(args.approval_file) if args.approval_file else None))
    return 0

def cmd_serve(args):
    from .server import run_server
    run_server(host=args.host, port=args.port)
    return 0

def build_parser():
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
    p = sub.add_parser("research-graph"); p.add_argument("prompt"); p.set_defaults(func=cmd_research_graph)
    p = sub.add_parser("research-queries"); p.add_argument("prompt"); p.add_argument("--depth", type=int, default=2); p.set_defaults(func=cmd_research_queries)
    p = sub.add_parser("self-bootstrap"); p.add_argument("prompt"); p.add_argument("--out", default="runs/self_bootstrap"); p.set_defaults(func=cmd_self_bootstrap)
    p = sub.add_parser("create-app"); p.add_argument("prompt"); p.add_argument("--target", default="generated_apps/generated-app"); p.add_argument("--name", default=""); p.add_argument("--execute", action="store_true"); p.set_defaults(func=cmd_create_app)
    p = sub.add_parser("test-app"); p.add_argument("target"); p.set_defaults(func=cmd_test_app)
    p = sub.add_parser("export-app"); p.add_argument("target"); p.add_argument("--out", default="runs/exported_app_manifest.json"); p.set_defaults(func=cmd_export_app)
    p = sub.add_parser("import-app"); p.add_argument("manifest"); p.add_argument("target"); p.add_argument("--execute", action="store_true"); p.set_defaults(func=cmd_import_app)
    p = sub.add_parser("init-project"); p.add_argument("target"); p.add_argument("--name", default="REPLACE_ME"); p.set_defaults(func=cmd_init_project)
    p = sub.add_parser("export-packet"); p.add_argument("target"); p.add_argument("--out", default=str(Path.home() / "storage/downloads")); p.set_defaults(func=cmd_export_packet)
    p = sub.add_parser("agent-plan"); p.add_argument("prompt"); p.add_argument("--target", default="."); p.add_argument("--out", default="runs"); p.set_defaults(func=cmd_agent_plan)
    p = sub.add_parser("approve-run"); p.add_argument("run_id"); p.add_argument("--out", default="approvals"); p.add_argument("--by", default="owner"); p.add_argument("--notes", default=""); p.set_defaults(func=cmd_approve)
    p = sub.add_parser("agent-run"); p.add_argument("plan"); p.add_argument("--approve", action="store_true"); p.add_argument("--approval-file", default=None); p.set_defaults(func=cmd_agent_run)
    p = sub.add_parser("serve"); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8765); p.set_defaults(func=cmd_serve)
    return parser

def main():
    args = build_parser().parse_args()
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
