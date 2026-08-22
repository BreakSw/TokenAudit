from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from audit_core.config import AuditConfig
from audit_core.scripts.deepseek_api import DeepSeekError, deepseek_chat, normalize_chat_completions_url


class DeepSeekRedactionTest(unittest.TestCase):
    def test_normalizes_service_roots_and_preserves_full_endpoints(self) -> None:
        self.assertEqual(
            normalize_chat_completions_url("https://api.deepseek.com"),
            "https://api.deepseek.com/v1/chat/completions",
        )
        self.assertEqual(
            normalize_chat_completions_url("https://judge.example/v1"),
            "https://judge.example/v1/chat/completions",
        )
        self.assertEqual(
            normalize_chat_completions_url("https://judge.example/compatibility/v1/chat/completions"),
            "https://judge.example/compatibility/v1/chat/completions",
        )

    def test_redacts_audited_token_before_sending_judge_payload(self) -> None:
        response = Mock()
        response.status_code = 200
        response.headers = {"content-type": "application/json"}
        response.json.return_value = {"choices": [{"message": {"content": "{}"}}]}
        audited_token = "sk-audited-secret-value"
        config = AuditConfig(
            deepseek_base_url="https://api.deepseek.com/v1/chat/completions",
            deepseek_api_key="judge-key",
            deepseek_model="deepseek-chat",
            deepseek_temperature=0.2,
            deepseek_max_tokens=128,
            request_timeout_s=2,
            export_dir=".",
        )

        with patch("audit_core.scripts.deepseek_api.requests.post", return_value=response) as post:
            deepseek_chat(
                config=config,
                messages=[{"role": "user", "content": f"untrusted response: {audited_token}"}],
                sensitive_values=[audited_token],
            )

        payload = post.call_args.kwargs["json"]
        self.assertNotIn(audited_token, str(payload))
        self.assertIn("[REDACTED]", str(payload))

    def test_never_puts_judge_api_key_in_payload(self) -> None:
        response = Mock()
        response.status_code = 200
        response.headers = {"content-type": "application/json"}
        response.json.return_value = {"choices": [{"message": {"content": "{}"}}]}
        config = AuditConfig("https://judge.example/v1", "judge-key", "judge", 0.2, 128, 2, ".")

        with patch("audit_core.scripts.deepseek_api.requests.post", return_value=response) as post:
            deepseek_chat(config=config, messages=[{"role": "user", "content": "facts"}])

        self.assertNotIn("judge-key", str(post.call_args.kwargs["json"]))
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer judge-key")

    def test_posts_a_service_root_to_the_normalized_chat_endpoint(self) -> None:
        response = Mock()
        response.status_code = 200
        response.headers = {"content-type": "application/json"}
        response.json.return_value = {"choices": [{"message": {"content": "OK"}}]}
        config = AuditConfig("https://api.deepseek.com", "judge-key", "judge", 0.2, 128, 2, ".")

        with patch("audit_core.scripts.deepseek_api.requests.post", return_value=response) as post:
            result = deepseek_chat(config=config, messages=[{"role": "user", "content": "ping"}])

        self.assertEqual(post.call_args.args[0], "https://api.deepseek.com/v1/chat/completions")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status_code"], 200)

    def test_raises_a_structured_error_for_http_failures(self) -> None:
        response = Mock()
        response.status_code = 404
        response.headers = {"content-type": "application/json"}
        response.json.return_value = {"error": {"message": "model not found"}}
        config = AuditConfig("https://judge.example", "judge-key", "missing", 0.2, 128, 2, ".")

        with patch("audit_core.scripts.deepseek_api.requests.post", return_value=response):
            with self.assertRaises(DeepSeekError) as raised:
                deepseek_chat(config=config, messages=[{"role": "user", "content": "ping"}])

        self.assertEqual(raised.exception.status_code, 404)
        self.assertEqual(raised.exception.reason, "endpoint_or_model_not_found")
        self.assertEqual(raised.exception.url, "https://judge.example/v1/chat/completions")


if __name__ == "__main__":
    unittest.main()
