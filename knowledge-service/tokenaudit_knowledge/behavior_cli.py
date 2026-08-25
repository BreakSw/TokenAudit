from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .behavior_pipeline import (
    build_behavior_profile_cards,
    load_behavior_records,
    select_behavior_evidence_records,
    write_behavior_records,
    write_profile_cards,
)
from .behavior_store import BehaviorMilvusStore
from .config import KnowledgeSettings
from .embedding import VoyageEmbeddingClient


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and inspect TokenAudit behavior RAG.")
    parser.add_argument("command", choices=("prepare", "build", "stats"))
    parser.add_argument("--env-file", action="append", default=[])
    parser.add_argument("--dataset-root")
    parser.add_argument("--output")
    parser.add_argument("--samples-per-model", type=int, default=20)
    parser.add_argument("--rebuild", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    settings = KnowledgeSettings.load(args.env_file)
    dataset_root = Path(args.dataset_root).resolve() if args.dataset_root else (
        settings.project_root / "docs" / "rag" / "datasets" / "huggingface-selected-v1"
    )
    output = Path(args.output).resolve() if args.output else (
        settings.project_root / "docs" / "rag" / "processed" / "behavior-v1" / "records.jsonl"
    )
    store = BehaviorMilvusStore(
        uri=settings.milvus_uri,
        token=settings.milvus_token,
        database=settings.milvus_database,
        collection=settings.behavior_collection,
        dimension=settings.embedding_dimension,
        metric_type=settings.milvus_metric_type,
    )
    try:
        if args.command == "stats":
            print(json.dumps({"collection": settings.behavior_collection, **store.stats()}, ensure_ascii=False, indent=2))
            return 0

        records, stats = load_behavior_records(dataset_root)
        write_behavior_records(records, output, stats)
        profile_cards = build_behavior_profile_cards(records)
        evidence_records = select_behavior_evidence_records(
            records, samples_per_model=args.samples_per_model
        )
        profile_output = output.with_name("profiles.jsonl")
        evidence_output = output.with_name("embedded-evidence.jsonl")
        write_profile_cards(profile_cards, profile_output)
        write_profile_cards(evidence_records, evidence_output)
        embedding_records = profile_cards + evidence_records
        if args.command == "prepare":
            print(json.dumps({"output": str(output), "profile_output": str(profile_output), "evidence_output": str(evidence_output), "profile_cards": len(profile_cards), "evidence_records": len(evidence_records), "embedding_records": len(embedding_records), **stats}, ensure_ascii=False, indent=2))
            return 0


        embedder = VoyageEmbeddingClient(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
            timeout_seconds=settings.embedding_timeout_seconds,
            batch_size=64,
            max_batch_characters=24000,
            min_request_interval_seconds=20,
        )
        store.ensure_collection(rebuild=args.rebuild)
        existing = set() if args.rebuild else store.existing_ids([record.id for record in embedding_records])
        pending_records = [record for record in embedding_records if record.id not in existing]
        inserted = 0
        pipeline_batch_size = 32
        for offset in range(0, len(pending_records), pipeline_batch_size):
            batch = pending_records[offset : offset + pipeline_batch_size]
            vectors = embedder.embed_documents([record.embedding_text for record in batch])
            inserted += store.upsert_records(batch, vectors)
            sys.stderr.write(
                json.dumps(
                    {
                        "phase": "behavior_embedding",
                        "completed": len(existing) + inserted,
                        "total": len(embedding_records),
                        "percent": round((len(existing) + inserted) * 100 / len(embedding_records), 2),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            sys.stderr.flush()
        result = {
            "collection": settings.behavior_collection,
            "milvus_uri": settings.milvus_uri,
            "inserted": inserted,
            "already_present": len(existing),
            "stats": store.stats(),
            "processed_output": str(output),
            "profile_output": str(profile_output),
            "evidence_output": str(evidence_output),
            "profile_cards": len(profile_cards),
            "evidence_records": len(evidence_records),
            "normalization": stats,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
