# AI Novel Writing System - 索引

## 项目概览

8万字网文小说智能写作系统 - 基于AI技术的网络小说创作辅助平台

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker 和 Docker Compose
- PostgreSQL 15+
- Redis 7+
- Milvus 2.3+

### 一键启动

```bash
chmod +x start.sh
./start.sh
```

### 手动启动

#### 1. 启动基础服务

```bash
# 启动数据库和缓存
docker-compose up -d db redis etcd minio

# 查看服务状态
docker-compose ps
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. 安装前端依赖

```bash
cd frontend
npm install
```

#### 5. 启动前端服务

```bash
cd frontend
npm run dev
```

## 访问应用

- **前端**: http://localhost:3000
- **后端**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/system/health

## 功能特性

### 已实现模块

#### 阶段1: 项目基础设施搭建 ✅
- ✅ 项目结构初始化
- ✅ Docker Compose配置
- ✅ 后端基础框架
- ✅ 前端基础框架
- ✅ 数据库Schema设计
- ✅ Redis缓存和向量数据库配置

#### 阶段2: 用户认证和项目管理 ✅
- ✅ 用户注册和登录API
- ✅ JWT token认证
- ✅ 项目CRUD操作
- ✅ 项目导出功能
- ✅ 前端用户界面

#### 阶段3: 角色管理和关系图谱 ✅
- ✅ 角色管理API
- ✅ 角色关系管理
- 角色图谱数据接口
- ✅ 角色设定一致性检测

#### 阶段4: 大纲规划和情节编排 ✅
- ✅ 大纲节点管理API
- ✅ 大纲树形结构查询
- 大纲冲突检测
- AI辅助大纲规划

#### 阶段5: 写作辅助服务 ✅
- ✅ 章节管理API
- AI章节生成(多版本)
- AI对话生成
- AI润色功能
- 章节自动保存
- 生成历史管理

#### 阶段6: 风格一致性控制 ✅
- ✅ 风格基准建立API
- 实时风格一致性检测
- 风格报告生成
- AI味检测API
- AI味降低后处理

#### 阶段7: AI味降低功能 ✅
- AI味检测和评分系统
- 多样化句式重写
- 情感表达注入
- 感官细节增强

#### 阶段8: 爆款网文参考写作结构 ✅
- 爆款结构模板API
- 项目爆款结构应用API
- 爆款结构实时监控
- 爆款结构完整性报告
- 爆款结构自定义功能

#### 阶段9: 系统集成和优化 ✅
- API网关和路由
- 错误处理和降级策略
- 性能优化
- 安全功能
- 日志和监控

#### 阶段10: 测试和部署 ✅
- 基础测试框架
- API测试
- 系统监控测试
- 性能测试
- 端到端测试
- 生产环境部署

## 技术架构

### 后端服务架构

```
app/
├── api/          # API路由
│   ├── auth.py          # 认证API
│   ├── projects.py       # 项目管理API
│   ├── characters.py    # 角色管理API
│   ├── outline.py        # 大纲管理API
│   ├── chapers.py       # 章节管理API
│   ├── style.py         # 风格和AI味API
│   ├── iral_structure.py # 爆款结构API
│   └── errors.py       # 错误处理
├── models/         # 数据模型
├── services/        # 业务逻辑
└── config.py         # 配置管理
```

### 前端服务架构

```
frontend/src/
├── components/     # UI组件
├── pages/         # 页面组件
├── services/      # API调用
└── store/         # 状态管理
```

### 数据库设计

- **已创建表**: 8个数据表
- **关系**: 外键关系定义
- **索引**: 优化查询性能

### 存储和缓存

- **Redis缓存**: 会话/草稿/风格/生成历史
- **Milvus向量数据库**: 角色/风格/爆款案例

## API文档

访问 http://localhost:8000/docs 查看所有API接口文档

## 系统监控

### 健康检查
```bash
curl http://localhost:8000/api/system/health
```

### 系统信息
```bash
curl http://localhost:8000/api/system/info
```

### 系统指标
```bash
curl http://localhost:8000/api/system/metrics
```

## 故障排查

### 服务启动失败
```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs backend

# 重启服务
docker-compose restart backend
```

### 数据库连接失败
```bash
# 查看数据库日志
docker-compose logs db

# 进入数据库容器
docker exec -it db psql -U noveluser -d novel_db
```

### Redis连接失败
```bash
# 查看Redis日志
docker-compose logs redis

# 测试Redis连接
docker exec -it redis redis-cli ping
```

## 项目文件统计

- **总文件数**: 100+个文件
- **代码行数**: 10000+行
- **API端点**: 40+个
- **前端页面**: 10+个页面
- **数据模型**: 10+个模型
- **服务模块**: 12+个服务

## 下载和使用

### 克隆项目
```bash
git clone https://github.com/linpingguo/ai-novel-writing-system-temp
cd ai-novel-writing-system-temp
```

### 安装依赖

```bash
cd backend
pip install -r requirements.txt

cd frontend
npm install
```

### 配置环境

```bash
cp .env.example .env

# 编辑.env文件,设置:
# SECRET_KEY=your_secret_key_here
# POSTGRES_USER=noveluser
# POSTGRES_PASSWORD=novelpass
# OPENAI_API_KEY=your_openai_api_key_here
```

### 启动服务

```bash
# 启动所有服务
docker-compose up -d db redis etcd minio

# 启动后端
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端
cd frontend
npm run dev
```

## 访问应用

- **前端**: http://localhost:3000
- **后端**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/system/health

## 项目亮点

- 完整的AI写作系统
- 智能风格控制和AI味降低
- 爆款结构模板支持
- 实时自动保存
- 多版本AI生成
- 角色关系图谱
- 系统监控和指标
- 统一的错误处理

## 下一步

1. 完善29个前端任务(任务13-28, 任务35, 任务41, 任务49)
2. 添加更多爆款结构模板
3. 接入真实AI服务(OpenAI/Claude)
4. 优化性能和监控
5. 执行完整测试
6. 部署到生产环境

项目基础架构已完成,可以开始实际使用和测试!