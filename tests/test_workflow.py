import os
import sys
import unittest
from unittest.mock import patch


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from agents import workflow  # noqa: E402


class _Message:
    def __init__(self, tool_calls=None):
        self.tool_calls = tool_calls


class _GraphStub:
    def __init__(self, result):
        self.result = result
        self.last_state = None

    async def ainvoke(self, state):
        self.last_state = state
        return self.result


class TestShouldContinue(unittest.TestCase):
    def test_routes_to_summarizer_when_tool_calls_reach_limit(self):
        state = {
            "messages": [_Message(tool_calls=[{"name": "websearch"}])],
            "tool_call_count": workflow.MAX_TOOL_CALLS,
        }
        self.assertEqual(workflow.should_continue(state), "summarizer")

    def test_routes_to_tools_when_last_message_has_tool_calls(self):
        state = {
            "messages": [_Message(tool_calls=[{"name": "websearch"}])],
            "tool_call_count": 1,
        }
        self.assertEqual(workflow.should_continue(state), "tools")

    def test_routes_to_summarizer_when_no_tool_calls(self):
        state = {
            "messages": [_Message(tool_calls=[])],
            "tool_call_count": 1,
        }
        self.assertEqual(workflow.should_continue(state), "summarizer")


class TestRunWorkflow(unittest.IsolatedAsyncioTestCase):
    async def test_run_workflow_returns_graph_result(self):
        expected = {"version": "14.24", "error": None}
        graph = _GraphStub(expected)

        with patch.object(workflow, "create_workflow", return_value=graph):
            result = await workflow.run_workflow("raw", version="14.24")

        self.assertEqual(result, expected)
        self.assertEqual(graph.last_state["raw_content"], "raw")
        self.assertEqual(graph.last_state["version"], "14.24")
        self.assertEqual(graph.last_state["messages"], [])
        self.assertEqual(graph.last_state["tool_call_count"], 0)

    async def test_run_workflow_raises_when_error_exists(self):
        graph = _GraphStub({"error": "analysis failed"})

        with patch.object(workflow, "create_workflow", return_value=graph):
            with self.assertRaises(ValueError) as ctx:
                await workflow.run_workflow("raw", version="14.24")

        self.assertEqual(str(ctx.exception), "analysis failed")


if __name__ == "__main__":
    unittest.main()
