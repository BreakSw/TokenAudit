from __future__ import annotations

from typing import Any, Sequence
import time

import requests


class VoyageRerankClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float,
        min_request_interval_seconds: float = 0,
        max_rate_limit_retries: int = 10,
    ) -> None:
        self.endpoint = f"{base_url.rstrip('/')}/rerank"
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.min_request_interval_seconds = min_request_interval_seconds
        self.max_rate_limit_retries = max_rate_limit_retries
        self._last_request_at = 0.0

    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        *,
        top_k: int,
    ) -> list[dict[str, Any]]:
        if not documents:
            return []
        response = None
        for attempt in range(self.max_rate_limit_retries + 1):
            elapsed = time.monotonic() - self._last_request_at
            wait_seconds = self.min_request_interval_seconds - elapsed
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            response = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": query,
                    "documents": list(documents),
                    "model": self.model,
                    "top_k": min(top_k, len(documents)),
                    "truncation": True,
                },
                timeout=self.timeout_seconds,
            )
            self._last_request_at = time.monotonic()
            if response.status_code != 429 or attempt >= self.max_rate_limit_retries:
                break
            retry_after = response.headers.get("Retry-After", "")
            try:
                retry_delay = float(retry_after)
            except ValueError:
                retry_delay = 0.0
            time.sleep(max(retry_delay, self.min_request_interval_seconds, 20.0))
        assert response is not None
        if response.status_code >= 400:
            try:
                payload = response.json()
                detail = payload.get("detail") or payload.get("message")
            except Exception:
                detail = None
            raise RuntimeError(
                f"Rerank request failed with HTTP {response.status_code}: "
                f"{detail or 'provider rejected the request'}"
            )
        payload = response.json()
        results = payload.get("data", payload.get("results", []))
        normalized = []
        for item in results:
            index = int(item["index"])
            normalized.append(
                {
                    "index": index,
                    "relevance_score": float(
                        item.get("relevance_score", item.get("score", 0.0))
                    ),
                }
            )
        return normalized
