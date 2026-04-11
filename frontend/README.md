# LOL Top News Frontend

Author: Ren

## Quick Start

### English

```bash
npm install
npm run dev
```

Optional:

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

Build for production:

```bash
npm run build
```

### 中文

```bash
npm install
npm run dev
```

如果后端不在同一个地址，可以这样启动：

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

生产构建：

```bash
npm run build
```

## What It Does / 人话功能介绍

### English

This app turns League of Legends patch notes into a top-lane focused summary.

- Analyze the latest patch or a specific patch version.
- Show top-lane champion changes in a faster, easier-to-scan format.
- Give an AI-generated summary of what actually matters for top-lane players.
- Let users switch between cached historical versions instantly.
- Support email subscription for patch update notifications.

### 中文

这个应用会把《英雄联盟》版本更新说明，整理成更适合上单玩家看的简化版。

- 可以分析最新版本，也可以指定某个版本号。
- 会把和上单相关的英雄改动提炼出来，不用自己硬啃整篇公告。
- 会给出一版 AI 总结，直接说这个版本上单环境大概怎么变。
- 支持切换历史版本，快速回看以前的分析结果。
- 支持邮件订阅，有新版本时可以收到提醒。
