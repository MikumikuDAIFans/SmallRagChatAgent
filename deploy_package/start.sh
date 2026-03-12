#!/bin/bash

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "❌ 错误: 未找到 .env 文件。"
    echo "请将 .env.example 复制为 .env 并填写您的 API Key。"
    echo "命令: cp .env.example .env"
    exit 1
fi

# 提取端口配置 (默认 11451)
APP_PORT=$(grep "^APP_PORT=" .env | cut -d '=' -f2)
if [ -z "$APP_PORT" ]; then
    APP_PORT=11451
fi

echo "🚀 开始构建 Docker 镜像..."
docker build -t rag-agent .

if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败"
    exit 1
fi

echo "🛑 停止并删除旧容器 (如果存在)..."
docker stop rag-agent 2>/dev/null
docker rm rag-agent 2>/dev/null

echo "▶️ 启动新容器..."
# 使用 pwd 获取当前路径，确保挂载正确
CURRENT_DIR=$(pwd)

docker run -d \
  -p ${APP_PORT}:${APP_PORT} \
  -v "$CURRENT_DIR/data":/app/data \
  -v "$CURRENT_DIR/System_prompt.txt":/app/System_prompt.txt \
  --env-file .env \
  --name rag-agent \
  rag-agent

if [ $? -eq 0 ]; then
    echo "✅ 服务已启动！"
    echo "API 地址: http://localhost:${APP_PORT}/chat"
    echo "您可以使用 'docker logs -f rag-agent' 查看日志"
else
    echo "❌ 服务启动失败"
    exit 1
fi
