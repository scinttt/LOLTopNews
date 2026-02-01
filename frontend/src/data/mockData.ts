export const mockData = {
  version: "25.24",
  totalChanges: 6,
  championChanges: [
    { name: "布隆", type: "buff", relevance: "冷门" },
    { name: "蒙多医生", type: "nerf", relevance: "主流" },
    { name: "沙漠死神 内瑟斯", type: "buff", relevance: "主流" },
    { name: "北地之怒 瑟庄妮", type: "buff", relevance: "冷门" },
    { name: "诺克萨斯统领 斯维因", type: "buff", relevance: "主流" },
    { name: "不落魔锋 亚恒", type: "nerf", relevance: "主流" },
  ],
  impactAnalysis: {
    champion_analyses: [
      {
        champion: "布隆",
        change_type: "buff",
        gameplay_changes: {
          laning_phase:
            "基础生命值增加20点，被动追加攻击伤害从30%提升到40%。对线期更耐打，配合被动打出的爆发更高，特别是配合打野gank时能造成更多伤害。",
          teamfight_role:
            "团战中作为前排坦克更硬，被动伤害提升让他在控制敌人后能造成更多输出，增强了对后排的威胁。",
          build_adjustment:
            "可以考虑更偏向攻击性的装备，如日炎、冰拳等，充分利用被动伤害提升。",
        },
        meta_impact: {
          tier_prediction: "C",
          tier_change: "从D tier到C tier",
          counter_changes: ["增强对抗近战战士", "对线期更安全"],
          synergy_items: ["日炎圣盾", "冰脉护手", "兰顿之兆"],
        },
        overall_assessment: {
          strength_score: 6,
          worth_practicing: false,
          win_rate_trend: "预计小幅上升",
          reasoning:
            "虽然增强明显，但布隆作为上单依然不是主流选择。生命值和被动伤害的提升让他在特定对局中更有竞争力，但整体上单生态中依然处于弱势。",
        },
      },
      {
        champion: "沙漠死神 内瑟斯",
        change_type: "buff",
        gameplay_changes: {
          laning_phase:
            "基础生命值增加19点，Q技能基础伤害全面提升5点。对线期更耐打，补刀更稳定，特别是前期Q技能伤害提升让补刀更容易，减少漏刀风险。",
          teamfight_role:
            "中期团战能力小幅提升，Q技能伤害增加让他在叠层后的爆发更高。",
          build_adjustment:
            "出装思路不变，依然以三相、破败、死舞为核心，但前期对线更舒服。",
        },
        meta_impact: {
          tier_prediction: "B",
          tier_change: "从C tier到B tier",
          counter_changes: ["增强对抗远程poke英雄", "前期抗压能力提升"],
          synergy_items: [
            "三相之力",
            "破败王者之刃",
            "斯特拉克的挑战护手",
          ],
        },
        overall_assessment: {
          strength_score: 7,
          worth_practicing: true,
          win_rate_trend: "预计明显上升",
          reasoning:
            "内瑟斯一直以来的问题是前期太弱，这次增强直接解决了两个核心痛点：生存能力和补刀稳定性。虽然增强幅度不大，但对狗头来说每一点前期增强都很关键。",
        },
      },
      {
        champion: "北地之怒 瑟庄妮",
        change_type: "buff",
        gameplay_changes: {
          laning_phase:
            "Q技能冷却时间减少1秒，法力消耗降低，所有技能AP加成大幅提升。对线期换血更频繁，AP猪妹玩法得到极大加强，可以打出更高爆发。",
          teamfight_role:
            "AP猪妹团战爆发极高，QWR连招可以秒杀脆皮。传统坦克猪妹控制更频繁，坦度略有提升。",
          build_adjustment:
            "AP猪妹成为可行选择，出装可以考虑卢登、暗夜收割者、巫妖等AP装备。传统出装依然强势。",
        },
        meta_impact: {
          tier_prediction: "A",
          tier_change: "从B tier到A tier",
          counter_changes: ["增强对抗脆皮英雄", "AP玩法克制坦克"],
          synergy_items: [
            "卢登的激荡",
            "暗夜收割者",
            "冰杖",
            "兰德里的苦楚",
          ],
        },
        overall_assessment: {
          strength_score: 8,
          worth_practicing: true,
          win_rate_trend: "预计大幅上升",
          reasoning:
            "这是瑟庄妮的重大加强，特别是AP玩法的可行性大幅提升。Q技能冷却和蓝耗的优化让对线期更舒服，AP加成的全面提升让猪妹有了全新的玩法维度。",
        },
      },
      {
        champion: "诺克萨斯统领 斯维因",
        change_type: "buff",
        gameplay_changes: {
          laning_phase:
            "被动每块碎片治疗固定为6%（原为3-6%基于等级）。前期回复能力大幅提升，对线换血更有优势，特别是配合E技能拉回敌人后的回复。",
          teamfight_role:
            "团战续航能力提升，大招期间通过被动回复更多生命值，站场能力更强。",
          build_adjustment:
            "可以考虑更偏向持续作战的装备，如时光杖、冰杖等，充分利用治疗提升。",
        },
        meta_impact: {
          tier_prediction: "B",
          tier_change: "从C tier到B tier",
          counter_changes: ["增强对抗持续伤害英雄", "对线续航能力大幅提升"],
          synergy_items: ["时光之杖", "瑞莱的冰晶节杖", "兰德里的苦楚"],
        },
        overall_assessment: {
          strength_score: 7,
          worth_practicing: true,
          win_rate_trend: "预计明显上升",
          reasoning:
            "斯维因的核心问题就是前期太弱，这次被动治疗的加强直接提升了前期对线能力。固定6%的治疗让他在1级就有不错的回复，对抗近战英雄时优势明显。",
        },
      },
      {
        champion: "不落魔锋 亚恒",
        change_type: "nerf",
        gameplay_changes: {
          laning_phase:
            "Q技能冷却时间增加1秒，E技能增效点伤害降低。对线期换血频率下降，爆发伤害降低，特别是E技能命中后的追击伤害减少。",
          teamfight_role:
            "团战切入频率降低，爆发伤害小幅下降，但机制依然强大。",
          build_adjustment:
            "可能需要更注重技能急速装备来弥补冷却增加，如黑切、死亡之舞等。",
        },
        meta_impact: {
          tier_prediction: "S",
          tier_change: "从S+ tier到S tier",
          counter_changes: ["削弱对抗高机动英雄", "对线压制力下降"],
          synergy_items: ["黑色切割者", "死亡之舞", "斯特拉克的挑战护手"],
        },
        overall_assessment: {
          strength_score: 4,
          worth_practicing: true,
          win_rate_trend: "预计小幅下降",
          reasoning:
            "虽然被削弱，但亚恒的基础机制依然强大。冷却时间的增加会影响他的技能循环，E技能伤害降低让他的爆发有所下降，但作为新英雄，他依然会是上单的强势选择。",
        },
      },
    ],
    meta_overview: {
      top_tier_champions: [
        "亚恒",
        "剑姬",
        "鳄鱼",
        "永恩",
        "赛恩",
        "波比",
      ],
      rising_picks: ["瑟庄妮(AP玩法)", "内瑟斯", "斯维因"],
      falling_picks: ["亚恒(小幅下降)"],
      meta_shift_summary:
        "15.24版本是S15最后一个版本，上路meta出现了一些有趣的变化：1) AP猪妹成为新的可玩选择，AP加成的全面提升让瑟庄妮有了爆发秒人的能力；2) 内瑟斯和斯维因的前期能力得到加强，让这些后期英雄对线期更舒服；3) 亚恒虽然被削弱但依然强势；4) 坦克英雄如布隆得到小幅增强。整体来看，版本偏向于让更多英雄有上场机会，为即将到来的新赛季做准备。",
    },
    analysis_timestamp: "25.24",
  },
  summaryReport: {
    version_info: { version: "25.24", total_changes: 6, champion_changes: 5 },
    tier_list: {
      S: [
        {
          champion: "亚恒",
          tier: "S",
          reason: "虽然被削弱，但基础机制依然强大，仍是上单强势选择",
          change_type: "nerf",
          strength_score: 4,
          tags: ["战士", "爆发", "机动"],
        },
      ],
      A: [
        {
          champion: "瑟庄妮",
          tier: "A",
          reason: "AP玩法的可行性大幅提升，团战爆发极高",
          change_type: "buff",
          strength_score: 8,
          tags: ["坦克", "AP", "团战"],
        },
      ],
      B: [
        {
          champion: "内瑟斯",
          tier: "B",
          reason: "前期能力得到加强，补刀更稳定",
          change_type: "buff",
          strength_score: 7,
          tags: ["战士", "后期", "单带"],
        },
        {
          champion: "斯维因",
          tier: "B",
          reason: "被动治疗提升，前期续航能力增强",
          change_type: "buff",
          strength_score: 7,
          tags: ["法师", "续航", "团战"],
        },
      ],
      C: [
        {
          champion: "布隆",
          tier: "C",
          reason:
            "生命值和被动伤害提升，但整体上单生态中依然处于弱势",
          change_type: "buff",
          strength_score: 6,
          tags: ["坦克", "控制", "团战"],
        },
      ],
      D: [],
    },
    meta_ecosystem: {
      dominant_archetypes: [
        {
          type: "坦克",
          champions: ["瑟庄妮"],
          reason: "坦克英雄生命值增强，对线续航能力提升",
        },
      ],
      declining_archetypes: [
        {
          type: "脆皮战士",
          champions: ["亚恒"],
          reason: "Q技能和E技能削弱导致对线压制力下降",
        },
      ],
      playstyle_trends: [
        "坦克英雄回归meta，抗压流玩法受益",
        "脆皮战士削弱，激进对线风险增加",
      ],
    },
    executive_summary:
      "本版本坦克英雄回归，瑟庄妮的AP玩法成为新的亮点，亚恒虽遭削弱但依然强势，内瑟斯和斯维因的前期能力增强使其在对线期更具竞争力。",
    tokens: {
      completion_tokens: 3294,
      prompt_tokens: 4002,
      total_tokens: 7296,
      completion_tokens_details: {
        accepted_prediction_tokens: 0,
        audio_tokens: 0,
        reasoning_tokens: 0,
        rejected_prediction_tokens: 0,
      },
      prompt_tokens_details: { audio_tokens: 0, cached_tokens: 0 },
    },
    champion_details: [
      {
        champion: "布隆",
        tier: "C",
        change_summary: "基础生命值和被动伤害提升",
        gameplay_impact: {
          laning_phase:
            "基础生命值增加20点，被动追加攻击伤害从30%提升到40%。对线期更耐打，配合被动打出的爆发更高，特别是配合打野gank时能造成更多伤害。",
          teamfight_role:
            "团战中作为前排坦克更硬，被动伤害提升让他在控制敌人后能造成更多输出，增强了对后排的威胁。",
          build_adjustment:
            "可以考虑更偏向攻击性的装备，如日炎、冰拳等，充分利用被动伤害提升。",
        },
        recommended_builds: [
          {
            name: "攻击性坦克",
            core_items: ["日炎圣盾", "冰脉护手", "兰顿之兆"],
            boots: "水银之靴",
            situational: ["亡者的板甲", "荆棘之甲"],
            reason:
              "利用被动伤害提升，增加输出能力，日炎和冰拳提供额外伤害和控制。",
            适用场景: "对阵物理输出为主的阵容",
            runes: "不灭之握",
          },
          {
            name: "标准坦克",
            core_items: ["日炎圣盾", "振奋铠甲", "荆棘之甲"],
            boots: "布甲靴",
            situational: ["石像鬼石板甲", "自然之力"],
            reason: "最大化坦度和续航能力，适合长时间团战。",
            适用场景: "对阵混合伤害阵容",
            runes: "不滅之握",
          },
        ],
      },
      {
        champion: "沙漠死神 内瑟斯",
        tier: "B",
        change_summary: "基础生命值和Q技能伤害提升",
        gameplay_impact: {
          laning_phase:
            "基础生命值增加19点，Q技能基础伤害全面提升5点。对线期更耐打，补刀更稳定，特别是前期Q技能伤害提升让补刀更容易，减少漏刀风险。",
          teamfight_role:
            "中期团战能力小幅提升，Q技能伤害增加让他在叠层后的爆发更高。",
          build_adjustment:
            "出装思路不变，依然以三相、破败、死舞为核心，但前期对线更舒服。",
        },
        recommended_builds: [
          {
            name: "三相破败流",
            core_items: ["三相之力", "破败王者之刃", "斯特拉克的挑战护手"],
            boots: "水银之靴",
            situational: ["振奋铠甲", "兰德里的苦楚"],
            reason: "提升输出和生存能力，适合打持久战。",
            适用场景: "对阵坦克和持续输出阵容",
            runes: "征服者",
          },
          {
            name: "坦克流",
            core_items: ["日炎圣盾", "振奋铠甲", "荆棘之甲"],
            boots: "布甲靴",
            situational: ["亡者的板甲", "自然之力"],
            reason: "最大化坦度，适合吸收伤害和打持久战。",
            适用场景: "对阵高爆发阵容",
            runes: "不滅之握",
          },
        ],
      },
      {
        champion: "北地之怒 瑟庄妮",
        tier: "A",
        change_summary: "AP加成提升，Q技能冷却和法力消耗降低",
        gameplay_impact: {
          laning_phase:
            "Q技能冷却时间减少1秒，法力消耗降低，所有技能AP加成大幅提升。对线期换血更频繁，AP猪妹玩法得到极大加强，可以打出更高爆发。",
          teamfight_role:
            "AP猪妹团战爆发极高，QWR连招可以秒杀脆皮。传统坦克猪妹控制更频繁，坦度略有提升。",
          build_adjustment:
            "AP猪妹成为可行选择，出装可以考虑卢登、暗夜收割者、巫妖等AP装备。传统出装依然强势。",
        },
        recommended_builds: [
          {
            name: "AP爆发流",
            core_items: ["卢登的激荡", "暗夜收割者", "巫妖之祸"],
            boots: "法穿鞋",
            situational: ["莫雷洛秘典", "灭世者的死亡之帽"],
            reason: "最大化技能伤害，适合秒杀脆皮。",
            适用场景: "对阵脆皮阵容",
            runes: "电刑",
          },
          {
            name: "坦克控制流",
            core_items: ["日炎圣盾", "振奋铠甲", "兰顿之兆"],
            boots: "水银之靴",
            situational: ["石像鬼石板甲", "自然之力"],
            reason: "提升坦度和控制能力，适合打持久战。",
            适用场景: "对阵混合伤害阵容",
            runes: "不滅之握",
          },
        ],
      },
      {
        champion: "诺克萨斯统领 斯维因",
        tier: "B",
        change_summary: "被动治疗提升",
        gameplay_impact: {
          laning_phase:
            "被动每块碎片治疗固定为6%（原为3-6%基于等级）。前期回复能力大幅提升，对线换血更有优势，特别是配合E技能拉回敌人后的回复。",
          teamfight_role:
            "团战续航能力提升，大招期间通过被动回复更多生命值，站场能力更强。",
          build_adjustment:
            "可以考虑更偏向持续作战的装备，如时光杖、冰杖等，充分利用治疗提升。",
        },
        recommended_builds: [
          {
            name: "持续输出流",
            core_items: ["时光之杖", "瑞莱的冰晶节杖", "兰德里的苦楚"],
            boots: "法穿鞋",
            situational: ["中娅沙漏", "灭世者的死亡之帽"],
            reason: "提升持续输出和控制能力，适合打持久战。",
            适用场景: "对阵持续输出阵容",
            runes: "征服者",
          },
          {
            name: "坦克法师流",
            core_items: ["日炎圣盾", "振奋铠甲", "自然之力"],
            boots: "水银之靴",
            situational: ["石像鬼石板甲", "荆棘之甲"],
            reason: "最大化坦度和续航能力，适合吸收伤害。",
            适用场景: "对阵高爆发阵容",
            runes: "不滅之握",
          },
        ],
      },
      {
        champion: "不落魔锋 亚恒",
        tier: "S",
        change_summary: "Q技能冷却增加，E技能伤害降低",
        gameplay_impact: {
          laning_phase:
            "Q技能冷却时间增加1秒，E技能增效点伤害降低。对线期换血频率下降，爆发伤害降低，特别是E技能命中后的追击伤害减少。",
          teamfight_role:
            "团战切入频率降低，爆发伤害小幅下降，但机制依然强大。",
          build_adjustment:
            "可能需要更注重技能急速装备来弥补冷却增加，如黑切、死亡之舞等。",
        },
        recommended_builds: [
          {
            name: "技能急速流",
            core_items: ["黑色切割者", "死亡之舞", "斯特拉克的挑战护手"],
            boots: "水银之靴",
            situational: ["振奋铠甲", "守护天使"],
            reason: "弥补技能冷却增加的问题，提升生存能力。",
            适用场景: "对阵高机动阵容",
            runes: "征服者",
          },
          {
            name: "爆发战士流",
            core_items: ["德拉克萨的暮刃", "幽梦之灵", "夜之锋刃"],
            boots: "法穿鞋",
            situational: ["赛瑞尔达的怨恨", "守护天使"],
            reason: "最大化爆发伤害，适合打脆皮。",
            适用场景: "对阵脆皮阵容",
            runes: "电刑",
          },
        ],
      },
    ],
    counter_matrix: {
      布隆: {
        counters: [
          { champion: "亚索", reason: "被动和控制技能可以限制亚索的灵活性" },
          { champion: "易大师", reason: "被动和控制技能可以限制易大师的输出" },
        ],
        countered_by: [
          { champion: "剑姬", reason: "剑姬的破绽可以无视布隆的防御" },
          { champion: "卡密尔", reason: "卡密尔的机动性可以绕过布隆的防御" },
        ],
        changes_this_patch: ["增强对抗近战战士", "对线期更安全"],
      },
      内瑟斯: {
        counters: [
          { champion: "提莫", reason: "内瑟斯的Q技能可以轻松击杀提莫" },
          { champion: "亚索", reason: "内瑟斯的Q技能可以轻松击杀亚索" },
        ],
        countered_by: [
          { champion: "奎因", reason: "奎因的机动性和远程攻击可以压制内瑟斯" },
          { champion: "凯尔", reason: "凯尔的远程攻击和后期能力可以压制内瑟斯" },
        ],
        changes_this_patch: ["增强对抗远程poke英雄", "前期抗压能力提升"],
      },
      瑟庄妮: {
        counters: [
          { champion: "卡莎", reason: "瑟庄妮的爆发可以轻松击杀卡莎" },
          { champion: "卢锡安", reason: "瑟庄妮的爆发可以轻松击杀卢锡安" },
        ],
        countered_by: [
          { champion: "剑姬", reason: "剑姬的机动性可以绕过瑟庄妮的控制" },
          { champion: "卡蜜尔", reason: "卡蜜尔的机动性可以绕过瑟庄妮的控制" },
        ],
        changes_this_patch: ["增强对抗脆皮英雄", "AP玩法克制坦克"],
      },
      斯维因: {
        counters: [
          { champion: "亚索", reason: "斯维因的控制和续航可以压制亚索" },
          { champion: "易大师", reason: "斯维因的控制和续航可以压制易大师" },
        ],
        countered_by: [
          { champion: "剑姬", reason: "剑姬的机动性和破绽可以无视斯维因的控制" },
          { champion: "卡蜜尔", reason: "卡蜜尔的机动性可以绕过斯维因的控制" },
        ],
        changes_this_patch: ["增强对抗持续伤害英雄", "对线续航能力大幅提升"],
      },
      亚恒: {
        counters: [
          { champion: "脆皮英雄", reason: "亚恒的爆发可以轻松击杀脆皮" },
          {
            champion: "低机动性英雄",
            reason: "亚恒的机动性可以轻松追击低机动性英雄",
          },
        ],
        countered_by: [
          { champion: "剑姬", reason: "剑姬的机动性和破绽可以无视亚恒的爆发" },
          { champion: "卡蜜尔", reason: "卡蜜尔的机动性可以绕过亚恒的爆发" },
        ],
        changes_this_patch: ["削弱对抗高机动英雄", "对线压制力下降"],
      },
    },
    key_highlights: [
      {
        type: "champion_buff",
        champion: "布隆",
        summary: "基础生命值和被动伤害提升，提升对线和团战能力",
        impact_level: "medium",
      },
      {
        type: "champion_buff",
        champion: "内瑟斯",
        summary: "基础生命值和Q技能伤害提升，增强前期对线能力",
        impact_level: "medium",
      },
      {
        type: "champion_buff",
        champion: "瑟庄妮",
        summary: "AP加成提升，Q技能冷却和法力消耗降低，提升AP玩法可行性",
        impact_level: "high",
      },
      {
        type: "champion_buff",
        champion: "斯维因",
        summary: "被动治疗提升，增强对线和团战续航能力",
        impact_level: "medium",
      },
      {
        type: "champion_nerf",
        champion: "亚恒",
        summary: "Q技能冷却增加，E技能伤害降低，削弱对线和团战爆发",
        impact_level: "medium",
      },
    ],
  },
};
