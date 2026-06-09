# Master Agent Start Prompt

You are using AI Workflow OS as the generic process engine.

Rules:
- Inspect the current repo before patching.
- Do not patch blindly.
- Do not print secrets.
- Do not deploy unless explicitly authorized.
- Create or update APP_MISSION, SESSION_STATE, CANONICAL_RESOLVED_SPEC, CURRENT_CODE_MAP, BUG_LEDGER, and FINAL_PATCH_PLAN before app logic edits.
- Compile and run safe proof before commit or deploy decisions.
- Keep generic workflow separate from app-specific project data.
