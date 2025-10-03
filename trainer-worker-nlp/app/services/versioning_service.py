import re
from typing import Optional
from app.repositories.model_versions_repository import ModelVersionsRepository

class VersioningService:
    def __init__(self, model_repo: ModelVersionsRepository):
        self.model_repo = model_repo

    @staticmethod
    def _parse_v(version: str) -> int:
        m = re.match(r"v(\d+)$", version or "")
        return int(m.group(1)) if m else 0

    @staticmethod
    def _format_v(n: int) -> str:
        return f"v{n}"

    def resolve_target_version(self, strategy: str, scope: str,
                               subject_id: Optional[str], channel: Optional[str],
                               base_version: Optional[str]) -> str:
        if strategy == "fixed" and base_version:
            return base_version

        versions = self.model_repo.list_versions(scope, subject_id, channel)
        max_n = 0
        for v in versions:
            max_n = max(max_n, self._parse_v(v.get("version", "")))

        if strategy in ("auto", "increment"):
            return self._format_v(max_n + 1)

        return self._format_v(max_n + 1)
