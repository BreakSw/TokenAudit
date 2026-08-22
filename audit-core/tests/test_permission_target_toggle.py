import unittest
from unittest.mock import patch

from audit_core.agents.permission_agent import PermissionAgent, PermissionInput
from audit_core.config import AuditConfig


def _token_response(model: str, status_code: int = 200):
    return {
        "status_code": status_code,
        "elapsed_ms": 12,
        "response": {"choices": [{"message": {"content": model}}]},
        "ok": status_code == 200,
        "endpoint": "chat_completions",
        "url": "https://relay.example/v1/chat/completions",
    }


def _judge_response():
    return {
        "status_code": 200,
        "elapsed_ms": 8,
        "response": {
            "choices": [{"message": {"content": '{"conclusion":"权限正常","evidence":"ok"}'}}]
        },
        "ok": True,
    }


class PermissionTargetToggleTest(unittest.TestCase):
    def setUp(self):
        self.config = AuditConfig("https://judge.example/v1", "judge-key", "judge", 0.2, 128, 10, ".")

    @patch("audit_core.agents.permission_agent.deepseek_chat", return_value=_judge_response())
    @patch("audit_core.agents.permission_agent.token_chat")
    def test_skips_target_model_call_when_disabled(self, token_chat_mock, _deepseek_mock):
        token_chat_mock.side_effect = [_token_response("claimed"), _token_response("anonymous", 401)]

        result = PermissionAgent().run(
            config=self.config,
            inp=PermissionInput("https://relay.example", "token", "claimed", ""),
        )

        self.assertEqual(token_chat_mock.call_count, 2)
        self.assertFalse(result["target_model_audit_enabled"])
        self.assertTrue(result["tests"][1]["skipped"])
        self.assertEqual(result["tests"][1]["skip_reason"], "target_model_audit_disabled")

    @patch("audit_core.agents.permission_agent.deepseek_chat", return_value=_judge_response())
    @patch("audit_core.agents.permission_agent.token_chat")
    def test_calls_target_model_when_enabled(self, token_chat_mock, _deepseek_mock):
        token_chat_mock.side_effect = [
            _token_response("claimed"),
            _token_response("target", 403),
            _token_response("anonymous", 401),
        ]

        result = PermissionAgent().run(
            config=self.config,
            inp=PermissionInput("https://relay.example", "token", "claimed", "target"),
        )

        self.assertEqual(token_chat_mock.call_count, 3)
        self.assertTrue(result["target_model_audit_enabled"])
        self.assertFalse(result["tests"][1]["skipped"])
        self.assertEqual(result["tests"][1]["model"], "target")


if __name__ == "__main__":
    unittest.main()
