from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pymilvus import DataType, MilvusClient

from .behavior_schema import BehaviorRecord
from .model_catalog import resolve_knowledge_baseline


class BehaviorMilvusStore:
    def __init__(self, *, uri: str, token: str, database: str, collection: str, dimension: int, metric_type: str) -> None:
        self.uri = uri
        self.collection = collection
        self.dimension = dimension
        self.metric_type = metric_type
        if not uri.startswith(("http://", "https://")):
            Path(uri).parent.mkdir(parents=True, exist_ok=True)
        kwargs: dict[str, Any] = {"uri": uri}
        if token:
            kwargs["token"] = token
        if database and uri.startswith(("http://", "https://")):
            kwargs["db_name"] = database
        self.client = MilvusClient(**kwargs)

    def close(self) -> None:
        self.client.close()
        if not self.uri.startswith(("http://", "https://")):
            try:
                from milvus_lite.server_manager import server_manager_instance

                server_manager_instance.release_all()
            except Exception:
                pass

    def ensure_collection(self, *, rebuild: bool = False) -> None:
        exists = self.client.has_collection(collection_name=self.collection)
        if exists and rebuild:
            self.client.drop_collection(collection_name=self.collection)
            exists = False
        if exists:
            description = self.client.describe_collection(collection_name=self.collection)
            vector_field = next(field for field in description["fields"] if field["name"] == "vector")
            existing_dimension = int(vector_field["params"]["dim"])
            if existing_dimension != self.dimension:
                raise ValueError(f"Behavior collection dimension is {existing_dimension}, expected {self.dimension}.")
            self.client.load_collection(collection_name=self.collection)
            return

        schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=128)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.dimension)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=8192)
        schema.add_field(field_name="model_id", datatype=DataType.VARCHAR, max_length=128)
        schema.add_field(field_name="source_id", datatype=DataType.VARCHAR, max_length=256)
        schema.add_field(field_name="trajectory_id", datatype=DataType.VARCHAR, max_length=128)
        schema.add_field(field_name="sample_kind", datatype=DataType.VARCHAR, max_length=32)
        schema.add_field(field_name="task_type", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="outcome", datatype=DataType.VARCHAR, max_length=24)
        schema.add_field(field_name="confidence", datatype=DataType.FLOAT)
        schema.add_field(field_name="persona_contaminated", datatype=DataType.BOOL)
        schema.add_field(field_name="observed_only", datatype=DataType.BOOL)
        schema.add_field(field_name="content_hash", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="payload_json", datatype=DataType.VARCHAR, max_length=16384)
        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(field_name="vector", index_type="AUTOINDEX", metric_type=self.metric_type)
        self.client.create_collection(
            collection_name=self.collection,
            schema=schema,
            index_params=index_params,
            consistency_level="Strong",
        )
        self.client.load_collection(collection_name=self.collection)

    def upsert_records(self, records: list[BehaviorRecord], vectors: list[list[float]], *, batch_size: int = 100) -> int:
        if len(records) != len(vectors):
            raise ValueError("Behavior record/vector count mismatch.")
        rows: list[dict[str, Any]] = []
        for record, vector in zip(records, vectors, strict=True):
            if len(vector) != self.dimension:
                raise ValueError(f"Vector dimension mismatch for {record.id}.")
            payload = record.to_dict()
            payload.pop("embedding_text", None)
            rows.append(
                {
                    "id": record.id,
                    "vector": vector,
                    "text": record.embedding_text[:8192],
                    "model_id": record.model_id,
                    "source_id": record.source_id[:256],
                    "trajectory_id": record.trajectory_id[:128],
                    "sample_kind": record.sample_kind[:32],
                    "task_type": record.task_type[:64],
                    "outcome": record.outcome[:24],
                    "confidence": float(record.confidence),
                    "persona_contaminated": bool(record.persona_contaminated),
                    "observed_only": bool(record.observed_only),
                    "content_hash": record.content_hash,
                    "payload_json": json.dumps(payload, ensure_ascii=False, sort_keys=True)[:16384],
                }
            )
        inserted = 0
        for offset in range(0, len(rows), batch_size):
            batch = rows[offset : offset + batch_size]
            self.client.upsert(collection_name=self.collection, data=batch)
            inserted += len(batch)
        return inserted

    def load_collection(self) -> None:
        if not self.client.has_collection(collection_name=self.collection):
            raise ValueError(f"Milvus behavior collection does not exist: {self.collection}")
        self.client.load_collection(collection_name=self.collection)

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def search(
        self,
        query_vector: list[float],
        *,
        limit: int,
        model_id: str | None = None,
        exclude_model_id: str | None = None,
        include_persona_contaminated: bool = False,
    ) -> list[dict[str, Any]]:
        filters: list[str] = []
        if model_id:
            resolved = resolve_knowledge_baseline(model_id)
            filters.append(f'model_id == "{self._escape(resolved.behavior_model_id)}"')
        if exclude_model_id:
            resolved = resolve_knowledge_baseline(exclude_model_id)
            filters.append(f'model_id != "{self._escape(resolved.behavior_model_id)}"')
        if not include_persona_contaminated:
            filters.append("persona_contaminated == false")
        result = self.client.search(
            collection_name=self.collection,
            data=[query_vector],
            filter=" and ".join(filters),
            limit=limit,
            output_fields=[
                "id", "text", "model_id", "source_id", "trajectory_id", "sample_kind",
                "task_type", "outcome", "confidence", "persona_contaminated", "observed_only",
                "payload_json",
            ],
        )
        return result[0]

    def stats(self) -> dict[str, Any]:
        return self.client.get_collection_stats(collection_name=self.collection)

    def existing_ids(self, ids: list[str]) -> set[str]:
        if not ids:
            return set()
        existing: set[str] = set()
        for offset in range(0, len(ids), 200):
            rows = self.client.get(
                collection_name=self.collection,
                ids=ids[offset : offset + 200],
                output_fields=["id"],
            )
            existing.update(str(row["id"]) for row in rows if row.get("id"))
        return existing
