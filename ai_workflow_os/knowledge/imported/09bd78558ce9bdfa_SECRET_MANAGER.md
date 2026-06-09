# Secret Manager Standard

AI Workflow OS stores secret references, never secret values.

Rules:
- Do not print secret values.
- Do not commit secret values.
- Use Google Secret Manager or target-app configured secret stores.
- Secret access requires explicit approval.
- CLI status commands may check whether a secret exists, but must not reveal values.

Example status check:

bin/ai-workflow-os secret-status OPENAI_API_KEY --project YOUR_PROJECT_ID
