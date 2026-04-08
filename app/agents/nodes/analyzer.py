"""
Analyzer Node - Analyze top lane champion changes impact
Simplified: no tool calls, direct LLM analysis to stay within 256MB RAM
"""
import json
import logging
import re

from agents.llm import analyzer_llm
from agents.state import WorkflowState
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


ANALYZER_PROMPT_TEMPLATE = """你是英雄联盟上单位置专业分析师。分析以下上单相关变更对游戏的影响。

## 变更内容

{changes_summary}

## 输出格式（纯JSON，不要其他文字）

{{
  "champion_analyses": [
    {{
      "champion": "英雄名称",
      "change_type": "buff/nerf/adjust",
      "gameplay_changes": {{
        "laning_phase": "对线期影响",
        "teamfight_role": "团战作用变化",
        "build_adjustment": "出装调整"
      }},
      "meta_impact": {{
        "tier_prediction": "S/A/B/C/D",
        "tier_change": "从X到Y",
        "counter_changes": ["对抗变化"],
        "synergy_items": ["推荐装备"]
      }},
      "overall_assessment": {{
        "strength_score": 7,
        "worth_practicing": true,
        "win_rate_trend": "上升/下降/持平",
        "reasoning": "分析理由"
      }}
    }}
  ],
  "meta_overview": {{
    "top_tier_champions": ["S tier英雄"],
    "rising_picks": ["崛起英雄"],
    "falling_picks": ["削弱英雄"],
    "meta_shift_summary": "meta变化总结"
  }}
}}
"""


async def analyzer_node(state: WorkflowState) -> WorkflowState:
    """Analyzer Node: direct LLM analysis, no tool calls."""
    logger.info("=" * 60)
    logger.info("Node: Analyzer - 开始分析上单变更影响")
    logger.info("=" * 60)

    # Free raw_content to reduce memory
    state = {**state, "raw_content": ""}

    try:
        top_lane_changes = state.get("top_lane_changes", [])

        if not top_lane_changes:
            logger.warning("没有上单相关变更，跳过分析")
            metadata = state.get("metadata") or {}
            metadata["analyzer_skipped"] = True
            return {**state, "impact_analyses": [], "metadata": metadata}

        logger.info(f"收到 {len(top_lane_changes)} 个上单相关变更")

        changes_summary = _format_changes_summary(top_lane_changes)

        system_msg = SystemMessage(content="You are a League of Legends top lane expert analyst.")
        prompt = ANALYZER_PROMPT_TEMPLATE.format(changes_summary=changes_summary)
        user_msg = HumanMessage(content=prompt)
        messages = [system_msg, user_msg]

        model = analyzer_llm(temperature=0.7, bind_tools=False)

        logger.info("调用 LLM 进行影响分析...")
        response = await model.ainvoke(messages)
        logger.info("LLM 响应成功")

        # Parse response
        response_content = response.content
        if not isinstance(response_content, str):
            response_content = str(response_content)

        try:
            data = json.loads(response_content)
        except json.JSONDecodeError:
            logger.warning("响应不是纯 JSON，尝试提取...")
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("无法提取 JSON 分析结果")

        champion_analyses = data.get("champion_analyses", [])
        meta_overview = data.get("meta_overview", {})

        logger.info(f"✅ Analyzer 完成: 分析了 {len(champion_analyses)} 个英雄")

        metadata = state.get("metadata") or {}
        if hasattr(response, "response_metadata") and response.response_metadata:
            usage = response.response_metadata.get("token_usage", {})
            if usage:
                metadata["analyzer_tokens"] = usage
                logger.info(
                    f"Token 使用: 输入={usage.get('prompt_tokens', 0)}, "
                    f"输出={usage.get('completion_tokens', 0)}"
                )

        impact_analyses_list = [{
            "champion_analyses": champion_analyses,
            "meta_overview": meta_overview,
            "analysis_timestamp": state.get("version", "unknown"),
        }]

        return {
            **state,
            "impact_analyses": impact_analyses_list,
            "messages": [],  # Clear messages to save memory
            "metadata": metadata,
        }

    except Exception as e:
        logger.error(f"❌ Analyzer 失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {**state, "error": f"Analyzer 失败: {str(e)}", "impact_analyses": []}


def _format_changes_summary(top_lane_changes: list) -> str:
    """Format changes for LLM analysis."""
    lines = []

    champions = [c for c in top_lane_changes if c.get("type") == "champion"]
    if champions:
        lines.append("### 英雄变更\n")
        for i, change in enumerate(champions, 1):
            champion = change.get("champion", "未知英雄")
            change_type = change.get("change_type", "adjust")
            details = change.get("details", {})
            lines.append(f"{i}. **{champion}** ({change_type})")
            for key, value in details.items():
                lines.append(f"   - {key}: {value}")
            lines.append("")

    items = [c for c in top_lane_changes if c.get("type") == "item"]
    if items:
        lines.append("### 装备变更\n")
        for i, item_change in enumerate(items, 1):
            lines.append(f"{i}. **{item_change.get('item', '未知')}**: {item_change.get('change', '')}")
        lines.append("")

    systems = [c for c in top_lane_changes if c.get("type") == "system"]
    if systems:
        lines.append("### 系统变更\n")
        for i, sys_change in enumerate(systems, 1):
            lines.append(f"{i}. **{sys_change.get('category', '未知')}**: {sys_change.get('change', '')}")
        lines.append("")

    return "\n".join(lines)
