import unittest
from unittest.mock import Mock, patch

from audit_core.scripts.token_api import _join_openai_path, token_chat


def _json_response(payload):
    response = Mock()
    response.status_code = 200
    response.headers = {"content-type": "application/json"}
    response.json.return_value = payload
    response.text = ""
    return response


class TokenApiRoutingTest(unittest.TestCase):
    def test_preserves_full_chat_endpoint_for_nonstandard_relay_paths(self):
        endpoint = "https://relay.example/custom/openai/chat/completions"
        self.assertEqual(endpoint, _join_openai_path(endpoint, "/chat/completions"))

    def test_replaces_explicit_endpoint_with_a_sibling_endpoint(self):
        endpoint = "https://relay.example/custom/openai/chat/completions"
        self.assertEqual(
            "https://relay.example/custom/openai/models",
            _join_openai_path(endpoint, "/models"),
        )

    @patch("audit_core.scripts.token_api.requests.post")
    def test_model_name_never_selects_a_vendor_specific_protocol(self, post_mock):
        post_mock.return_value = _json_response({"choices": [{"message": {"content": "OK"}}]})

        result = token_chat(
            base_url="https://relay.example/v1",
            token="test-token",
            model="gpt-5.4",
            messages=[{"role": "user", "content": "hello"}],
        )

        self.assertTrue(result["ok"])
        self.assertEqual(post_mock.call_count, 1)
        self.assertEqual(post_mock.call_args.args[0], "https://relay.example/v1/chat/completions")

    @patch("audit_core.scripts.token_api.requests.post")
    def test_explicit_responses_endpoint_selects_responses_protocol(self, post_mock):
        post_mock.return_value = _json_response({"output": [{"type": "message"}]})

        result = token_chat(
            base_url="https://relay.example/custom/responses",
            token="test-token",
            model="vendor/model-any-name",
            messages=[{"role": "user", "content": "hello"}],
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["endpoint"], "responses")
        self.assertEqual(post_mock.call_args.args[0], "https://relay.example/custom/responses")
        self.assertEqual(post_mock.call_args.kwargs["json"]["model"], "vendor/model-any-name")


if __name__ == "__main__":
    unittest.main()
