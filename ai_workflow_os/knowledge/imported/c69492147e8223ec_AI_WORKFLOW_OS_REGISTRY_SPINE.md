# AI Workflow OS Registry Spine

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
