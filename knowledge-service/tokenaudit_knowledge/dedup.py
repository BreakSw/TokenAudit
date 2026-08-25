from __future__ import annotations

import re
from typing import Any

from llama_index.core.ingestion import DocstoreStrategy, IngestionPipeline
from llama_index.core.schema import TextNode
from llama_index.core.storage.docstore import SimpleDocumentStore


class LlamaIndexChunkDeduplicator:
    """Exact content deduplication with provenance merging.

    LlamaIndex owns the canonical node hashing and duplicate decision. TokenAudit
    then merges source references so deduplication never breaks the evidence chain.
    """

    def deduplicate(
        self,
        chunks: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, Any]]:
        nodes = [
            TextNode(
                id_=chunk["id"],
                text=self._normalized_text(chunk["text"]),
            )
            for chunk in chunks
        ]
        pipeline = IngestionPipeline(
            transformations=[],
            docstore=SimpleDocumentStore(),
            docstore_strategy=DocstoreStrategy.DUPLICATES_ONLY,
        )
        unique_nodes = pipeline.run(nodes=nodes)
        canonical_by_hash = {node.hash: node.node_id for node in unique_nodes}
        chunk_by_id = {chunk["id"]: dict(chunk) for chunk in chunks}
        aliases: dict[str, str] = {}

        for node in nodes:
            aliases[node.node_id] = canonical_by_hash[node.hash]

        unique_chunks: list[dict[str, Any]] = []
        for node in unique_nodes:
            canonical = chunk_by_id[node.node_id]
            duplicate_ids = [
                chunk_id
                for chunk_id, canonical_id in aliases.items()
                if canonical_id == node.node_id and chunk_id != node.node_id
            ]
            source_chunks = [canonical, *(chunk_by_id[item] for item in duplicate_ids)]
            canonical["duplicate_chunk_ids"] = duplicate_ids
            canonical["source_ids"] = sorted(
                {source_id for chunk in source_chunks for source_id in chunk["source_ids"]}
            )
            canonical["source_urls"] = sorted(
                {
                    source_url
                    for chunk in source_chunks
                    for source_url in chunk["source_urls"]
                    if source_url
                }
            )
            canonical["dedup_hash"] = node.hash
            unique_chunks.append(canonical)

        stats = {
            "engine": "llama-index-core",
            "strategy": "DocstoreStrategy.DUPLICATES_ONLY",
            "input_chunks": len(chunks),
            "unique_chunks": len(unique_chunks),
            "duplicates_removed": len(chunks) - len(unique_chunks),
        }
        return unique_chunks, aliases, stats

    @staticmethod
    def _normalized_text(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
