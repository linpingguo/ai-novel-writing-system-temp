# AI Novel Writing System

8万字网文小说智能写作系统 - 基于AI技术的网络小说创作辅助平台

## 快速开始

### 一键启动

```bash
chmod +x start.sh
./start.sh
```

脚本会自动:
1. 检查并创建.env配置文件
2. 启动数据库和缓存服务
3. 提供启动命令提示

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+
- Node.js 18+

### 手动启动步骤

#### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑.env文件,设置必需的环境变量:
- SECRET_KEY: JWT密钥(建议使用随机字符串)
- POSTGRES_USER: 数据库用户名
- POSTGRES_PASSWORD: 数据库密码
- POSTGRES_DB: 数据库名称
- OPENAI_API_KEY: OpenAI API密钥(可选)
- CLAUDE_API_KEY: Claude API密钥(可选)

#### 2. 启动基础服务

```bash
docker-compose up -d db redis etcd minio
```

#### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 4. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5. 安装前端依赖

```bash
cd frontend
npm install
```

#### 6. 启动前端服务

```bash
cd frontend
npm run dev
```

## 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Swagger UI: http://localhost:8000/docs

## 项目结构

```
.
├── backend/          # FastAPI后端
│   ├── app/
│   │   ├── api/      # API路由
│   │   ├── models/   # 数据模型
│   │   └── services/ # 业务逻辑
│   ├── alembic/      # 数据库迁移
│   ├── requirements.txt
│   └── scripts/       # 脚本
├── frontend/         # React前端
│   ├── src/
│   │   ├── pages/   # 页面组件
│   │   ├── store/    # 状态管理
│   │   └── lib/      # 工具函数
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml # Docker编排
├── start.sh          # 一键启动脚本
├── .env.example      # 环境变量模板
├── QUICKSTART.md    # 快速启动指南
└── DEVELOPMENT_PROGRESS.md # 开发进度
```

## 技术栈

- 前端: React 18 + TypeScript + Vite + React Router
- 后端: Python 3.11+ (FastAPI)
- 数据库: PostgreSQL 15
- 缓存: Redis 7
- 向量数据库: Milvus 2.3
- 对象存储: MinIO
- AI模型: OpenAI GPT-4 / Claude 3 / 本地Llama 3
- 部署: Docker + Docker Compose

## 功能特性

### 已实现

#### 阶段1: 项目基础设施搭建 ✅
- 项目结构初始化
- Docker环境配置
- 后端基础框架(FastAPI + SQLAlchemy)
- 前端基础框架(React + TypeScript + Vite)
- 数据库Schema设计
- Redis和向量数据库配置

#### 阶段2: 用户认证和项目管理 ✅
- 用户注册和登录API
- JWT token认证
- 项目CRUD操作
- 项目导出功能
- 前端用户界面(登录/注册/项目列表/详情)

#### 阶段3: 角色管理和关系图谱 🔄
- 角色管理API
- 角色关系管理
- 角色图谱数据接口

### 规划中

- 阶段4: 大纲规划和情节编排
- 阶段5: 写作辅助服务
- 阶段6: 风格一致性控制
- 阶段7: 极致降低AI味功能
- 阶段8: 爆款网文参考写作结构服务
- 阶段9: 系统集成和优化
- 阶段10: 测试和部署

## 故障排查

### 端口被占用
```bash
lsof -i:3000
lsof -i:8000
kill -9 <PID>
```

### 数据库连接失败
```bash
docker-compose ps
docker-compose logs db
docker-compose restart db
```

### 前端构建失败
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 开发提示

1. 后端修改会自动热重载
2. 前端支持HMR热更新
3. API文档自动更新
4. 使用http://localhost:8000/docs查看API文档
5. LSP错误提示会在安装依赖后解决

## 下一步

详见开发进度文档: [DEVELOPMENT_PROGRESS.md](./DEVELOPMENT_PROGRESS.md)

## License

MIT
