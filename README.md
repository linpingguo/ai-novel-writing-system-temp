# AI Novel Writing System

8万字网文小说智能写作系统 - 基于AI技术的网络小说创作辅助平台

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+
- Node.js 18+

### 启动开发环境

1. 复制环境变量配置
```bash
cp .env.example .env
```

2. 启动基础服务
```bash
docker-compose up -d db redis etcd minio
```

3. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

4. 安装前端依赖
```bash
cd frontend
npm install
```

5. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. 启动前端服务
```bash
cd frontend
npm run dev
```

访问 http://localhost:3000 查看应用

## 项目结构

```
.
├── backend/          # FastAPI后端
│   ├── app/
│   │   ├── api/      # API路由
│   │   ├── models/   # 数据模型
│   │   └── services/ # 业务逻辑
│   └── tests/        # 测试
├── frontend/         # React前端
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── public/
├── docker-compose.yml # Docker编排
└── .monkeycode/     # 项目文档
```

## 技术栈

- **前端**: React 18 + TypeScript + Vite
- **后端**: Python 3.11+ (FastAPI)
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **AI模型**: OpenAI GPT-4 / Claude 3

## 许可证

MIT
