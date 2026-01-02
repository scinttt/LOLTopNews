"""
LOL Top Lane Guide - 主工作流
一个 LangGraph，包含 3 个 Node: Extractor, Analyzer, Summarizer
支持 WebSearch 工具调用
"""
import os
import logging
from typing import Dict, Any, Literal
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agents.state import WorkflowState
from agents.tools import websearch
from agents.nodes.extractor import extractor_node
from agents.nodes.analyzer import analyzer_node
from agents.nodes.summarizer import summarizer_node


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from agents.llm import create_llm


# ==================== Node 2: Tool Node ====================

# 使用 LangGraph 内置的 ToolNode
tools = [websearch]
tool_node = ToolNode(tools)


# ==================== 条件路由 ====================

def should_continue(state: WorkflowState) -> Literal["tools", "analyzer"]:
    """决定是否继续调用工具还是进入 Analyzer"""

    messages = state["messages"]
    last_message = messages[-1]

    # 检查工具调用次数（防止无限循环）
    MAX_TOOL_CALLS = 3
    tool_call_count = state.get("tool_call_count", 0)

    if tool_call_count >= MAX_TOOL_CALLS:
        logger.warning(f"⚠️ 已达到最大工具调用次数 ({MAX_TOOL_CALLS})，强制进入 analyzer")
        return "analyzer"

    # 如果最后一条消息包含工具调用，进入 tool_node
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        logger.info(f"→ 路由到: tools (LLM 请求调用工具，当前次数: {tool_call_count + 1}/{MAX_TOOL_CALLS})")
        return "tools"

    # 否则，进入 analyzer
    logger.info("→ 路由到: analyzer (无需调用工具)")
    return "analyzer"


# ==================== 创建工作流 ====================

def create_workflow() -> StateGraph:
    """
    创建主工作流 (一个 Graph, 包含工具调用循环)

    流程:
    START -> extractor -> analyzer -> [should_continue?]
                             |            |
                             v            v
                          tools -----> summarizer -> END
                             |
                             └──> (循环回 analyzer)
    """
    # 创建图
    workflow = StateGraph(WorkflowState)

    # 添加节点
    workflow.add_node("extractor", extractor_node)
    workflow.add_node("tools", tool_node)             # 工具调用节点
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("summarizer", summarizer_node)

    # 定义流程
    workflow.set_entry_point("extractor")

    # extractor 后直接进入 analyzer
    workflow.add_edge("extractor", "analyzer")

    # 正常流程
    workflow.add_edge("analyzer", "summarizer")
    workflow.add_edge("summarizer", END)

    # 编译
    return workflow.compile()


# ==================== 便捷函数 ====================

async def run_workflow(raw_content: str, version: str = "unknown") -> Dict[str, Any]:
    """
    运行完整工作流

    Args:
        raw_content: 原始公告内容
        version: 版本号

    Returns:
        Dict: 包含所有输出的结果
    """
    # 创建工作流
    graph = create_workflow()

    # 初始状态
    initial_state: WorkflowState = {
        "raw_content": raw_content,
        "version": version,
        "top_lane_changes": None,
        "impact_analyses": None,
        "summary_report": None,
        "messages": [],
        "error": None,
        "metadata": {},
        "tool_call_count": 0  # 初始化工具调用计数器
    }

    # 执行
    result = await graph.ainvoke(initial_state)

    # 检查错误
    if result.get("error"):
        raise ValueError(result["error"])

    return result
