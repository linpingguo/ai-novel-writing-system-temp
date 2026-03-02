#!/bin/bash

set -e

echo "🚀 启动8万字网文小说智能写作系统"

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件,从.env.example复制..."
    cp .env.example .env
    echo "✅ .env文件已创建,请编辑配置正确的环境变量"
    echo ""
    echo "必需配置项:"
    echo "  - SECRET_KEY: 设置一个随机密钥"
    echo "  - POSTGRES_USER: 数据库用户名"
    echo "  - POSTGRES_PASSWORD: 数据库密码"
    echo "  - POSTGRES_DB: 数据库名称"
    echo "  - OPENAI_API_KEY: OpenAI API密钥(可选)"
    echo "  - CLAUDE_API_KEY: Claude API密钥(可选)"
    echo ""
    read -p "按Enter继续,或按Ctrl+C取消..."
fi

# 启动基础服务
echo "📦 启动数据库和缓存服务..."
docker-compose up -d db redis etcd minio

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
docker-compose ps

echo ""
echo "✅ 基础服务已启动"
echo ""
echo "📝 后端服务启动命令:"
echo "  cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📝 前端服务启动命令:"
echo "  cd frontend && npm run dev"
echo ""
echo "🌐 访问地址:"
echo "  前端: http://localhost:3000"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "💡 提示: 在新终端中分别启动后端和前端服务"
