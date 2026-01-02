from typing import TypedDict, Optional, Dict, List, Any, Annotated

from langgraph.graph.message import add_messages


# ==================== 状态定义 ====================

class WorkflowState(TypedDict):
    """主工作流的状态 - 所有 Node 共享"""
    # 输入
    raw_content: str                                    # 爬取的原始内容
    version: str                                        # 版本号

    # Extractor 输出
    top_lane_changes: Optional[List[Dict[str, Any]]]   # 上单相关变更

    # Analyzer 输出 (Day 4-5 实现)
    impact_analyses: Optional[List[Dict[str, Any]]]    # 影响分析

    # Summarizer 输出 (Day 8 实现)
    summary_report: Optional[Dict[str, Any]]           # 总结报告

    # LangGraph 消息历史
    messages: Annotated[list, add_messages]

    # 通用
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]                 # Token 使用等元数据
    tool_call_count: int                               # 工具调用计数器（防止无限循环）
