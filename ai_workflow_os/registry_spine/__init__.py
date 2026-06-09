"""AI Workflow OS registry spine package.

This package intentionally does not use the name `core` because
`ai_workflow_os/core.py` is the existing public app-builder core module.
"""

from .spine import build_registry, dispatch, rebuild

__all__ = ["build_registry", "dispatch", "rebuild"]
