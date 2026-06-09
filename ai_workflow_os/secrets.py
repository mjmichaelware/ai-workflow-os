from __future__ import annotations

from dataclasses import dataclass
import shutil
import subprocess
from typing import Optional


class SecretAccessError(RuntimeError):
    pass


@dataclass
class SecretRef:
    name: str
    project_id: Optional[str] = None
    version: str = "latest"


class GoogleSecretManagerResolver:
    def __init__(self, project_id: Optional[str] = None) -> None:
        self.project_id = project_id

    def has_gcloud(self) -> bool:
        return shutil.which("gcloud") is not None

    def _project_args(self, ref: SecretRef) -> list[str]:
        project = ref.project_id or self.project_id
        return ["--project", project] if project else []

    def exists(self, ref: SecretRef) -> bool:
        if not self.has_gcloud():
            return False
        cmd = ["gcloud", "secrets", "describe", ref.name, "--quiet"] + self._project_args(ref)
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
        return result.returncode == 0

    def access(self, ref: SecretRef, approved: bool = False) -> str:
        if not approved:
            raise SecretAccessError("Secret access requires explicit approval. Values are never printed by default.")
        if not self.has_gcloud():
            raise SecretAccessError("gcloud is not installed or not on PATH.")
        cmd = ["gcloud", "secrets", "versions", "access", ref.version, "--secret", ref.name, "--quiet"] + self._project_args(ref)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise SecretAccessError("Secret Manager access failed. Check auth, project, secret name, and IAM.")
        return result.stdout.rstrip("\\n")


def secret_status(secret_name: str, project_id: Optional[str] = None) -> dict:
    resolver = GoogleSecretManagerResolver(project_id=project_id)
    ref = SecretRef(name=secret_name, project_id=project_id)
    return {
        "secret": secret_name,
        "project_id": project_id,
        "gcloud_available": resolver.has_gcloud(),
        "exists": resolver.exists(ref),
        "value_printed": False,
    }
