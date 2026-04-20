from __future__ import annotations

import re
from typing import Any


def mask_token(token: str, keep_start: int = 4, keep_end: int = 4) -> str:
    if not token:
        return ""
    if len(token) <= keep_start + keep_end + 3:
        return token[:2] + "***"
    return token[:keep_start] + "***" + token[-keep_end:]


def detect_basic_risks(token_value: str) -> dict[str, Any]:
    dangers: list[str] = []
    v = token_value or ""

    if v.startswith("sk-"):
        dangers.append("token形态类似API Key（sk-），泄露风险高")

    if len(v) < 16:
        dangers.append("token长度过短，可能弱口令/可猜测")

    if re.search(r"\s", v):
        dangers.append("token包含空白字符，可能复制粘贴错误")

    if _looks_like_jwt(v):
        dangers.append("token形态类似JWT，注意有效期与签名算法配置")

    risk_level = "low"
    if len(dangers) >= 3:
        risk_level = "high"
    elif len(dangers) >= 1:
        risk_level = "middle"

    suggestion = ""
    if dangers:
        suggestion = "建议启用白名单/限流，使用最小权限Token，并定期轮换。"

    return {"risk_level": risk_level, "security_hidden_dangers": dangers, "reinforcement_suggestion": suggestion}


def _looks_like_jwt(token: str) -> bool:
    parts = token.split(".")
    if len(parts) != 3:
        return False
    return all(_looks_like_base64url(p) for p in parts)


def _looks_like_base64url(s: str) -> bool:
    if not s:
        return False
    return re.fullmatch(r"[A-Za-z0-9_-]+", s) is not None

