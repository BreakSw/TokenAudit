from __future__ import annotations

import unittest

from audit_core.scripts.langgraph_schedule import run_langgraph


class LangGraphScheduleTest(unittest.TestCase):
    def test_preserves_each_node_result_in_graph_state(self) -> None:
        result = run_langgraph(
            nodes={
                "validity": lambda _: {"validity": {"conclusion": "有效"}},
                "security": lambda state: {
                    "security": {
                        "conclusion": "安全",
                        "saw_validity": "validity" in state,
                    }
                },
            },
            edges=[("validity", "security")],
            start="validity",
        )

        self.assertEqual(result["validity"]["conclusion"], "有效")
        self.assertEqual(result["security"]["conclusion"], "安全")
        self.assertTrue(result["security"]["saw_validity"])


if __name__ == "__main__":
    unittest.main()
