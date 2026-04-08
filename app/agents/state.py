from typing import Any, Dict, List, Optional, TypedDict

# ==================== 状态定义 ====================

class WorkflowState(TypedDict):
    """Main workflow state shared across all nodes."""
    # Input
    raw_content: str
    version: str

    # Extractor output
    top_lane_changes: Optional[List[Dict[str, Any]]]

    # Analyzer output
    impact_analyses: Optional[List[Dict[str, Any]]]

    # Summarizer output
    summary_report: Optional[Dict[str, Any]]

    # Messages — plain list, no add_messages reducer (saves memory)
    messages: list

    # Common
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]
    tool_call_count: int
