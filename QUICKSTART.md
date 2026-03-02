# 快速启动指南

## 前置条件

- Docker和Docker Compose已安装
- Python 3.11+已安装
- Node.js 18+已安装

## 一键启动(推荐)

```bash
chmod +x start.sh
./start.sh
```

脚本会自动:
1. 检查并创建.env配置文件
2. 启动数据库和缓存服务
3. 提供启动命令提示

## 手动启动步骤

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件,设置正确的配置
```

### 2. 启动基础服务

```bash
docker-compose up -d db redis etcd minio
```

### 3. 启动后端服务

```bash
cd backend
pip3 install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 启动前端服务(新终端)

```bash
cd frontend
npm install
npm run dev
```

## 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Swagger UI: http://localhost:8000/docs

## 环境变量说明

必需配置项:
- SECRET_KEY: JWT密钥(建议使用随机字符串)
- POSTGRES_USER: 数据库用户名
- POSTGRES_PASSWORD: 数据库密码
- POSTGRES_DB: 数据库名称

可选配置项:
- OPENAI_API_KEY: OpenAI API密钥
- CLAUDE_API_KEY: Claude API密钥
- MINIO_ACCESS_KEY: MinIO访问密钥
- MINIO_SECRET_KEY: MinIO密钥

## 已实现功能

### 阶段1: 项目基础设施搭建 ✅
- 项目结构初始化
- Docker环境配置
- 后端基础框架(FastAPI + SQLAlchemy)
- 前端基础框架(React + TypeScript + Vite)
- 数据库Schema设计
- Redis和向量数据库配置

### 阶段2: 用户认证和项目管理 ✅
- 用户注册和登录API
- JWT token认证
- 项目CRUD操作
- 项目导出功能
- 前端用户界面(登录/注册/项目列表/详情)

### 阶段3: 角色管理和关系图谱 🔄
- 角色管理API
- 角色关系管理
- 角色图谱数据接口

## 故障排查

### 端口被占用
```bash
# 查看端口占用
lsof -i:3000
lsof -i:8000

# 杀死进程
kill -9 <PID>
```

### 数据库连接失败
```bash
# 检查数据库容器状态
docker-compose ps
docker-compose logs db

# 重启数据库
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
5. 所有LSP错误在安装依赖后会解决

## 下一步开发计划

1. 完成角色管理前端界面(任务13)
2. 实现大纲规划服务(任务16-21)
3. 开发写作辅助服务(任务22-30)
4. 实现风格一致性控制(任务31-36)
5. 开发AI味降低功能(任务37-42)
6. 实现爆款结构服务(任务43-50)
7. 系统集成和优化(任务51-56)
8. 测试和部署(任务57-63)
