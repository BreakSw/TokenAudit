from __future__ import annotations

from pathlib import Path

from tokenaudit_knowledge.processor import _clean_source, process_fable5


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "docs" / "rag" / "raw-sources" / "claude-fable-5"


def test_cleaner_removes_front_matter_and_private_use_glyphs() -> None:
    raw = "---\nsource_id: \"demo\"\npriority: \"P0\"\n---\n\ue056Copy page\n# Title\nUseful text.\n"
    metadata, clean, assets, dropped = _clean_source("demo", raw)
    assert metadata["source_id"] == "demo"
    assert "source_id:" not in clean
    assert "\ue056" not in clean
    assert "Useful text." in clean
    assert not assets
    assert not dropped


def test_fable5_pipeline_quarantines_fallback_metrics(tmp_path: Path) -> None:
    result = process_fable5(RAW_ROOT, tmp_path, download_assets=False)
    assert result["stats"]["documents"] == 5
    assert result["stats"]["attributes"] == 6
    assert result["stats"]["ground_truth_claims"] > 0
    assert all(
        not record["fallback_contaminated"]
        for record in result["ground_truth_claims"] + result["attributes"]
    )
    quarantined_ids = {claim["id"] for claim in result["quarantine"]["claims"]}
    assert "fable5-aa-intelligence" in quarantined_ids
    assert "fable5-aa-speed" in quarantined_ids
    assert "fable5-aa-ttft" in quarantined_ids


def test_raw_sections_are_never_embedding_eligible(tmp_path: Path) -> None:
    result = process_fable5(RAW_ROOT, tmp_path, download_assets=False)
    assert result["sections"]
    assert all(not section["embedding_eligible"] for section in result["sections"])
