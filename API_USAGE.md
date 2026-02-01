# LOL Top Lane Guide - API 使用文档

## 快速开始

### 1. 启动 API 服务器

```bash
# 方式 1: 使用启动脚本
./run_api.sh

# 方式 2: 直接使用 uvicorn
cd app && uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

服务器启动后，访问以下地址：
- **API 根路径**: http://localhost:8000
- **交互式文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## API 端点

### 1. GET /api/analyze

分析指定版本的更新公告（自动爬取）

**请求示例**:
```bash
# 分析最新版本
curl "http://localhost:8000/api/analyze?version=latest"

# 分析指定版本
curl "http://localhost:8000/api/analyze?version=14.24"
```

**参数**:
- `version` (可选): 版本号，默认为 `latest`

**响应示例**:
```json
{
  "version": "14.24",
  "top_lane_changes": [
    {
      "type": "champion",
      "champion": "剑姬",
      "change_type": "buff",
      "relevance": "primary",
      "details": {
        "Q技能": "冷却时间降低"
      }
    }
  ],
  "impact_analyses": [
    {
      "champion_analyses": [
        {
          "champion": "剑姬",
          "change_type": "buff",
          "gameplay_changes": {
            "laning_phase": "...",
            "teamfight_role": "...",
            "build_adjustment": "..."
          },
          "meta_impact": {
            "tier_prediction": "S",
            "tier_change": "从A tier到S tier",
            "counter_changes": ["增强对抗诺手"],
            "synergy_items": ["破败王者之刃", "三相之力"]
          },
          "overall_assessment": {
            "strength_score": 8,
            "worth_practicing": true,
            "win_rate_trend": "预计上升",
            "reasoning": "..."
          }
        }
      ],
      "meta_overview": {
        "top_tier_champions": ["剑姬", "青钢影"],
        "rising_picks": ["剑姬"],
        "falling_picks": ["诺手"],
        "meta_shift_summary": "..."
      }
    }
  ],
  "summary_report": null,
  "metadata": {
    "extractor_tokens": {
      "prompt_tokens": 1500,
      "completion_tokens": 500,
      "total_tokens": 2000
    },
    "analyzer_tokens": {
      "prompt_tokens": 2000,
      "completion_tokens": 800,
      "total_tokens": 2800
    }
  }
}
```

---

### 2. POST /api/analyze

分析指定版本的更新公告（可提供内容）

**请求示例**:
```bash
# 自动爬取内容
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "14.24"
  }'

# 提供内容（不爬取）
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "14.24",
    "raw_content": "版本更新内容..."
  }'
```

**请求体**:
```json
{
  "version": "latest",  // 可选，默认 latest
  "raw_content": "..."  // 可选，提供则不爬取
}
```

**响应**: 与 GET 请求相同

---

### 3. GET /health

健康检查端点

**请求示例**:
```bash
curl "http://localhost:8000/health"
```

**响应**:
```json
{
  "status": "healthy"
}
```

---

## 前端集成示例

### JavaScript / TypeScript

```javascript
// 分析最新版本
async function analyzeLatest() {
  const response = await fetch('http://localhost:8000/api/analyze?version=latest');
  const result = await response.json();
  console.log(result);
}

// 分析指定版本
async function analyzeVersion(version) {
  const response = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ version })
  });
  const result = await response.json();
  return result;
}

// 使用示例
analyzeVersion('14.24').then(result => {
  // 显示英雄变更
  result.top_lane_changes.forEach(change => {
    if (change.type === 'champion') {
      console.log(`${change.champion}: ${change.change_type}`);
    }
  });

  // 显示影响分析
  if (result.impact_analyses) {
    result.impact_analyses.forEach(analysis => {
      analysis.champion_analyses.forEach(champ => {
        console.log(`${champ.champion} - Tier: ${champ.meta_impact.tier_prediction}`);
      });
    });
  }
});
```

### React 示例

```typescript
import { useState } from 'react';

interface AnalysisResult {
  version: string;
  top_lane_changes: any[];
  impact_analyses: any[] | null;
  summary_report: any | null;
  metadata: any;
}

function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  const analyzeVersion = async (version: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/analyze?version=${version}`);
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('分析失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => analyzeVersion('latest')}>
        分析最新版本
      </button>

      {loading && <p>分析中...</p>}

      {result && (
        <div>
          <h2>版本 {result.version}</h2>
          <h3>变更列表</h3>
          <ul>
            {result.top_lane_changes.map((change, i) => (
              <li key={i}>
                {change.champion || change.item || change.category}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

## 响应数据结构

### 完整响应对象

```typescript
{
  version: string;                    // 版本号
  top_lane_changes: Change[];         // 上单相关变更列表
  impact_analyses: Analysis[] | null; // 影响分析（可能为空）
  summary_report: any | null;         // 总结报告（待实现）
  metadata: {
    extractor_tokens?: TokenUsage;    // Extractor Token 使用
    analyzer_tokens?: TokenUsage;     // Analyzer Token 使用
  };
}
```

### Change 对象

```typescript
{
  type: 'champion' | 'item' | 'system';  // 变更类型

  // 英雄变更 (type === 'champion')
  champion?: string;                      // 英雄名称
  change_type?: 'buff' | 'nerf' | 'adjust';
  relevance?: 'primary' | 'secondary';
  details?: Record<string, string>;

  // 装备变更 (type === 'item')
  item?: string;                          // 装备名称
  change?: string;                        // 变更描述

  // 系统变更 (type === 'system')
  category?: string;                      // 系统类别
  change?: string;                        // 变更描述
}
```

### Analysis 对象

```typescript
{
  champion_analyses: ChampionAnalysis[];
  meta_overview: MetaOverview;
  analysis_timestamp: string;
}

interface ChampionAnalysis {
  champion: string;
  change_type: string;
  gameplay_changes: {
    laning_phase: string;
    teamfight_role: string;
    build_adjustment: string;
  };
  meta_impact: {
    tier_prediction: 'S' | 'A' | 'B' | 'C' | 'D';
    tier_change: string;
    counter_changes: string[];
    synergy_items: string[];
  };
  overall_assessment: {
    strength_score: number;      // 1-10
    worth_practicing: boolean;
    win_rate_trend: string;
    reasoning: string;
  };
}

interface MetaOverview {
  top_tier_champions: string[];
  rising_picks: string[];
  falling_picks: string[];
  meta_shift_summary: string;
}
```

---

## 生产环境部署

### 使用 Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 使用 systemd

```ini
[Unit]
Description=LOL Top Lane Guide API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/LOLTopNews
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 常见问题

### 1. CORS 错误
如果前端遇到 CORS 错误，需要在 `api.py` 中配置允许的域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # 替换为你的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 性能优化
- 添加 Redis 缓存避免重复分析相同版本
- 使用异步队列处理长时间运行的分析任务
- 添加速率限制防止滥用

### 3. 错误处理
API 返回标准 HTTP 状态码：
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

错误响应格式：
```json
{
  "detail": "分析失败: 具体错误信息"
}
```
