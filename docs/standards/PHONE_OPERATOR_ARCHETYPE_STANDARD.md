# Phone Operator Archetype Standard

AI Workflow OS is a phone-first local operating agent for building applications from inside Termux.

## Archetypal loop

prompt -> event -> approval -> registered action -> CLI capability -> material file change -> compile -> test -> proof -> export -> publish

## Required operator properties

- phone-first operator console appears before legacy panels
- browser UI sends prompts to local endpoints
- local Termux executes only approved, repo-scoped actions
- CLI tools are capabilities when installed and authenticated
- keys are never written to source, never printed, and never committed
- generated apps inherit standards, tests, manifests, export paths, and proof rules
- runtime memory must not pollute source commits unless intentionally snapshotted
- PWA assets make the phone app installable with a real icon
- architecture must remain portable to desktop, SaaS, and public contributor modes

