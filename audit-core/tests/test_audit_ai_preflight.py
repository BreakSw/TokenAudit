from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch

from audit_core.cli import main
from audit_core.config import AuditConfig
from audit_core.scripts.audit_ai_preflight import run_audit_ai_preflight
from audit_core.scripts.deepseek_api import DeepSeekError


def _config() -> AuditConfig:
    return AuditConfig("https://judge.example", "judge-key", "judge-model", 0.2, 128, 10, ".")


class AuditAiPreflightTest(unittest.TestCase):
    @patch("audit_core.scripts.audit_ai_preflight.log_event")
    @patch("audit_core.scripts.audit_ai_preflight.deepseek_chat")
    def test_passes_after_a_compatible_judge_response(self, chat_mock, log_mock):
        chat_mock.return_value = {
            "ok": True,
            "status_code": 200,
            "elapsed_ms": 25,
            "response": {"choices": [{"message": {"content": "OK"}}]},
            "endpoint": "chat_completions",
            "url": "https://judge.example/v1/chat/completions",
        }

        result = run_audit_ai_preflight(config=_config())

        self.assertTrue(result["passed"])
        self.assertEqual(result["reason"], "connected")
        self.assertEqual(chat_mock.call_args.kwargs["max_tokens"], 8)
        self.assertEqual(chat_mock.call_args.kwargs["timeout_s"], 10)
        self.assertEqual(log_mock.call_args_list[-1].args[0], "audit_ai_preflight_end")

    @patch("audit_core.scripts.audit_ai_preflight.log_event")
    @patch("audit_core.scripts.audit_ai_preflight.deepseek_chat")
    def test_returns_a_structured_failure(self, chat_mock, _log_mock):
        chat_mock.side_effect = DeepSeekError(
            "model not found",
            reason="endpoint_or_model_not_found",
            status_code=404,
            elapsed_ms=20,
            url="https://judge.example/v1/chat/completions",
        )

        result = run_audit_ai_preflight(config=_config())

        self.assertFalse(result["passed"])
        self.assertEqual(result["status_code"], 404)
        self.assertEqual(result["reason"], "endpoint_or_model_not_found")

    @patch("audit_core.cli.OrchestratorAgent")
    @patch("audit_core.cli.run_audit_ai_preflight")
    @patch("audit_core.cli.run_relay_preflight")
    @patch("audit_core.cli.load_config")
    def test_cli_stops_before_agents_when_auditor_preflight_fails(
        self,
        config_mock,
        relay_mock,
        audit_ai_mock,
        orchestrator_mock,
    ):
        config_mock.return_value = _config()
        relay_mock.return_value = {
            "passed": True,
            "reason": "connected",
            "status_code": 200,
            "message": "",
            "model": "claimed-model",
        }
        audit_ai_mock.return_value = {
            "passed": False,
            "reason": "endpoint_or_model_not_found",
            "status_code": 404,
            "message": "model not found",
            "model": "judge-model",
            "endpoint": "chat_completions",
            "url": "https://judge.example/v1/chat/completions",
        }
        stdin = io.StringIO(json.dumps({
            "token_id": 1,
            "audited_token": "secret-token",
            "platform": "relay",
            "token_base_url": "https://relay.example",
            "claimed_model": "claimed-model",
        }))
        stdout = io.StringIO()
        stderr = io.StringIO()

        with patch("sys.stdin", stdin), patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            exit_code = main()

        self.assertEqual(exit_code, 4)
        orchestrator_mock.return_value.run.assert_not_called()
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("audit_ai_preflight_failed", stderr.getvalue())
        self.assertNotIn("secret-token", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
