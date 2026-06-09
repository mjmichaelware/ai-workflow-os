# App Creator Agent

The app creator agent starts with a prompt, creates a dry-run plan, writes a run folder, requires an approval manifest, then executes only approved local adapters.

Flow:
1. agent-plan creates runs/RUN_ID/plan.json.
2. approve-run creates approvals/RUN_ID.approval.json.
3. agent-run with approval executes approved safe adapters.
4. events.jsonl and result.json record proof.

No secret values are printed.
No deploys are automatic.
No git push is automatic.
