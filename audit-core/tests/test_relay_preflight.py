import io
import json
import unittest
from unittest.mock import patch

from audit_core.cli import main
from audit_core.config import AuditConfig
from audit_core.scripts.relay_preflight import run_relay_preflight


def _response(status_code=200, response=None, ok=True):
    return {
        "status_code": status_code,
        "elapsed_ms": 12,
        "response": response if response is not None else {"choices": [{"message": {"content": "OK"}}]},
        "ok": ok,
        "endpoint": "chat_completions",
        "url": "https://relay.example/v1/chat/completions",
    }


class RelayPreflightTest(unittest.TestCase):
    @patch("audit_core.scripts.relay_preflight.log_event")
    @patch("audit_core.scripts.relay_preflight.token_chat", return_value=_response())
    def test_passes_only_after_a_real_compatible_model_response(self, token_chat_mock, log_event_mock):
        result = run_relay_preflight(
            base_url="https://relay.example",
            token="secret-token",
            model="claimed-model",
            timeout_s=60,
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["reason"], "connected")
        self.assertEqual(token_chat_mock.call_args.kwargs["max_tokens"], 8)
        self.assertEqual(token_chat_mock.call_args.kwargs["timeout_s"], 20.0)
        self.assertEqual(log_event_mock.call_args_list[-1].args[0], "preflight_end")

    @patch("audit_core.scripts.relay_preflight.log_event")
    @patch(
        "audit_core.scripts.relay_preflight.token_chat",
        return_value=_response(401, {"error": {"message": "bad secret-token"}}, False),
    )
    def test_returns_sanitized_authentication_failure(self, _token_chat_mock, _log_event_mock):
        result = run_relay_preflight(
            base_url="https://relay.example",
            token="secret-token",
            model="claimed-model",
            timeout_s=10,
        )

        self.assertFalse(result["passed"])
        self.assertEqual(result["reason"], "authentication_failed")
        self.assertNotIn("secret-token", result["message"])
        self.assertIn("[REDACTED]", result["message"])

    @patch("audit_core.scripts.relay_preflight.log_event")
    @patch(
        "audit_core.scripts.relay_preflight.token_chat",
        return_value=_response(
            403,
            {"error": {"message": "This model is not available in your region."}},
            False,
        ),
    )
    def test_classifies_region_restriction_separately_from_authentication(self, _token_chat_mock, _log_event_mock):
        result = run_relay_preflight(
            base_url="https://relay.example",
            token="secret-token",
            model="provider/model",
            timeout_s=10,
        )

        self.assertFalse(result["passed"])
        self.assertEqual(result["reason"], "region_restricted")
        self.assertEqual(result["status_code"], 403)

    @patch("audit_core.scripts.relay_preflight.log_event")
    @patch("audit_core.scripts.relay_preflight.token_chat", return_value=_response(200, {"status": "ok"}, True))
    def test_rejects_non_openai_response_shapes(self, _token_chat_mock, _log_event_mock):
        result = run_relay_preflight(
            base_url="https://relay.example",
            token="secret-token",
            model="claimed-model",
            timeout_s=10,
        )

        self.assertFalse(result["passed"])
        self.assertEqual(result["reason"], "incompatible_response")

    @patch("audit_core.cli.OrchestratorAgent")
    @patch("audit_core.cli.run_relay_preflight")
    @patch("audit_core.cli.load_config")
    def test_cli_stops_before_agents_and_returns_failure_log(self, config_mock, preflight_mock, orchestrator_mock):
        config_mock.return_value = AuditConfig("https://judge.example/v1", "judge-key", "judge", 0.2, 128, 10, ".")
        preflight_mock.return_value = {
            "passed": False,
            "reason": "network_unreachable",
            "status_code": 0,
            "message": "connection refused",
            "model": "claimed-model",
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

        self.assertEqual(exit_code, 3)
        orchestrator_mock.return_value.run.assert_not_called()
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("audit_aborted", stderr.getvalue())
        self.assertIn("relay_preflight_failed", stderr.getvalue())
        self.assertNotIn("secret-token", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
