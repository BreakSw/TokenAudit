from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditConfig:
    deepseek_base_url: str
    deepseek_api_key: str | None
    deepseek_model: str
    deepseek_temperature: float
    deepseek_max_tokens: int
    request_timeout_s: float
    export_dir: str


def load_config() -> AuditConfig:
    deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1/chat/completions")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-v2")
    deepseek_temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.2"))
    deepseek_max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "2048"))
    request_timeout_s = float(os.getenv("AUDIT_REQUEST_TIMEOUT_S", "60"))
    export_dir = os.getenv("AUDIT_EXPORT_DIR", os.path.abspath(os.path.join(os.getcwd(), "..", "data", "report")))
    return AuditConfig(
        deepseek_base_url=deepseek_base_url,
        deepseek_api_key=deepseek_api_key,
        deepseek_model=deepseek_model,
        deepseek_temperature=deepseek_temperature,
        deepseek_max_tokens=deepseek_max_tokens,
        request_timeout_s=request_timeout_s,
        export_dir=export_dir,
    )
