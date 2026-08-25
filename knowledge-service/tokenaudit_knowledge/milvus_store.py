from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pymilvus import DataType, MilvusClient

from .model_catalog import resolve_knowledge_baseline


class KnowledgeMilvusStore:
    def __init__(
        self,
        *,
        uri: str,
        token: str,
        database: str,
        collection: str,
        dimension: int,
        metric_type: str,
    ) -> None:
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
            description = self.client.describe_collection(
                collection_name=self.collection
            )
            vector_field = next(
                field for field in description["fields"] if field["name"] == "vector"
            )
            existing_dimension = int(vector_field["params"]["dim"])
            if existing_dimension != self.dimension:
                raise ValueError(
                    f"Milvus collection dimension is {existing_dimension}, expected {self.dimension}."
                )
            self.client.load_collection(collection_name=self.collection)
            return

        schema = MilvusClient.create_schema(auto_id=False, enable_dynamic_field=False)
        schema.add_field(
            field_name="id",
            datatype=DataType.VARCHAR,
            is_primary=True,
            max_length=128,
        )
        schema.add_field(
            field_name="vector",
            datatype=DataType.FLOAT_VECTOR,
            dim=self.dimension,
        )
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=8192)
        schema.add_field(field_name="model_id", datatype=DataType.VARCHAR, max_length=128)
        schema.add_field(field_name="record_type", datatype=DataType.VARCHAR, max_length=32)
        schema.add_field(field_name="claim_type", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="source_id", datatype=DataType.VARCHAR, max_length=128)
        schema.add_field(field_name="source_level", datatype=DataType.VARCHAR, max_length=8)
        schema.add_field(field_name="surface", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="content_hash", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="effective_from", datatype=DataType.VARCHAR, max_length=32)
        schema.add_field(field_name="authority", datatype=DataType.FLOAT)
        schema.add_field(field_name="audit_relevance", datatype=DataType.FLOAT)
        schema.add_field(field_name="eligible", datatype=DataType.BOOL)
        schema.add_field(field_name="fallback_contaminated", datatype=DataType.BOOL)
        schema.add_field(
            field_name="payload_json",
            datatype=DataType.VARCHAR,
            max_length=16384,
        )
        index_params = MilvusClient.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="AUTOINDEX",
            metric_type=self.metric_type,
        )
        self.client.create_collection(
            collection_name=self.collection,
            schema=schema,
            index_params=index_params,
            consistency_level="Strong",
        )
        self.client.load_collection(collection_name=self.collection)

    def load_collection(self) -> None:
        if not self.client.has_collection(collection_name=self.collection):
            raise ValueError(f"Milvus collection does not exist: {self.collection}")
        self.client.load_collection(collection_name=self.collection)

    def upsert_records(
        self,
        records: list[dict[str, Any]],
        vectors: list[list[float]],
    ) -> dict[str, Any]:
        if len(records) != len(vectors):
            raise ValueError("Record/vector count mismatch.")
        rows = []
        for record, vector in zip(records, vectors, strict=True):
            if not record.get("eligible_for_ground_truth"):
                raise ValueError(f"Refusing to insert quarantined record: {record['id']}")
            if record.get("fallback_contaminated"):
                raise ValueError(f"Refusing fallback-contaminated record: {record['id']}")
            if len(vector) != self.dimension:
                raise ValueError(f"Vector dimension mismatch for {record['id']}.")
            payload = {
                key: value
                for key, value in record.items()
                if key not in {"embedding_text"}
            }
            rows.append(
                {
                    "id": record["id"],
                    "vector": vector,
                    "text": record["embedding_text"][:8192],
                    "model_id": record["model_id"],
                    "record_type": record["record_type"],
                    "claim_type": record["claim_type"],
                    "source_id": record["source_id"],
                    "source_level": record["source_level"],
                    "surface": record.get("surface", "unspecified"),
                    "content_hash": record["content_hash"],
                    "effective_from": record.get("effective_from", ""),
                    "authority": float(record["authority"]),
                    "audit_relevance": float(record["audit_relevance"]),
                    "eligible": True,
                    "fallback_contaminated": False,
                    "payload_json": json.dumps(payload, ensure_ascii=False, sort_keys=True)[
                        :16384
                    ],
                }
            )
        return self.client.upsert(collection_name=self.collection, data=rows)

    @staticmethod
    def _escape_filter_value(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def query_all(self, model_id: str | None = None) -> list[dict[str, Any]]:
        filter_expression = 'eligible == true and fallback_contaminated == false'
        if model_id:
            resolved = resolve_knowledge_baseline(model_id)
            escaped_model_id = self._escape_filter_value(resolved.spec_model_id)
            filter_expression += f' and model_id == "{escaped_model_id}"'
        return self.client.query(
            collection_name=self.collection,
            filter=filter_expression,
            output_fields=[
                "id",
                "text",
                "model_id",
                "record_type",
                "claim_type",
                "source_id",
                "source_level",
                "surface",
                "content_hash",
                "effective_from",
                "authority",
                "audit_relevance",
                "eligible",
                "fallback_contaminated",
                "payload_json",
            ],
            limit=1000,
        )

    def search(
        self,
        query_vector: list[float],
        *,
        limit: int = 5,
        model_id: str | None = None,
    ) -> list[dict[str, Any]]:
        filter_expression = 'eligible == true and fallback_contaminated == false'
        if model_id:
            resolved = resolve_knowledge_baseline(model_id)
            escaped_model_id = self._escape_filter_value(resolved.spec_model_id)
            filter_expression += f' and model_id == "{escaped_model_id}"'
        result = self.client.search(
            collection_name=self.collection,
            data=[query_vector],
            filter=filter_expression,
            limit=limit,
            output_fields=[
                "id",
                "text",
                "model_id",
                "record_type",
                "claim_type",
                "source_id",
                "source_level",
                "surface",
                "authority",
                "audit_relevance",
            ],
        )
        return result[0]

    def stats(self) -> dict[str, Any]:
        return self.client.get_collection_stats(collection_name=self.collection)
