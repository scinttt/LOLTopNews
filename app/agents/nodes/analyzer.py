"""
Analyzer Node - 分析上单英雄变更的影响
支持使用 WebSearch 工具获取社区分析和meta信息
"""
import json
import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import WorkflowState
from agents.llm import analyzer_llm

logger = logging.getLogger(__name__)


ANALYZER_PROMPT_TEMPLATE = """你是英雄联盟上单位置专业分析师，精通版本变化对上路meta的影响。

你的任务是深度分析以下上单相关变更对游戏的影响。

## 本版本上单相关变更

{changes_summary}

## 分析要求

请为每个英雄变更提供深度分析，包括：

1. **玩法变化**
   - 技能/属性变更如何影响对线期打法
   - 团战定位和作用是否改变
   - 出装思路是否需要调整

2. **上路生态影响**
   - 该英雄在当前meta中的定位变化（S/A/B/C/D tier）
   - 与其他主流上单的对抗关系变化
   - 是否会导致新的counter关系出现

3. **综合评估**
   - 变更强度评分（1-10分，5分为中性）
   - 是否值得在新版本优先练习
   - 预测该英雄在rank中的胜率/出场率趋势

## 重要提示

如果你需要以下信息来做出更准确的分析，请使用 websearch 工具搜索：
- 该英雄在新版本的社区评价和实战数据
- 其他上单英雄在新版本的表现（用于对比）
- 该版本上路meta的整体趋势分析
- 专业选手或高分玩家对该变更的看法

搜索示例：
- "剑姬 15.24版本 上单 强度分析"
- "15.24版本 上单tier排行"
- "诺手 新版本 对线技巧"

## 输出格式

请以 JSON 格式返回分析结果（只返回JSON，不要其他文字）:

{{
  "champion_analyses": [
    {{
      "champion": "英雄名称",
      "change_type": "buff/nerf/adjust",
      "gameplay_changes": {{
        "laning_phase": "对线期影响描述",
        "teamfight_role": "团战作用变化",
        "build_adjustment": "出装思路调整"
      }},
      "meta_impact": {{
        "tier_prediction": "S/A/B/C/D",
        "tier_change": "从X tier到Y tier",
        "counter_changes": ["增强对抗XX", "削弱对抗YY"],
        "synergy_items": ["推荐装备1", "推荐装备2"]
      }},
      "overall_assessment": {{
        "strength_score": 7,
        "worth_practicing": true,
        "win_rate_trend": "预计上升/下降/持平",
        "reasoning": "综合分析理由"
      }}
    }}
  ],
  "meta_overview": {{
    "top_tier_champions": ["S tier英雄1", "S tier英雄2"],
    "rising_picks": ["崛起的英雄"],
    "falling_picks": ["削弱的英雄"],
    "meta_shift_summary": "本版本上路meta变化总结"
  }}
}}
"""


async def analyzer_node(state: WorkflowState) -> WorkflowState:
    """
    Analyzer Node: 分析上单变更的影响

    功能：
    1. 接收 extractor 提取的上单相关变更
    2. 使用 LLM 深度分析每个英雄的玩法变化和meta影响
    3. 可选使用 WebSearch 获取社区分析和实战数据
    4. 输出结构化的影响分析报告
    """
    logger.info("=" * 60)
    logger.info("Node: Analyzer - 开始分析上单变更影响")
    logger.info("=" * 60)

    try:
        # 1. 获取 extractor 的输出
        top_lane_changes = state.get("top_lane_changes", [])

        if not top_lane_changes:
            logger.warning("没有上单相关变更，跳过分析")
            current_metadata = state.get("metadata", {})
            if current_metadata is None:
                current_metadata = {}
            current_metadata["analyzer_skipped"] = True

            return {
                **state,
                "impact_analyses": [],
                "metadata": current_metadata
            }

        logger.info(f"收到 {len(top_lane_changes)} 个上单相关变更")

        # 2. 准备变更摘要
        changes_summary = _format_changes_summary(top_lane_changes)

        # 3. 获取或创建消息列表
        messages = state.get("messages", [])

        # 检查是否是第一次调用（从 extractor 过来）
        # 如果 messages 中没有 analyzer 相关的内容，说明是第一次
        is_first_call = not any("上单位置专业分析师" in str(msg.content) for msg in messages if hasattr(msg, 'content'))

        if is_first_call:
            # 第一次调用：初始化 analyzer 的消息
            logger.info("首次进入 Analyzer，初始化分析流程")

            system_msg = SystemMessage(content="""You are a League of Legends top lane expert analyst.

Your task is to analyze the impact of champion changes on top lane meta.

If you need more information about:
- Community reactions and win rate data
- Current meta trends
- Pro player opinions
- Champion matchup changes

Use the websearch tool to find relevant analysis and data.

Search examples:
- "剑姬 15.24版本 上单 强度"
- "15.24版本 上路meta分析"
- "诺手 新版本 胜率"
""")

            prompt = ANALYZER_PROMPT_TEMPLATE.format(changes_summary=changes_summary)
            user_msg = HumanMessage(content=prompt)
            messages = [system_msg, user_msg]

        # 4. 调用 LLM（绑定工具，允许搜索）
        # 检查是否接近工具调用上限
        MAX_TOOL_CALLS = 10  # 与 workflow.py 中的值保持一致
        tool_call_count = state.get("tool_call_count", 0)
        approaching_limit = tool_call_count >= MAX_TOOL_CALLS - 1  # 最后一次机会

        if approaching_limit:
            # 接近上限，不绑定工具，强制 LLM 给出最终分析
            logger.warning(f"⚠️ 工具调用次数接近上限 ({tool_call_count}/{MAX_TOOL_CALLS})，强制 LLM 完成分析")
            model = analyzer_llm(temperature=0.7, bind_tools=False)

            # 添加强制 JSON 输出的提示
            force_json_msg = HumanMessage(content="""请基于以上信息和之前搜索的结果，立即给出最终分析报告。

**重要**: 你的回复必须是纯 JSON 格式，不要包含任何解释文字、markdown 代码块或其他内容。直接输出 JSON 对象即可。

请按照之前要求的格式输出完整的分析结果。""")
            messages = messages + [force_json_msg]
        else:
            # 正常情况，允许调用工具
            model = analyzer_llm(temperature=0.7, bind_tools=True)

        logger.info("调用 LLM 进行影响分析...")
        response = await model.ainvoke(messages)
        logger.info("LLM 响应成功")

        # 5. 检查是否需要调用工具
        if response.tool_calls:
            logger.info(f"🔍 Analyzer 请求调用工具: {len(response.tool_calls)} 次")
            for tool_call in response.tool_calls:
                logger.info(f"   - {tool_call['name']}: {tool_call['args']}")

            # 更新工具调用计数
            tool_call_count = state.get("tool_call_count", 0) + 1

            # 返回状态，让 should_continue 决定下一步
            return {
                **state,
                "messages": messages + [response],
                "tool_call_count": tool_call_count,
                "metadata": state.get("metadata", {})
            }

        # 6. 没有工具调用，解析分析结果
        response_content = response.content

        # 确保 response_content 是字符串
        if isinstance(response_content, list):
            response_content = str(response_content)
        elif not isinstance(response_content, str):
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

        # 7. 提取分析结果
        champion_analyses = data.get("champion_analyses", [])
        meta_overview = data.get("meta_overview", {})

        logger.info(f"✅ Analyzer 完成: 分析了 {len(champion_analyses)} 个英雄")

        # 8. 记录 token 使用
        metadata = state.get("metadata", {})
        if metadata is None:
            metadata = {}
        if hasattr(response, "response_metadata") and response.response_metadata:
            usage = response.response_metadata.get("token_usage", {})
            if usage:
                metadata["analyzer_tokens"] = usage
                logger.info(
                    f"Token 使用: 输入={usage.get('prompt_tokens', 0)}, "
                    f"输出={usage.get('completion_tokens', 0)}"
                )

        # 9. 构建影响分析结果 - 保持为列表以匹配 state 类型
        impact_analyses_list = [{
            "champion_analyses": champion_analyses,
            "meta_overview": meta_overview,
            "analysis_timestamp": state.get("version", "unknown")
        }]
        
        logger.info(f"✅ Analyzer 完成: {impact_analyses_list}")

        return {
            **state,
            "impact_analyses": impact_analyses_list,
            "messages": messages + [response],
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"❌ Analyzer 失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "error": f"Analyzer 失败: {str(e)}",
            "impact_analyses": []
        }


def _format_changes_summary(top_lane_changes: list) -> str:
    """格式化变更摘要供 LLM 分析"""
    lines = []

    # 英雄变更
    champions = [c for c in top_lane_changes if c.get("type") == "champion"]
    if champions:
        lines.append("### 英雄变更\n")
        for i, change in enumerate(champions, 1):
            champion = change.get("champion", "未知英雄")
            change_type = change.get("change_type", "adjust")
            details = change.get("details", {})

            lines.append(f"{i}. **{champion}** ({change_type})")
            if details:
                for key, value in details.items():
                    lines.append(f"   - {key}: {value}")
            lines.append("")

    # 装备变更
    items = [c for c in top_lane_changes if c.get("type") == "item"]
    if items:
        lines.append("### 装备变更\n")
        for i, item_change in enumerate(items, 1):
            item_name = item_change.get("item", "未知装备")
            change = item_change.get("change", "")
            lines.append(f"{i}. **{item_name}**: {change}")
        lines.append("")

    # 系统变更
    systems = [c for c in top_lane_changes if c.get("type") == "system"]
    if systems:
        lines.append("### 系统变更\n")
        for i, sys in enumerate(systems, 1):
            category = sys.get("category", "未知系统")
            change = sys.get("change", "")
            lines.append(f"{i}. **{category}**: {change}")
        lines.append("")

    return "\n".join(lines)