from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import Element, Table, Title
from unstructured.partition.image import partition_image
from unstructured.partition.md import partition_md


FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
PRIVATE_USE_RE = re.compile(r"[\uE000-\uF8FF]")


def sha256(value: str | bytes) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, text[match.end() :]


@dataclass(frozen=True)
class ChunkingPolicy:
    max_characters: int = 1800
    new_after_n_characters: int = 1200
    combine_text_under_n_characters: int = 300
    overlap_characters: int = 120


class WebNoiseFilter:
    """Filters page chrome after Unstructured has identified document elements."""

    _exact_noise = {
        "Copy page",
        "Was this page helpful?",
        "Tap to unmute",
        "Claude547K subscribers",
        "NEW",
        "Add model from specific provider",
        "Reasoning models are indicated by a lightbulb icon",
        "Premium",
        "Log in K",
        "•",
        "01 /26",
    }

    def apply(
        self,
        source_id: str,
        elements: list[Element],
    ) -> tuple[list[Element], list[dict[str, str]]]:
        kept: list[Element] = []
        dropped: list[dict[str, str]] = []
        dropping = False
        started = source_id != "05-japan-ai"

        for element in elements:
            text = PRIVATE_USE_RE.sub("", str(element)).strip()
            text = re.sub(r"\s+", " ", text)
            if not text:
                continue

            if isinstance(element, Title):
                title = text.strip()
                if source_id == "05-japan-ai" and title == "Claude Fable 5とは":
                    started = True
                if not started:
                    continue
                if source_id == "01-anthropic-fable":
                    dropping = title in {"Announcements", "Hear from our customers"}
                elif source_id == "03-anthropic-research":
                    if title == "Related content":
                        dropped.append(
                            {
                                "source_id": source_id,
                                "heading": title,
                                "reason": "related content",
                            }
                        )
                        break
                    dropping = title == "Early feedback for Claude Fable 5"
                else:
                    dropping = False
                if dropping:
                    dropped.append(
                        {
                            "source_id": source_id,
                            "heading": title,
                            "reason": "marketing or duplicate section",
                        }
                    )
                    continue

            if not started or dropping:
                continue
            if text in self._exact_noise:
                continue
            if any(
                marker in text
                for marker in (
                    "youtube.com/watch",
                    "youtube-nocookie.com/channel",
                    "twitter.com/intent/tweet",
                    "linkedin.com/shareArticle",
                    "uqid=",
                )
            ):
                continue
            if source_id == "04-artificial-analysis" and (
                re.fullmatch(r"\d+ of \d+ models", text)
                or text.startswith("Open Weights / ProprietaryReasoning")
                or text.startswith("CodingTool UsePrivate Dataset")
                or text.startswith("AnthropicMetaOpenAI")
            ):
                continue
            if source_id == "05-japan-ai" and text in {"目次", "【関連記事】"}:
                continue

            element.text = text
            kept.append(element)
        return kept, dropped


class UnstructuredDocumentPipeline:
    def __init__(
        self,
        *,
        chunking: ChunkingPolicy,
        tesseract_executable: Path,
        tessdata_prefix: Path,
        ocr_languages: list[str],
        hi_res_model_name: str,
        request_timeout_seconds: float = 60,
    ) -> None:
        self.chunking = chunking
        self.tesseract_executable = tesseract_executable
        self.tessdata_prefix = tessdata_prefix
        self.ocr_languages = ocr_languages
        self.hi_res_model_name = hi_res_model_name
        self.request_timeout_seconds = request_timeout_seconds
        self.noise_filter = WebNoiseFilter()

    def process_source(self, content_path: Path) -> dict[str, Any]:
        raw_text = content_path.read_text(encoding="utf-8-sig")
        front_matter, body = parse_front_matter(raw_text)
        source_id = front_matter.get("source_id") or content_path.parent.name
        elements = partition_md(
            text=body,
            metadata_filename=content_path.name,
        )
        filtered, dropped = self.noise_filter.apply(source_id, list(elements))
        clean_text = "\n".join(str(element) for element in filtered).strip() + "\n"

        element_rows = [
            self._element_record(element, index, front_matter)
            for index, element in enumerate(filtered)
        ]
        table_rows = [row for row in element_rows if row["element_type"] == "Table"]
        chunk_elements = chunk_by_title(
            filtered,
            max_characters=self.chunking.max_characters,
            new_after_n_chars=self.chunking.new_after_n_characters,
            combine_text_under_n_chars=self.chunking.combine_text_under_n_characters,
            overlap=self.chunking.overlap_characters,
            overlap_all=False,
            multipage_sections=True,
            include_orig_elements=True,
            isolate_table=True,
        )
        chunks = [
            self._chunk_record(chunk, index, front_matter)
            for index, chunk in enumerate(chunk_elements)
        ]
        assets = self._discover_images(body, front_matter)
        return {
            "front_matter": front_matter,
            "clean_text": clean_text,
            "elements": element_rows,
            "tables": table_rows,
            "chunks": chunks,
            "assets": assets,
            "dropped_sections": dropped,
        }

    def download_and_ocr_assets(
        self,
        assets: list[dict[str, Any]],
        output_root: Path,
    ) -> list[dict[str, Any]]:
        asset_root = output_root / "assets"
        asset_root.mkdir(parents=True, exist_ok=True)
        self._configure_ocr()
        seen: dict[str, dict[str, Any]] = {}
        results: list[dict[str, Any]] = []

        for asset in assets:
            if asset["role"] == "decorative_or_unlabelled_image":
                results.append(
                    {
                        **asset,
                        "download_status": "skipped",
                        "ocr_status": "skipped_decorative",
                        "embedding_eligible": False,
                    }
                )
                continue
            if asset["url"] in seen:
                results.append({**asset, **seen[asset["url"]], "duplicate_asset": True})
                continue

            record = {
                **asset,
                "duplicate_asset": False,
                "embedding_eligible": False,
                "evidence_verified": False,
                "quarantine_reason": "image OCR requires manual verification before Ground Truth",
            }
            try:
                response = requests.get(asset["url"], timeout=self.request_timeout_seconds)
                response.raise_for_status()
                extension = self._extension(response.headers.get("Content-Type", ""))
                target = asset_root / f"{asset['asset_id']}{extension}"
                target.write_bytes(response.content)
                record.update(
                    {
                        "download_status": "success",
                        "local_path": str(target.relative_to(output_root)).replace("\\", "/"),
                        "bytes": len(response.content),
                        "sha256": sha256(response.content),
                    }
                )
                record.update(self._ocr_image(target, asset["role"]))
            except Exception as exc:
                record.update(
                    {
                        "download_status": record.get("download_status", "failed"),
                        "ocr_status": "failed",
                        "error": str(exc),
                    }
                )
            seen[asset["url"]] = {
                key: value
                for key, value in record.items()
                if key
                in {
                    "download_status",
                    "local_path",
                    "bytes",
                    "sha256",
                    "ocr_status",
                    "ocr_strategy",
                    "ocr_text",
                    "ocr_characters",
                    "ocr_element_types",
                    "tables",
                    "table_html",
                    "embedding_eligible",
                    "evidence_verified",
                    "quarantine_reason",
                }
            }
            results.append(record)
        return results

    def _configure_ocr(self) -> None:
        if not self.tesseract_executable.exists():
            raise FileNotFoundError(
                f"Tesseract executable does not exist: {self.tesseract_executable}"
            )
        os.environ["TESSDATA_PREFIX"] = str(self.tessdata_prefix)
        path_parts = os.environ.get("PATH", "").split(os.pathsep)
        executable_parent = str(self.tesseract_executable.parent)
        if executable_parent not in path_parts:
            os.environ["PATH"] = executable_parent + os.pathsep + os.environ.get("PATH", "")
        import unstructured_pytesseract

        unstructured_pytesseract.pytesseract.tesseract_cmd = str(
            self.tesseract_executable
        )

    def _ocr_image(self, target: Path, role: str) -> dict[str, Any]:
        if target.suffix.lower() == ".svg":
            return {
                "ocr_status": "skipped_vector_graphic",
                "ocr_strategy": "not_applicable",
                "ocr_text": "",
                "ocr_characters": 0,
                "ocr_element_types": [],
                "tables": 0,
                "table_html": [],
            }
        strategy = "hi_res" if role == "benchmark_image_pending_verification" else "ocr_only"
        kwargs: dict[str, Any] = {
            "filename": str(target),
            "strategy": strategy,
            "languages": self.ocr_languages,
            "infer_table_structure": role == "benchmark_image_pending_verification",
        }
        if strategy == "hi_res":
            kwargs["hi_res_model_name"] = self.hi_res_model_name
        try:
            elements = partition_image(**kwargs)
            used_strategy = strategy
        except Exception:
            if strategy != "hi_res":
                raise
            elements = partition_image(
                filename=str(target),
                strategy="ocr_only",
                languages=self.ocr_languages,
            )
            used_strategy = "ocr_only_fallback"

        text = "\n".join(str(element) for element in elements).strip()
        tables = [element for element in elements if isinstance(element, Table)]
        return {
            "ocr_status": "success" if text else "empty",
            "ocr_strategy": used_strategy,
            "ocr_text": text,
            "ocr_characters": len(text),
            "ocr_element_types": [type(element).__name__ for element in elements],
            "tables": len(tables),
            "table_html": [
                table.metadata.text_as_html
                for table in tables
                if table.metadata.text_as_html
            ],
        }

    @staticmethod
    def _element_record(
        element: Element,
        index: int,
        metadata: dict[str, str],
    ) -> dict[str, Any]:
        text = str(element).strip()
        element_type = type(element).__name__
        source_id = metadata.get("source_id", "")
        digest = sha256(f"{source_id}|{index}|{element_type}|{text}")
        element_id = f"element-{digest[:20]}"
        return {
            "id": element_id,
            "source_id": metadata.get("source_id", ""),
            "source_level": metadata.get("priority", ""),
            "source_url": metadata.get("source_url", ""),
            "captured_at": metadata.get("captured_at", ""),
            "element_type": element_type,
            "text": text,
            "characters": len(text),
            "table_html": element.metadata.text_as_html if isinstance(element, Table) else None,
            "embedding_eligible": False,
        }

    @staticmethod
    def _chunk_record(
        chunk: Element,
        index: int,
        metadata: dict[str, str],
    ) -> dict[str, Any]:
        text = str(chunk).strip()
        original_elements = chunk.metadata.orig_elements or []
        titles = [str(element).strip() for element in original_elements if isinstance(element, Title)]
        heading = titles[-1] if titles else metadata.get("title", "Preamble")
        source_id = metadata.get("source_id", "")
        digest = sha256(f"{source_id}|{index}|{heading}|{text}")
        chunk_id = f"chunk-{digest[:20]}"
        return {
            "id": chunk_id,
            "record_type": "evidence_chunk",
            "model_id": "claude-fable-5",
            "subject_model": "claude-fable-5",
            "model_family": "claude",
            "model_version": "5",
            "source_id": source_id,
            "source_ids": [source_id],
            "source_level": metadata.get("priority", ""),
            "source_url": metadata.get("source_url", ""),
            "source_urls": [metadata.get("source_url", "")],
            "captured_at": metadata.get("captured_at", ""),
            "heading": heading,
            "chunk_index": index,
            "chunk_strategy": "unstructured_by_title",
            "element_types": [type(element).__name__ for element in original_elements],
            "text": text,
            "characters": len(text),
            "content_hash": sha256(re.sub(r"\s+", " ", text).strip()),
            "fallback_contaminated": source_id == "04-artificial-analysis",
            "evidence_verified": False,
            "eligible_for_ground_truth": False,
            "embedding_eligible": False,
        }

    @staticmethod
    def _discover_images(
        markdown_body: str,
        metadata: dict[str, str],
    ) -> list[dict[str, Any]]:
        source_id = metadata.get("source_id", "")
        source_level = metadata.get("priority", "")
        current_heading = ""
        assets: list[dict[str, Any]] = []
        for line in markdown_body.splitlines():
            heading_match = HEADING_RE.match(line.strip())
            if heading_match:
                current_heading = PRIVATE_USE_RE.sub("", heading_match.group(2)).strip()
            for match in IMAGE_RE.finditer(line):
                alt, url = match.groups()
                context = f"{alt} {current_heading}".lower()
                if any(word in context for word in ("benchmark", "evaluation", "table", "graph")):
                    role = "benchmark_image_pending_verification"
                elif "logo" in context or not alt.strip():
                    role = "decorative_or_unlabelled_image"
                else:
                    role = "supporting_image_pending_review"
                assets.append(
                    {
                        "asset_id": f"asset-{sha256(url)[:16]}",
                        "source_id": source_id,
                        "source_level": source_level,
                        "source_url": metadata.get("source_url", ""),
                        "captured_at": metadata.get("captured_at", ""),
                        "heading": current_heading,
                        "alt": alt.strip(),
                        "url": url,
                        "role": role,
                        "embedding_eligible": False,
                    }
                )
        return assets

    @staticmethod
    def _extension(content_type: str) -> str:
        lowered = content_type.lower()
        if "png" in lowered:
            return ".png"
        if "jpeg" in lowered or "jpg" in lowered:
            return ".jpg"
        if "webp" in lowered:
            return ".webp"
        if "svg" in lowered:
            return ".svg"
        return ".img"
