#!/bin/bash
# LOL Top Lane Guide - API 服务器启动脚本

cd "$(dirname "$0")"

echo "🚀 启动 LOL Top Lane Guide API 服务器..."
echo "📍 访问地址: http://localhost:8000"
echo "📖 API 文档: http://localhost:8000/docs"
echo ""

cd app && python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload