# No Fragile Paste Protocol

AI Workflow OS must not depend on giant fragile paste scripts for core builds.

## Banned for core system construction

- giant terminal paste blobs
- nested heredocs
- unclosed Markdown fences inside shell scripts
- fake proof output
- scripts that continue after failed writes
- secret-bearing pasted documents
- base64 blobs used as a substitute for readable knowledge

## Required pattern

Every serious build step must be one of:

1. an existing committed command
2. a small staged script
3. a registry action
4. a resumable transaction
5. a verified generated file with compile/test proof

## Recovery rule

If Termux shows a `>` continuation prompt, stop immediately with Ctrl+C.
Do not keep typing.
Run verification before continuing.

## Agent behavior rule

The agent must prefer small staged actions over huge paste scripts.
The agent must inspect, write, compile, verify, then commit.
The agent must never claim a system action worked unless proof was observed.
