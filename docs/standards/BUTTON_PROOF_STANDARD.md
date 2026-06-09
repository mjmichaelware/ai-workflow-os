# Button Proof Standard

A button is not real unless the endpoint it triggers is proven.

## Required proof

- The UI must expose explicit data-action attributes for important actions.
- The action endpoint must be callable from a local proof script.
- Build buttons must prove /api/operator/run.
- Export buttons must prove /api/phone/export.
- Status buttons must prove /api/operator/status.
- Proof output must not print secret values.
