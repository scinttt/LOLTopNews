"""
LOL Top Lane Guide - Summarizer Node
聚合 Analyzer 的分析结果，生成前端可用的完整报告
"""
import json
import logging
from typing import Dict, List
from langchain_core.messages import HumanMessage

from agents.state import WorkflowState
from agents.llm import summarizer_llm

logger = logging.getLogger(__name__)


async def summarizer_node(state: WorkflowState) -> WorkflowState:
    """
    Summarizer Node: 分2步生成完整报告

    ⚠️ REVISED: 不再从头生成，而是聚合Analyzer的输出
    """
    logger.info("=" * 60)
    logger.info("Node: Summarizer - 开始生成总结报告")
    logger.info("=" * 60)

    try:
        # 1. 提取输入数据
        top_lane_changes = state.get("top_lane_changes", [])
        impact_analyses = state.get("impact_analyses", [])
        version = state.get("version", "unknown")

        # 2. 验证Analyzer输出
        if not impact_analyses or len(impact_analyses) == 0:
            logger.error("❌ Analyzer未返回分析结果")
            return {
                **state,
                "error": "Analyzer未返回分析结果，无法生成Summary"
            }

        # 提取champion_analyses
        champion_analyses = impact_analyses[0].get("champion_analyses", [])
        analyzer_meta_overview = impact_analyses[0].get("meta_overview", {})

        # 3. 特殊情况处理: 无上单变更
        if not champion_analyses or len(champion_analyses) == 0:
            logger.warning("本版本无上单英雄变更，生成meta维持分析")
            return {
                **state,
                "summary_report": {
                    "version_info": {"version": version, "total_changes": 0},
                    "meta_maintained": True,
                    "message": "本版本无上单英雄变更，meta环境保持稳定"
                }
            }

        # 4. Step 1: 聚合Tier List + Meta生态分析
        logger.info("Step 1: 聚合Tier List + Meta生态分析...")
        tier_and_meta_result = await _aggregate_tier_list_and_meta(
            champion_analyses,
            analyzer_meta_overview
        )

        # 5. Step 2: 增强出装推荐 + 生成Counter Matrix
        logger.info("Step 2: 增强出装推荐 + 生成Counter Matrix...")
        builds_and_counters_result = await _enhance_builds_and_counters(
            champion_analyses,
            tier_and_meta_result["tier_list"],
            top_lane_changes
        )

        # 6. 整合最终报告
        summary_report = {
            "version_info": {
                "version": version,
                "total_changes": len(top_lane_changes),
                "champion_changes": len(champion_analyses)
            },
            **tier_and_meta_result,           # tier_list, meta_ecosystem, executive_summary
            **builds_and_counters_result      # champion_details, counter_matrix, key_highlights
        }

        # 7. 记录Token使用
        metadata = state.get("metadata", {})
        metadata["summarizer_tokens"] = {
            "step1": tier_and_meta_result.get("tokens", {}),
            "step2": builds_and_counters_result.get("tokens", {})
        }

        logger.info("✅ Summarizer 完成 (2步)")

        return {
            **state,
            "summary_report": summary_report,
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"❌ Summarizer 失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "error": f"Summarizer 失败: {str(e)}"
        }


# ========== Helper Functions ==========

async def _aggregate_tier_list_and_meta(
    champion_analyses: List[Dict],
    analyzer_meta_overview: Dict
) -> Dict:
    """
    Step 1: 聚合Tier List + Meta生态分析

    ⚠️ 不是从头生成，而是聚合Analyzer已有的tier_prediction
    """
    prompt = STEP1_AGGREGATE_TIER_LIST_PROMPT.format(
        champion_analyses=json.dumps(champion_analyses, ensure_ascii=False, indent=2),
        analyzer_meta_overview=json.dumps(analyzer_meta_overview, ensure_ascii=False, indent=2)
    )

    llm = summarizer_llm(temperature=0.4)
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    try:
        # 解析JSON
        result = json.loads(response.content)
        result["tokens"] = response.response_metadata.get("token_usage", {})
        return result
    except json.JSONDecodeError as e:
        logger.error(f"LLM did not return valid JSON despite JSON mode. Response content:\n{response.content}")
        raise ValueError(f"Failed to decode JSON from LLM response in _aggregate_tier_list_and_meta: {e}")


async def _enhance_builds_and_counters(
    champion_analyses: List[Dict],
    tier_list: Dict,
    top_lane_changes: List[Dict]
) -> Dict:
    """
    Step 2: 增强出装推荐 + 生成Counter Matrix

    ⚠️ 基于Analyzer的synergy_items生成完整出装，基于counter_changes生成矩阵
    """
    prompt = STEP2_ENHANCE_BUILDS_AND_COUNTERS_PROMPT.format(
        champion_analyses=json.dumps(champion_analyses, ensure_ascii=False, indent=2),
        tier_list=json.dumps(tier_list, ensure_ascii=False, indent=2),
        top_lane_changes=json.dumps(top_lane_changes, ensure_ascii=False, indent=2)
    )

    llm = summarizer_llm(temperature=0.5)  # 适中创造性（出装+克制）
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    try:
        result = json.loads(response.content)
        result["tokens"] = response.response_metadata.get("token_usage", {})
        return result
    except json.JSONDecodeError as e:
        logger.error(f"LLM did not return valid JSON. Response content:\n{response.content}")
        raise ValueError(f"Failed to decode JSON from LLM response in _enhance_builds_and_counters: {e}")


# ========== Prompt Templates ==========

STEP1_AGGREGATE_TIER_LIST_PROMPT = """
你是一位资深的英雄联盟上单位置专家。

任务：基于Analyzer已经提供的per-champion分析，聚合生成Tier List和Meta生态分析。

输入数据（来自Analyzer）:
{champion_analyses}

Analyzer的meta_overview:
{analyzer_meta_overview}

注意：每个champion已经包含：
- tier_prediction: Analyzer预测的tier (S/A/B/C/D)
- strength_score: 强度评分 (1-10)
- counter_changes: 本版本克制关系变化
- synergy_items: 推荐装备
- gameplay_changes: 对线/团战/出装变化

输出JSON格式:
{{
  "tier_list": {{
    "S": [
      {{
        "champion": "蒙多医生",
        "tier": "S",
        "reason": "基础生命值和生命回复大幅提升，对线期几乎无解",
        "change_type": "buff",
        "strength_score": 9,
        "tags": ["坦克", "续航", "抗压"]
      }}
    ],
    "A": [...],
    "B": [...],
    "C": [...],
    "D": [...]
  }},

  "meta_ecosystem": {{
    "dominant_archetypes": [
      {{
        "type": "坦克",
        "champions": ["蒙多医生"],
        "reason": "坦克英雄生命值增强，对线续航能力提升"
      }}
    ],
    "declining_archetypes": [
      {{
        "type": "脆皮战士",
        "champions": ["内瑟斯"],
        "reason": "Q技能CD增加削弱叠Q效率"
      }}
    ],
    "playstyle_trends": [
      "坦克英雄回归meta，抗压流玩法受益",
      "脆皮战士削弱，激进对线风险增加"
    ]
  }},

  "executive_summary": "本版本坦克英雄回归，蒙多医生成为T0级抗压上单，内瑟斯遭遇削弱不推荐使用。"
}}

Tier聚合规则:
1. **优先使用Analyzer的tier_prediction**（已经过深度分析）
2. 微调：如果strength_score和tier_prediction不一致，以strength_score为准
   - S层: strength_score >= 8
   - A层: score 6-7
   - B层: score 4-5
   - C层: score 2-3
   - D层: score <= 1
3. 为每个英雄添加tags（从gameplay_changes推断，如"坦克", "战士", "单带", "团战"等）
4. 合并Analyzer的meta_overview，生成更全面的meta_ecosystem

只返回JSON，不要其他文字。
"""


STEP2_ENHANCE_BUILDS_AND_COUNTERS_PROMPT = """
你是英雄联盟上单专家，精通出装和对线克制。

任务1: 为每个英雄生成2-3套完整出装方案（基于Analyzer的synergy_items）
任务2: 生成克制关系矩阵（基于Analyzer的counter_changes）

输入数据:
{champion_analyses}  # Analyzer已提供的分析
{tier_list}          # Step 1生成的tier_list
{top_lane_changes}   # Extractor提取的原始变更（用于key_highlights）

输出JSON:
{{
  "champion_details": [
    {{
      "champion": "蒙多医生",
      "tier": "S",
      "change_summary": "基础生命值↑, 生命回复↑",

      "gameplay_impact": {{
        "laning_phase": "基础生命值增加使得蒙多在对线期...",  # 直接复用Analyzer的
        "teamfight_role": "生命回复提升使得蒙多在团战中...",
        "build_adjustment": "可以更早出日炎..."
      }},

      "recommended_builds": [
        {{
          "name": "标准坦克流",
          "core_items": ["日炎圣盾", "振奋铠甲", "荆棘之甲"],
          "boots": "水银之靴",
          "situational": ["兰顿之兆", "石像鬼石板甲"],
          "reason": "基于生命值增强，最大化坦度和续航，日炎配合被动清兵快",
          "适用场景": "对阵物理输出为主阵容",
          "runes": "不灭之握"
        }},
        {{
          "name": "法坦流",
          "core_items": ["日炎圣盾", "深渊面具", "振奋铠甲"],
          "boots": "法穿鞋",
          "situational": ["亡者的板甲", "兰德里的折磨"],
          "reason": "E技能AP加成，深渊提供魔抗+法伤双重收益",
          "适用场景": "对阵法系英雄或需要额外输出时",
          "runes": "不灭之握"
        }}
      ]
    }}
  ],

  "counter_matrix": {{
    "蒙多医生": {{
      "counters": [
        {{"champion": "塞恩", "reason": "生命值优势可以压制塞恩的坦度"}},
        {{"champion": "鳄鱼", "reason": "续航能力可以抵消鳄鱼的爆发"}}
      ],
      "countered_by": [
        {{"champion": "瓦洛兰之盾", "reason": "重伤效果严重削弱回复能力"}},
        {{"champion": "剑姬", "reason": "百分比真伤无视生命值优势"}}
      ],
      "changes_this_patch": [
        "对近战战士优势扩大（生命值↑）",  # 直接引用Analyzer的counter_changes
        "对重伤英雄仍然疲软"
      ]
    }}
  }},

  "key_highlights": [
    {{
      "type": "champion_buff",
      "champion": "蒙多医生",
      "summary": "生命值+回复双提升，坦度显著增强",
      "impact_level": "high"
    }},
    {{
      "type": "champion_nerf",
      "champion": "内瑟斯",
      "summary": "Q技能CD↑，叠Q效率下降",
      "impact_level": "medium"
    }}
  ]
}}

要求:
1. **复用Analyzer的gameplay_changes**（不要重新生成，直接使用）
2. **基于synergy_items生成2-3套完整出装**:
   - 每套有明确的name, core_items, boots, situational
   - 每套有详细reason（为什么这样出，配合本版本变更）
   - 每套有适用场景（对阵什么阵容）
   - 每套有符文推荐
3. **基于counter_changes生成counter_matrix**:
   - counters: 该英雄克制谁（基于本版本变更）
   - countered_by: 谁克制该英雄
   - changes_this_patch: 直接引用Analyzer的counter_changes
4. **生成key_highlights**（核心变更摘要，用于前端快速浏览）

只返回JSON，不要其他文字。
"""
