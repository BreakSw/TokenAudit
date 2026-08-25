from __future__ import annotations

from collections.abc import Sequence
import time

import requests


class VoyageEmbeddingClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        dimension: int,
        timeout_seconds: float,
        batch_size: int = 64,
        max_batch_characters: int = 24000,
        min_request_interval_seconds: float = 0,
        max_rate_limit_retries: int = 10,
        max_network_retries: int = 5,
    ) -> None:
        self.endpoint = f"{base_url.rstrip('/')}/embeddings"
        self.api_key = api_key
        self.model = model
        self.dimension = dimension
        self.timeout_seconds = timeout_seconds
        self.batch_size = batch_size
        self.max_batch_characters = max_batch_characters
        self.min_request_interval_seconds = min_request_interval_seconds
        self.max_rate_limit_retries = max_rate_limit_retries
        self.max_network_retries = max_network_retries
        self._last_request_at = 0.0

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._embed(texts, input_type="document")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], input_type="query")[0]

    def embed_queries(self, texts: Sequence[str]) -> list[list[float]]:
        return self._embed(texts, input_type="query")

    def _embed(
        self,
        texts: Sequence[str],
        *,
        input_type: str,
    ) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float]] = []
        batches: list[list[str]] = []
        batch: list[str] = []
        batch_characters = 0
        for text in texts:
            if batch and (
                len(batch) >= self.batch_size
                or batch_characters + len(text) > self.max_batch_characters
            ):
                batches.append(batch)
                batch = []
                batch_characters = 0
            batch.append(text)
            batch_characters += len(text)
        if batch:
            batches.append(batch)
        for batch in batches:
            vectors.extend(self._embed_batch(batch, input_type=input_type))
        return vectors

    def _embed_batch(
        self,
        texts: Sequence[str],
        *,
        input_type: str,
    ) -> list[list[float]]:
        response = None
        network_errors = 0
        for attempt in range(self.max_rate_limit_retries + self.max_network_retries + 1):
            elapsed = time.monotonic() - self._last_request_at
            wait_seconds = self.min_request_interval_seconds - elapsed
            if wait_seconds > 0:
                time.sleep(wait_seconds)
            try:
                response = requests.post(
                    self.endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "input": list(texts),
                        "model": self.model,
                        "input_type": input_type,
                        "output_dimension": self.dimension,
                    },
                    timeout=self.timeout_seconds,
                )
            except requests.RequestException as exc:
                network_errors += 1
                if network_errors > self.max_network_retries:
                    raise RuntimeError(f"Embedding network request failed after retries: {type(exc).__name__}") from exc
                time.sleep(max(self.min_request_interval_seconds, min(30.0, 2.0 ** network_errors)))
                continue
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
                detail = response.json().get("detail") or response.json().get("message")
            except Exception:
                detail = None
            raise RuntimeError(
                f"Embedding request failed with HTTP {response.status_code}: "
                f"{detail or 'provider rejected the request'}"
            )
        payload = response.json()
        rows = sorted(payload.get("data", []), key=lambda item: item.get("index", 0))
        vectors = [row.get("embedding", []) for row in rows]
        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Embedding provider returned {len(vectors)} vectors for {len(texts)} texts."
            )
        bad_dimensions = [len(vector) for vector in vectors if len(vector) != self.dimension]
        if bad_dimensions:
            raise RuntimeError(
                f"Embedding dimension mismatch: expected {self.dimension}, got {bad_dimensions[0]}."
            )
        return vectors
