import json
import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import WorkflowState
from agents.llm import create_llm

logger = logging.getLogger(__name__)

EXTRACTOR_PROMPT_TEMPLATE = """你是英雄联盟上单位置专家。从以下更新公告中提取**仅与上单位置相关的变更**。

关注点:
1. 上单常用英雄变更（剑姬、诺手、剑魔、刀妹、鳄鱼、青钢影、杰斯、亚索、克烈等）
2. 可以打上单的英雄变更（需判断变更是否影响上路）
3. 上单常用装备变更（黑切、日炎、三相、死舞、破败、斯特拉克等）
4. 上单相关符文变更（征服者、坚决系、余震、骸骨镀层等）
5. 上路机制变更（峡谷先锋、上路经验、防御塔等）

**忽略**: 中单、ADC、辅助、打野专属英雄和装备

**重要**: 如果公告内容不够详细，或者你需要了解某个英雄的具体机制，可以使用 websearch 工具搜索更多信息。

更新公告内容:
{content}

请按照以下 JSON 格式返回（只返回JSON，不要其他文字）:
{{
  "version": "版本号",
  "needs_more_info": false,
  "top_lane_changes": [
    {{
      "champion": "英雄名称",
      "type": "buff/nerf/adjust",
      "relevance": "primary/secondary",
      "details": {{
        "技能或属性": "变更描述"
      }}
    }}
  ],
  "item_changes": [
    {{
      "item": "装备名称",
      "change": "变更内容"
    }}
  ],
  "system_changes": [
    {{
      "category": "峡谷先锋/上路经验/防御塔等",
      "change": "变更内容"
    }}
  ]
}}
"""


async def extractor_node(state: WorkflowState) -> WorkflowState:
    """
    Extractor Node: 提取上单相关变更
    支持调用 WebSearch 工具获取额外信息
    """
    logger.info("=" * 60)
    logger.info("Node: Extractor - 开始提取上单相关变更")
    logger.info("=" * 60)

    try:
        # 1. 获取或创建消息列表
        messages = state.get("messages", [])

        # 如果messages为空，这是第一次调用，需要初始化
        if not messages:
            raw_content = state["raw_content"]
            content = raw_content[:10000]  # 限制长度

            system_msg = SystemMessage(content="""You are a League of Legends top lane expert analyst.
If the patch notes lack detail about a champion's abilities or mechanics, use the websearch tool to find more information.

Example: If you see "剑姬 Q技能调整" but no specifics, search for "剑姬 Q技能 破绽机制".""")

            prompt = EXTRACTOR_PROMPT_TEMPLATE.format(content=content)
            user_msg = HumanMessage(content=prompt)
            messages = [system_msg, user_msg]

        # 2. 调用 LLM
        model_with_tools = create_llm(temperature=0.3, bind_tools=False)

        logger.info("调用 LLM 提取...")
        response = await model_with_tools.ainvoke(messages)
        logger.info("LLM 响应成功")

        # 4. 解析 JSON
        response_content = response.content

        try:
            data = json.loads(response_content)
        except json.JSONDecodeError:
            logger.warning("响应不是纯 JSON，尝试提取...")
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("无法提取 JSON")

        # 5. 整合所有上单相关变更
        top_lane_changes = []

        # 英雄变更
        for change in data.get("top_lane_changes", []):
            top_lane_changes.append({
                "type": "champion",
                "champion": change.get("champion"),
                "change_type": change.get("type"),
                "relevance": change.get("relevance", "primary"),
                "details": change.get("details", {})
            })

        # 装备变更
        for item in data.get("item_changes", []):
            top_lane_changes.append({
                "type": "item",
                "item": item.get("item"),
                "change": item.get("change")
            })

        # 系统变更
        for system in data.get("system_changes", []):
            top_lane_changes.append({
                "type": "system",
                "category": system.get("category"),
                "change": system.get("change")
            })

        logger.info(f"✅ Extractor 完成: 提取到 {len(top_lane_changes)} 个上单相关变更")

        # 记录 token 使用
        metadata = state.get("metadata", {})
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("token_usage", {})
            metadata["extractor_tokens"] = usage
            logger.info(
                f"Token 使用: 输入={usage.get('prompt_tokens', 0)}, "
                f"输出={usage.get('completion_tokens', 0)}"
            )

        return {
            **state,
            "top_lane_changes": top_lane_changes,
            "version": data.get("version", state.get("version")),
            "messages": messages,
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"❌ Extractor 失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "error": f"Extractor 失败: {str(e)}"
        }
