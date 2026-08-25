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

    def test_preserves_query_parameters_for_deployment_style_endpoints(self):
        endpoint = "https://relay.example/openai/deployments/demo/chat/completions?api-version=2026-01-01"
        self.assertEqual(
            "https://relay.example/openai/deployments/demo/models?api-version=2026-01-01",
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

    @patch("audit_core.scripts.token_api.requests.post")
    def test_falls_back_to_non_v1_chat_path_after_404(self, post_mock):
        missing = _json_response({"error": {"message": "not found"}})
        missing.status_code = 404
        post_mock.side_effect = [missing, _json_response({"choices": [{"message": {"content": "OK"}}]})]

        result = token_chat(
            base_url="https://relay.example/openai",
            token="test-token",
            model="model-x",
            messages=[{"role": "user", "content": "hello"}],
        )

        self.assertTrue(result["ok"])
        self.assertTrue(result["path_fallback_used"])
        self.assertEqual(post_mock.call_args_list[0].args[0], "https://relay.example/openai/v1/chat/completions")
        self.assertEqual(post_mock.call_args_list[1].args[0], "https://relay.example/openai/chat/completions")

    @patch("audit_core.scripts.token_api.requests.post")
    def test_decodes_chat_completion_sse_returned_by_compatible_relays(self, post_mock):
        response = Mock()
        response.status_code = 200
        response.headers = {"content-type": "text/event-stream"}
        response.json.side_effect = ValueError("not a single json response")
        response.text = (
            'data: {"choices":[{"delta":{"content":"Hel"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n'
            "data: [DONE]\n"
        )
        post_mock.return_value = response

        result = token_chat(
            base_url="https://relay.example/v1",
            token="test-token",
            model="model-x",
            messages=[{"role": "user", "content": "hello"}],
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["response"]["choices"][0]["message"]["content"], "Hello")

    @patch("audit_core.scripts.token_api.requests.post")
    def test_retries_reasoning_models_with_max_completion_tokens_when_required(self, post_mock):
        unsupported = _json_response({
            "error": {
                "message": "Unsupported parameter: max_tokens. Use max_completion_tokens instead."
            }
        })
        unsupported.status_code = 400
        post_mock.side_effect = [unsupported, _json_response({"choices": [{"message": {"content": "OK"}}]})]

        result = token_chat(
            base_url="https://relay.example/v1",
            token="test-token",
            model="reasoning-model",
            messages=[{"role": "user", "content": "hello"}],
            max_tokens=4096,
        )

        self.assertTrue(result["ok"])
        self.assertTrue(result["payload_fallback_used"])
        self.assertIn("max_tokens", post_mock.call_args_list[0].kwargs["json"])
        self.assertNotIn("max_tokens", post_mock.call_args_list[1].kwargs["json"])
        self.assertEqual(post_mock.call_args_list[1].kwargs["json"]["max_completion_tokens"], 4096)


if __name__ == "__main__":
    unittest.main()
