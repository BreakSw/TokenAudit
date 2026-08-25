from __future__ import annotations

from pathlib import Path

from tokenaudit_knowledge.dedup import LlamaIndexChunkDeduplicator
from tokenaudit_knowledge.unstructured_pipeline import (
    ChunkingPolicy,
    UnstructuredDocumentPipeline,
)


def test_unstructured_by_title_preserves_table_and_removes_noise(
    tmp_path: Path,
) -> None:
    content = tmp_path / "content.md"
    content.write_text(
        """---
source_id: "demo"
priority: "P0"
source_url: "https://example.test/model"
captured_at: "2026-08-24T00:00:00Z"
---
Copy page

# Capability

Useful model evidence.

| Model | Context |
| --- | --- |
| Demo | 1M |
""",
        encoding="utf-8",
    )
    pipeline = UnstructuredDocumentPipeline(
        chunking=ChunkingPolicy(),
        tesseract_executable=Path("missing-tesseract-for-non-ocr-test"),
        tessdata_prefix=Path("missing-tessdata-for-non-ocr-test"),
        ocr_languages=["eng"],
        hi_res_model_name="yolox",
    )
    result = pipeline.process_source(content)
    assert "Copy page" not in result["clean_text"]
    assert "Useful model evidence" in result["clean_text"]
    assert len(result["tables"]) == 1
    assert result["chunks"]
    assert all(chunk["chunk_strategy"] == "unstructured_by_title" for chunk in result["chunks"])


def test_llama_index_dedup_merges_provenance() -> None:
    chunks = [
        {
            "id": "chunk-a",
            "text": "same evidence",
            "source_ids": ["source-a"],
            "source_urls": ["https://a.test"],
        },
        {
            "id": "chunk-b",
            "text": "same   evidence",
            "source_ids": ["source-b"],
            "source_urls": ["https://b.test"],
        },
    ]
    unique, aliases, stats = LlamaIndexChunkDeduplicator().deduplicate(chunks)
    assert len(unique) == 1
    assert stats["duplicates_removed"] == 1
    assert aliases["chunk-b"] == "chunk-a"
    assert unique[0]["source_ids"] == ["source-a", "source-b"]
