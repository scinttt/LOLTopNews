"""
LOL Top Lane Guide - Main Workflow
Linear LangGraph pipeline: Extractor -> Analyzer -> Summarizer
"""
import logging
from typing import Any, Dict

from agents.nodes.analyzer import analyzer_node
from agents.nodes.extractor import extractor_node
from agents.nodes.summarizer import summarizer_node
from agents.state import WorkflowState
from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_initial_state(raw_content: str, version: str) -> WorkflowState:
    """Build a fresh workflow state for each execution."""
    return {
        "raw_content": raw_content,
        "version": version,
        "top_lane_changes": None,
        "impact_analyses": None,
        "summary_report": None,
        "messages": [],
        "error": None,
        "metadata": {},
        "tool_call_count": 0,
    }


def create_workflow():
    """
    Create a linear pipeline: extractor -> analyzer -> summarizer

    No tool call loop — keeps memory usage low for constrained containers.
    """
    workflow = StateGraph(WorkflowState)

    workflow.add_node("extractor", extractor_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("summarizer", summarizer_node)

    workflow.set_entry_point("extractor")
    workflow.add_edge("extractor", "analyzer")
    workflow.add_edge("analyzer", "summarizer")
    workflow.add_edge("summarizer", END)

    return workflow.compile()


async def run_workflow(raw_content: str, version: str = "unknown") -> Dict[str, Any]:
    """Run the full analysis pipeline."""
    graph = create_workflow()
    initial_state = build_initial_state(raw_content, version)
    result = await graph.ainvoke(initial_state)

    if result.get("error"):
        raise ValueError(result["error"])

    return result
