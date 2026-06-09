# Tool Adapter Standard

Every tool adapter must return structured ToolResult data: tool, ok, command, stdout, stderr, returncode, executed, and note.

Adapters must support dry-run mode.
Adapters must not print secrets.
Dangerous shell commands are blocked.
