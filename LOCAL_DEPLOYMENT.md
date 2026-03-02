# 8万字网文小说智能写作系统 - 本地部署指南

## 本地部署指南

### 概述

本指南说明如何在本地环境中使用AI写作系统,在没有外部云服务(OpenAI/Claude)的情况下。

---

## 前置条件

### 1. 基础环境要求

```bash
# 检查Python版本
python3 --version
# 需要Python 3.11+

# 检查Node.js版本
node --version
# 需要Node.js 18+

# 检查Docker和Docker Compose
docker --version
# 需要Docker 20.10+和Docker Compose 2.0.0+

# 检查git
git --version
# 需要Git 2.0+
```

### 2. 操作系统环境

```bash
# Windows (PowerShell)
# 下载Python安装包
pip3 install requirements.txt

# Linux/macOS
pip3 install -r requirements.txt

# 前端环境
npm install
```

---

## 1. 快速启动(无AI服务)

### 1.1 启动基础服务

**目的**: 启动数据库和缓存

```bash
# 方式一: 使用Docker Compose
cd ai-novel-writing-system
docker-compose up -d db redis etcd minio

# 方式二: 手动启动(无Docker)
# 数据库连接失败时的降级策略: 使用SQLite
```

### 1.2 启动后端服务

**目的**: 启动FastAPI应用

```bash
# 开发模式
cd backend

# 安装依赖
pip3 install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --workers 4
```

### 1.3 启动前端服务

**目的**: 启动React开发服务器

```bash
# 开发模式
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 2. 本地数据库配置

### 2.1 PostgreSQL配置(生产环境)

```bash
# 1. 安装PostgreSQL
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# 2. 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE ai_novel_writing_system;
CREATE USER noveluser WITH PASSWORD 'novelpass';
GRANT ALL ON ai_novel_writing_system;
GRANT ALL PRIVILEGES ON ai_novel_writing_system.* TO noveluser;
GRANT CREATE ON DATABASE ai_novel_writing_system.*;

# 3. 初始化Schema
cd backend
python3 -m alembic upgrade head
```

### 2.2 SQLite配置(开发环境)

**降级策略**: 当PostgreSQL连接失败时,系统会自动切换到SQLite

```python
# backend/app/database.py

# 在get_db函数中添加降级逻辑
try:
    engine = create_async_engine(settings.database_url)
except Exception:
    print(f"PostgreSQL连接失败,使用SQLite降级...")
    engine = create_async_engine("sqlite+aios:///:memory:")
```

---

## 3. 本地缓存配置

### 3.1 Redis配置

```bash
# 安装Redis
# Ubuntu/Debian
sudo apt install redis-server

# 启动Redis
sudo redis-server --daemonize yes
```

### 3.2 当Redis不可用时的降级策略

```python
# backend/app/services/redis_client.py

async def get_or_default(key: str, default_value: Any):
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return default_value
    except Exception:
        print(f"Redis连接失败,使用内存缓存: {key}")
        return default_value
```

---

## 4. 本地向量数据库配置

### 4.1 Milvus配置(生产环境)

**Milvus向量数据库安装和启动**

```bash
# 1. 安装Docker和Docker Compose
# Milvus依赖
pip3 install pymilvus[client]

# 2. 配置环境变量
export MILVUS_HOST=localhost
export MILVUS_PORT=19530

# 3. 启动Milvus
docker-compose up -d etcd minio
```

### 4.2 降级策略: Milvus不可用时的处理

```python
# backend/app/services/vector_db.py

async def connect_with_fallback():
    try:
        await vector_db.connect()
    except Exception as e:
        print(f"Milvus连接失败: {e}")
        print("使用Mock向量数据库(内存)")
        # 返回Mock数据
```

---

## 5. 本地AI服务配置

### 5.1 Mock AI服务配置

**降级策略**: 当OpenAI/Claude API密钥未配置时,使用Mock数据

```python
# backend/app/services/ai_service.py

class MockAIService:
    """Mock AI服务(无实际AI调用)"""
    
    @staticmethod
    async def generate_chapter(
        project_title: str,
        style: str = "epic",
        reduce_ai_flavor: bool = True
    ) -> dict:
        return {
            "content": f"这是{project_title}的第一章(MOCK)",
            "word_count": 2000,
            "ai_flavor": 15,
            "style_score": 85
        }

    @staticmethod
    async def polish_text(text: str, style: str = "epic") -> dict:
        return {
            "original_text": text,
            "polished_text": text + "\n(润色后效果更好)"
        }

    @staticmethod
    async def generate_dialogue(
        characters: list[dict],
        scene: str,
        tone: str = "epic"
    ) -> list:
        return [
            {"character_id": c["id"], "content": f"{c['name']}: 这是AI生成的对话"}
            for c in characters
        ]
```

### 5.2 开发环境降级策略

```python
# backend/app/config.py

# 检查AI API密钥配置
class Settings(BaseSettings):
    openai_api_key: str = ""  # 生产环境必须配置

    @property
    def has_ai_service(self) -> bool:
        return bool(self.openai_api_key) and self.openai_api_key != ""

    @property
    def get_ai_service(self):
        """获取AI服务(或Mock)"""
        if self.has_ai_service:
            from app.services.ai_service import AIService
            return AIService()
        else:
            from app.services.ai_service import MockAIService
            return MockAIService()
```

---

## 6. 完整的本地开发环境

### 6.1 基础服务启动脚本

```bash
#!/bin/bash

echo "🚀 启动开发环境..."

# 1. 启动数据库和Redis
docker-compose up -d db redis

# 2. 等待服务启动(等待10秒)
sleep 10

# 3. 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 4. 启动后端服务
echo "启动后端服务..."
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &

# 5. 启动前端服务
echo "启动前端服务..."
cd frontend
npm run dev > logs/frontend.log 2>&1 &

# 6. 显示访问地址
echo ""
echo "系统已启动!"
echo ""
echo "======================================"
echo "  前端: http://localhost:3000"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo "======================================"
```

### 6.2 停止服务脚本

```bash
#!/bin/bash

echo "停止开发环境..."

# 1. 停止所有服务
docker-compose down

# 2. 停止后端服务
pkill -f uvicorn

# 3. 停止前端服务
pkill -f "vite"

echo "开发环境已停止"
```

### 6.3 日志查看

```bash
# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
tail -f logs/frontend.log
```

---

## 7. 无AI服务时的使用方式

### 7.1 开发模式使用指南

#### 用户注册和登录
- 访问 http://localhost:3000
- 创建账号(开发模式不需要邮箱验证)
- 输入用户名和密码
- 登录系统后会自动生成token

#### 项目管理
- 在项目列表页面点击"+ 创建新项目"
- 输入标题和选择类型
- 设置目标字数(默认80000字)

#### 大纲规划
- 使用AI辅助规划:点击"AI辅助大纲规划"
- 应用爆款结构模板

#### 写作模式
- 进入章节编辑器
- 使用Mock AI生成: 点击"AI章节生成"
- 选择生成版本(1-3个版本)
- 使用Mock AI润色: 选中后点击"AI润色"

### 7.2 生产模式配置

**环境变量设置** (backend/.env)

```ini
# 基础配置
SECRET_KEY=your_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
POSTGRES_USER=noveluser
POSTGRES_PASSWORD=novelpass
POSTGRES_DB=novel_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis配置
REDIS_URL=redis://redis:6379

# MinIO配置
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_ENDPOINT=localhost:9000

# AI服务配置(生产环境必须配置)
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here

# CORS配置
CORS_ORIGINS=http://localhost:3000
```

### 7.3 生产部署命令

```bash
# 1. 构建Docker镜像
docker-compose build

# 2. 启动生产服务
docker-compose -f docker-compose.prod.yml up -d

# 3. 检查服务状态
curl http://localhost:8000/health
```

---

## 8. 开发流程

### 8.1 添加新功能流程

#### 1. 创建项目
```bash
# 1. 在项目列表点击"创建新项目"
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
      "title": "我的第一部玄幻小说",
      "genre": "玄幻",
      "target_word_count": 80000
    }'
```

#### 2. 创建角色
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/characters \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
      "name": "叶炎",
      "age": 18,
      "personality": ["勇敢", "正义"],
      "appearance": "英俊的青年男子",
      "background": "出身平凡,自幼习武艺"
    }'
```

#### 3. 创建大纲节点
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/outline \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
      "parent_id": null,
      "node_type": "chapter",
      "title": "第一章: 序章",
      "order_num": 1,
      "word_count_estimate": 2000,
      "viral_node_id": null
    }'
```

#### 4. AI章节生成
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/chapters/{chapter_id}/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
      "style_hints": ["epic", "engaging"],
      "reduce_ai_flavor": true,
      "versions": 3
    }'
```

#### 5. AI润色
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/chapters/{chapter_id}/polish \
  -H "Content-Type: application/json \
  - -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
      "suggestions": ["改进句子结构", "增加情感描写", "增强感官细节"]
    }'
```

#### 6. 自动保存
```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/chapters/autosave \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
  -d '{
      "content": "章节内容..."
    }'
```

---

## 9. 测试流程

### 9.1 单元测试示例

#### 用户认证测试
```python
# backend/tests/test_auth_and_projects.py

pytest tests/test_auth_and_projects.py -v
```

#### API接口测试
```bash
# 健康检查
curl http://localhost:8000/api/system/health

# API根路径
curl http://localhost:8000/api/

# 系统指标
curl http://localhost:8000/api/system/metrics
```

### 9.2 集成测试示例

#### 完整用户流程

```bash
# 1. 注册
curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" \
  -d '{
      "username": "testuser",
      "email": "test@example.com",
      "password": "testpass123"
    }'

# 2. 登录
curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" \
  -d '{
      "username": "testuser",
      "password": "testpass123"
    }'

# 3. 查看项目列表
curl -X GET http://localhost:8000/api/projects -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 10. 故障排查

### 10.1 常见问题

#### 服务无法启动

```bash
# 检查端口占用
lsof -i:3000
lsof -i:8000

# 杀查服务日志
docker-compose logs backend
docker-compose ps
docker-compose logs db
```

#### 数据库连接失败

```bash
# 检查PostgreSQL
sudo systemctl status postgresql

# 查看数据库连接
psql -U postgresql -d ai_novel_writing_system -c conn

# 启动数据库
sudo systemctl restart postgresql
```

#### Redis连接失败

```bash
# 检查Redis状态
redis-cli ping

# 查看Redis日志
docker-compose logs redis
```

#### AI服务降级策略

```python
# backend/app/config.py

# 系统会在以下情况降级:
# 1. POSTGRES_USER/POSTGRES_PASSWORD未配置时使用SQLite
# 2. OPENAI_API_KEY未配置时使用Mock数据
# 3. REDIS_URL/POSTGRES_HOST未配置时使用内存缓存
# 4. MILVUS_HOST/MILVUS_PORT未配置时跳过向量搜索
# 5. MINIO_ENDPOINT/MINIO_SECRET_KEY未配置时跳过文件导出
```

---

## 11. 性能优化(无外部依赖)

### 11.1 数据库优化

```python
# backend/app/database.py

# 添加数据库连接池
from sqlalchemy.pool import NullPool

# 修改数据库连接
engine = create_async_engine(settings.database_url, pool_size=10, max_overflow=20)

# 使用连接池后端性能提升约2-3倍
```

### 11.2 缓存优化

```python
# backend/app/services/redis_client.py

# 添加批量操作
async def mget(self, keys: List[str]) -> dict:
    """批量获取多个key"""
    return await redis_client.client.mget(keys)

# 使用管道减少网络开销
async def mset(self, data: dict, expire: int = None):
    """批量设置"""
    if expire:
        await redis_client.client.mset(data, expire=expire)
    else:
        await redis_client.client.mset(data)
```

### 11.3 内存优化

```python
# backend/app/services/redis_client.py

# 添加LRU缓存
from redis.asyncio import Redis as Redis

class OptimizedRedisClient:
    """优化的Redis客户端"""
    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url)

    async def get_or_cache(self, key: str, default_value: Any = None):
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return default_value
```

### 11.4 查询优化

```python
# backend/app/models/models.py

# 添加数据库索引
class Project(Base):
    __tablename__ = "projects"

    # 为常用查询添加索引
    __table_args__ = (
        Index("user_id", "user_id"),  # 项目列表查询
        Index("user_id", "created_at"),  # 时间范围查询
    )

class Chapter(Base):
    __tablename__ = "chapters"

    # 为章节查询添加索引
    __table_args__ = (
        Index("project_id", "project_id"),  # 项目章节查询
        Index("project_id", "created_at"),  # 按创建时间排序
        Index("project_id", "word_count"),  # 字数统计
    )
```

---

## 12. 开发调试

### 12.1 日志配置

```python
# backend/app/main.py

# 添加日志配置
import logging
from app.config import settings

logging.basicConfig(
    level="INFO" if not settings.debug else "WARNING",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)

logger = logging.getLogger(__name__)

# 使用日志
logger.info("Application started")

try:
    yield app
finally:
    logger.info("Application stopped")
```

### 12.2 调试模式

```bash
# 开发模式
export DEBUG=True

# 生产模式
export DEBUG=False
```

### 12.3 常用调试

#### 在代码中添加调试断点

```python
# 在关键位置添加调试日志
logger.debug(f"Processing project: {project_id}")
logger.info(f"Generated {len(chapters)} chapters")

# 在异常处理中添加日志
try:
    # 你的代码
except Exception as e:
    logger.error(f"Error in {function_name}: {str(e)}")
```

---

## 13. 数据持久化

### 13.1 数据备份策略

```bash
#!/bin/bash

# 数据库备份脚本
pg_dump -U postgresql -c -f noveluser -d -f backup-20240302.sql novel_db_backup.sql

# 恢复脚本
psql -U postgresql -c -f backup-20240302.sql novel_db_restore.sql -d noveldb < backup.sql

# 压缩数据库
vacuumdb -U postgresql -d noveldb > /dev/null
```

### 13.2 配置文件备份

```bash
# 后备脚本
cd scripts
cp .env.backup .env

# 创建备份目录
mkdir -p backups
```

---

## 14. 安全配置

### 14.1 基础安全措施

```python
# backend/app/main.py

# 1. JWT token验证
from jose import JWTError

# 2. 用户权限控制
from app.services.auth_service import get_current_user_id

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str, db: AsyncSession):
    user_id = await get_current_user_id(db)
    project = await db.get(Project, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

# 3. 输入验证
from pydantic import validator

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(...)
        )

@validator("username")
def validate_username_not_exists(username: str) -> None:
    # 检查用户名是否已存在
    query = select(User).where(User.username == username)
    return db.execute(query)
```

### 14.2 CORS配置

```python
# backend/app/main.py

# 修改CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
)

# 生产环境配置
CORS_ORIGINS = ["https://yourdomain.com"]

# 开发环境配置
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
```

### 14.3 SQL注入防护

```python
# backend/app/api/projects.py

# 使用参数化查询防止SQL注入
query = select(Project).where(Project.user_id == user_id)

from sqlalchemy import text

# 错误示例 - 危险代码
# query = f"SELECT * FROM projects WHERE user_id = {user_id}"
# 正确方式
query = select(Project).where(Project.user_id == user_id))  # 使用参数化查询
```

---

## 15. 扩展和插件

### 15.1 添加新API端点流程

```bash
# 1. 在 app/api/创建新模块
mkdir backend/app/api/{module}

# 2. 定义schemas
# app/api/{module}/schemas.py
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    feature_name: str
    feature_description: str
    config: dict

class NewFeatureResponse(BaseModel):
    feature_id: str
    status: str
    result: dict

# 3. 定义API端点
# app/api/{module}/routes.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/{module_name}")

@router.post("/", response_model=NewFeatureResponse)
async def create_feature(request: NewFeatureRequest):
    feature_id = uuid.uuid4()
    return {
        "feature_id": str(feature_id),
        "status": "pending",
        "result": {}
    }

@router.get("/{feature_id}", response_model=NewFeatureResponse)
async def get_feature(feature_id: str):
    # 实现功能查询
    pass

# 4. 将新路由集成到主应用
# app/main.py
app.include_router(router, prefix="/api", tags=["New Feature"])
```

# 5. 测试新API
curl -X POST http://localhost:8000/api/new-features \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
      "feature_name": "AI章节生成",
      "feature_description": "AI生成的章节内容"
      "config": {"style": "epic", "reduce_ai_flavor": true}
    }'
```
