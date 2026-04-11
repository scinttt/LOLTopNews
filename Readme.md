# LOL Top Lane Guide

Author: Ren

## Quick Start

### English

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
npm run dev
```

If your backend runs on another address:

```bash
cd frontend
VITE_API_URL=http://localhost:8000 npm run dev
```

### 中文

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
npm run dev
```

如果后端不在同一个地址，可以这样启动前端：

```bash
cd frontend
VITE_API_URL=http://localhost:8000 npm run dev
```

## Feature

### English

This project turns League of Legends patch notes into a top-lane focused summary.

- Analyze the latest patch or a specific patch version.
- Pull out the champion and system changes that actually matter for top lane.
- Generate an AI summary so players can quickly understand the new meta.
- Support fast switching between cached historical versions.
- Support email subscription for patch update notifications.

### 中文

这个项目会把《英雄联盟》版本更新说明整理成更适合上单玩家看的版本。

- 可以分析最新版本，也可以指定某个版本号。
- 会提炼出真正和上单有关的英雄与系统改动。
- 会生成一版 AI 总结，帮助玩家快速看懂版本环境变化。
- 支持快速切换历史缓存版本。
- 支持邮件订阅版本更新提醒。
