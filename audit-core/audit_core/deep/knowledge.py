from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any

import requests


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _knowledge_package_root() -> Path:
    return _project_root() / "knowledge-service"


def _env_files() -> list[Path]:
    explicit = os.getenv("TOKENAUDIT_ENV_FILE", "").strip()
    candidates = [Path(explicit)] if explicit else []
    root = _project_root()
    candidates.extend((root / ".env", root.parents[2] / ".env"))
    return [path.resolve() for path in candidates if path and path.exists()]


class DeepKnowledgeGateway:
    def __init__(self) -> None:
        self.service_url = os.getenv("KNOWLEDGE_SERVICE_URL", "http://127.0.0.1:8091").rstrip("/")
        self.timeout_seconds = float(os.getenv("KNOWLEDGE_SERVICE_TIMEOUT_SECONDS", "120"))
        self._retriever = None
        if os.getenv("KNOWLEDGE_DIRECT_MODE", "").casefold() in {"1", "true", "yes"}:
            package_root = _knowledge_package_root()
            if str(package_root) not in sys.path:
                sys.path.insert(0, str(package_root))
            from tokenaudit_knowledge.hybrid_retriever import HybridAuditRetriever

            env_files = _env_files()
            if not env_files:
                raise ValueError("No environment file containing RAG configuration was found.")
            self._retriever = HybridAuditRetriever.load(env_files)

    def close(self) -> None:
        if self._retriever is not None:
            self._retriever.close()

    def retrieve(self, *, model_id: str, query: str) -> dict[str, Any]:
        if self._retriever is not None:
            from tokenaudit_knowledge.hybrid_retriever import compact_evidence

            return compact_evidence(self._retriever.retrieve(model_id=model_id, query=query))
        try:
            response = requests.post(
                f"{self.service_url}/retrieve",
                json={"model_id": model_id, "query": query},
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                f"knowledge_service_unreachable:{self.service_url}; start tokenaudit_knowledge.server first"
            ) from exc
        if response.status_code >= 400:
            raise RuntimeError(f"knowledge_service_failed:HTTP_{response.status_code}:{response.text[:500]}")
        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("knowledge_service_incompatible_response")
        return payload
