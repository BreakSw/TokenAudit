from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(f"Environment file does not exist: {path}")
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[name.strip()] = value
    return values


def _first(values: dict[str, str], *names: str, default: str = "") -> str:
    for name in names:
        if name in os.environ:
            return os.environ[name]
        if name in values:
            return values[name]
    return default


def _resolve_uri(uri: str, project_root: Path) -> str:
    if uri.startswith(("http://", "https://")):
        return uri.rstrip("/")
    path = Path(uri)
    if not path.is_absolute():
        path = project_root / path
    return str(path.resolve())


@dataclass(frozen=True)
class KnowledgeSettings:
    project_root: Path
    raw_source_root: Path
    processed_root: Path
    milvus_uri: str
    milvus_token: str
    milvus_database: str
    milvus_collection: str
    behavior_collection: str
    milvus_metric_type: str
    embedding_base_url: str
    embedding_api_key: str
    embedding_model: str
    embedding_dimension: int
    embedding_timeout_seconds: float
    rerank_base_url: str
    rerank_api_key: str
    rerank_model: str
    rerank_timeout_seconds: float
    retrieval_top_k: int
    rerank_top_k: int
    behavior_retrieval_top_k: int
    behavior_rerank_top_k: int
    chunk_max_characters: int
    chunk_new_after_characters: int
    chunk_combine_under_characters: int
    chunk_overlap_characters: int
    tesseract_executable: Path
    tessdata_prefix: Path
    ocr_languages: tuple[str, ...]
    unstructured_hi_res_model: str

    @classmethod
    def load(cls, env_files: Iterable[str | Path]) -> "KnowledgeSettings":
        project_root = Path(__file__).resolve().parents[2]
        values: dict[str, str] = {}
        for env_file in env_files:
            values.update(_parse_env_file(Path(env_file).resolve()))

        milvus_uri = _resolve_uri(
            _first(
                values,
                "MILVUS_URI",
                "milvus-uri",
                default="./data/milvus/tokenaudit.db",
            ),
            project_root,
        )
        embedding_base_url = _first(
            values,
            "EMBEDDING_BASE_URL",
            "embedding-base-url",
            default="https://api.voyageai.com/v1",
        ).rstrip("/")
        embedding_api_key = _first(
            values,
            "EMBEDDING_API_KEY",
            "embedding-api-key",
        )
        if not embedding_api_key:
            raise ValueError("Embedding API key is missing.")
        rerank_api_key = _first(
            values,
            "RERANK_API_KEY",
            "rerank-api-key",
            default=embedding_api_key,
        )
        if not rerank_api_key:
            raise ValueError("Rerank API key is missing.")

        tesseract_executable = Path(
            _first(
                values,
                "TESSERACT_EXECUTABLE",
                "tesseract-executable",
                default=r"D:\download\OCR\tesseract.exe",
            )
        ).resolve()
        tessdata_prefix = Path(
            _first(
                values,
                "TESSDATA_PREFIX",
                "tessdata-prefix",
                default=str(tesseract_executable.parent / "tessdata"),
            )
        ).resolve()

        return cls(
            project_root=project_root,
            raw_source_root=project_root
            / "docs"
            / "rag"
            / "raw-sources"
            / "claude-fable-5",
            processed_root=project_root
            / "docs"
            / "rag"
            / "processed"
            / "claude-fable-5",
            milvus_uri=milvus_uri,
            milvus_token=_first(values, "MILVUS_TOKEN", "milvus-token"),
            milvus_database=_first(
                values,
                "MILVUS_DATABASE",
                "milvus-database",
                default="default",
            ),
            milvus_collection=_first(
                values,
                "MILVUS_COLLECTION",
                "milvus-collection",
                default="tokenaudit_knowledge_v4",
            ),
            behavior_collection=_first(
                values,
                "MILVUS_BEHAVIOR_COLLECTION",
                "milvus-behavior-collection",
                default="tokenaudit_behavior_v1",
            ),
            milvus_metric_type=_first(
                values,
                "MILVUS_METRIC_TYPE",
                "milvus-metric-type",
                default="COSINE",
            ).upper(),
            embedding_base_url=embedding_base_url,
            embedding_api_key=embedding_api_key,
            embedding_model=_first(
                values,
                "EMBEDDING_MODEL",
                "embedding-model",
                default="voyage-code-3",
            ),
            embedding_dimension=int(
                _first(
                    values,
                    "EMBEDDING_DIMENSION",
                    "embedding-dimension",
                    default="1024",
                )
            ),
            embedding_timeout_seconds=float(
                _first(
                    values,
                    "EMBEDDING_TIMEOUT_SECONDS",
                    "embedding-timeout-seconds",
                    default="60",
                )
            ),
            rerank_base_url=_first(
                values,
                "RERANK_BASE_URL",
                "rerank-base-url",
                default=embedding_base_url,
            ).rstrip("/"),
            rerank_api_key=rerank_api_key,
            rerank_model=_first(
                values,
                "RERANK_MODEL",
                "rerank-model",
                default="rerank-2.5",
            ),
            rerank_timeout_seconds=float(
                _first(
                    values,
                    "RERANK_TIMEOUT_SECONDS",
                    "rerank-timeout-seconds",
                    default="60",
                )
            ),
            retrieval_top_k=int(
                _first(
                    values,
                    "RAG_RETRIEVAL_TOP_K",
                    "rag-retrieval-top-k",
                    default="12",
                )
            ),
            rerank_top_k=int(
                _first(
                    values,
                    "RAG_RERANK_TOP_K",
                    "rag-rerank-top-k",
                    default="5",
                )
            ),
            behavior_retrieval_top_k=int(
                _first(
                    values,
                    "RAG_BEHAVIOR_RETRIEVAL_TOP_K",
                    "rag-behavior-retrieval-top-k",
                    default="20",
                )
            ),
            behavior_rerank_top_k=int(
                _first(
                    values,
                    "RAG_BEHAVIOR_RERANK_TOP_K",
                    "rag-behavior-rerank-top-k",
                    default="8",
                )
            ),
            chunk_max_characters=int(
                _first(values, "RAG_CHUNK_MAX_CHARACTERS", default="1800")
            ),
            chunk_new_after_characters=int(
                _first(values, "RAG_CHUNK_NEW_AFTER_CHARACTERS", default="1200")
            ),
            chunk_combine_under_characters=int(
                _first(values, "RAG_CHUNK_COMBINE_UNDER_CHARACTERS", default="300")
            ),
            chunk_overlap_characters=int(
                _first(values, "RAG_CHUNK_OVERLAP_CHARACTERS", default="120")
            ),
            tesseract_executable=tesseract_executable,
            tessdata_prefix=tessdata_prefix,
            ocr_languages=tuple(
                item.strip()
                for item in _first(values, "OCR_LANGUAGES", default="eng").split(",")
                if item.strip()
            ),
            unstructured_hi_res_model=_first(
                values,
                "UNSTRUCTURED_HI_RES_MODEL",
                default="yolox",
            ),
        )
