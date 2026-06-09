# No Heredoc Core Build Standard

The OS must not use heredoc blocks for core system construction.

## Failure pattern

Markdown fences inside heredoc can leave Termux waiting at the continuation prompt.
That is a broken material action and must be prevented.

## Rule

Use staged scripts, Python writers, registry actions, or committed files.
Never use heredoc for core OS builds, standards, dashboard wiring, or generated app templates.
