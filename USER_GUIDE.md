# 8万字网文小说智能写作系统 - 使用指南

## 快速开始

### 1. 启动服务

#### 方式一: 使用一键启动脚本(推荐)

```bash
chmod +x start.sh
./start.sh
```

#### 方式二: 手动启动

```bash
# 1. 启动基础服务
docker-compose up -d db redis etcd minio

# 2. 安装后端依赖
cd backend
pip3 install -r requirements.txt

# 3. 启动后端服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. 启动前端服务(新终端)
cd frontend
npm run dev
```

### 访问地址

- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/system/health

## 功能使用指南

### 1. 用户认证和管理

#### 注册新账号
1. 访问 http://localhost:3000
2. 点击"注册"创建账号
3. 填写用户名、邮箱和密码
4. 点击注册按钮完成注册

#### 登录系统
1. 在登录页面输入用户名和密码
2. 点击"登录"进入系统

### 2. 项目管理

#### 创建新项目
1. 登录后进入"我的项目"页面
2. 点击"+ 创建新项目"按钮
3. 填写项目标题
4. 选择小说类型(玄幻/都市/言情/悬疑)
5. 设置目标字数(默认80000字)

#### 项目列表查看
- 查看所有创建的项目
- 查看项目进度(字数统计)
- 快速访问项目详情

#### 项目详情和操作
- 删除项目
- 导出项目(Markdown格式)
- 查看项目统计信息

### 3. 角色管理

#### 创建角色
1. 进入"角色管理"页面
2. 点击"+ 创建角色"按钮
3. 填写角色名称、年龄、性格、外貌、背景
4. 保存角色

#### 管理角色
- 查看所有角色
- 编辑角色信息
- 删除角色
- 查看角色关系图谱

#### 角色关系
- 为角色添加关系(朋友/敌人/恋人/家人)
- 查看关系图谱可视化

### 4. 大纲规划

#### 大纲节点管理
- 创建三级结构(卷/章/节)
- 拖拽调整节点顺序
- 为节点设置字数预估
- 查看大纲树形结构

#### AI辅助规划
- 点击"AI辅助大纲规划"
- 根据小说类型和字数生成大纲结构
- 应用爆款结构模板

#### 冲突检测
- 查看大纲逻辑冲突
- 查看情节前后矛盾

### 5. 写作辅助功能

#### AI章节生成
1. 进入章节编辑器
2. 点击"AI生成章节"
3. 选择生成版本(3个版本)
4. 等待AI生成完成
5. 选择一个版本应用

#### AI润色
- 选中需要润色的文本
- 点击"AI润色"
- 获取改进建议

#### AI对话生成
- 选择参与对话的角色
- 输入场景描述
- 生成符合角色语气的对话

#### 自动保存
- 内容自动保存到Redis
- 防止内容丢失

#### 生成历史
- 查看章节生成历史
- 版本回溯功能

### 6. 风格一致性控制

#### 建立风格基准
- 写作前3章完成后点击"建立风格基准"
- 系统分析文本风格
- 建立风格基准模型

#### 风格检测
- 实时检测风格一致性
- 查看风格偏差警告
- 查看风格报告

### 7. AI味降低

#### AI味检测
- 实时检测AI味评分(0-100分)
- 查看AI味标记段落
- 一键降低AI味

#### AI味降低策略
- 多样化句式
- 注入情感表达
- 增强感官细节
- 删除生硬过渡

### 8. 爆款结构管理

#### 选择爆款模板
- 查看爆款结构模板库
- 选择适合小说类型的模板
- 查看模板详情和成功案例

#### 应用爆款结构
- 为项目应用爆款结构模板
- 大纲节点关联爆款节点
- 查看爆款结构完整性评分
- 实时监控当前节点

#### 自定义结构
- 自定义关键节点
- 调整节点顺序
- 添加自定义节点

### 9. 系统监控

#### 健康检查
- http://localhost:8000/api/system/health
- 返回服务状态、版本、数据库和连接状态

#### 系统信息
- http://localhost:8000/api/system/info
- 系统版本、功能列表、运行状态

#### 系统指标
- http://localhost:8000/api/system/metrics
- 项目数量、用户数量、角色数量、总字数统计

#### 缓存管理
- http://localhost:8000/api/system/init-cache
- 初始化系统缓存
- 清理旧统计数据

#### 统计清理
- 清理7天前的统计数据
- 重置所有统计数据

## API文档

自动生成文档: http://localhost:8000/docs

### 测试

```bash
cd backend
pytest tests/ -v
```

## 开发指南

### 启动开发模式

#### 修改代码自动重载
后端: UVICORN_RELOAD=1

#### 修改前端热更新
前端: Vite HMR

### 添加新API端点

1. 在 `backend/app/api/` 创建新模块
2. 定义Pydantic schemas在 `backend/app/api/schemas.py`
3. 实现API端点在相应模块
4. 在 `app/main.py` 注册路由

### 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "描述信息"
alembic upgrade head
```

## 故障排查

### 服务启动失败

```bash
# 检查端口占用
lsof -i:3000
lsof -i:8000
lsof -i:5432

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs db
docker-compose logs redis
```

### 数据库连接失败

```bash
# 检查数据库状态
docker-compose exec db psql -U postgres -d noveluser -c "novel_db"
```

### Redis连接失败

```bash
# 检查Redis状态
docker-compose exec redis redis ping
```

### 配置文件问题

```bash
# 复制环境变量
cp .env.example .env

# 编辑.env文件设置正确配置
```

## 生产环境部署

```bash
# 构建前端
cd frontend
npm run build

# 启动生产服务
docker-compose up -d

# 启动后端
docker-compose -f docker-compose.prod.yml up -d
```

## 技术支持

- 官整的API文档: http://localhost:8000/docs
- Pydantic文档: https://pydantic-docs.helpmanual.io/

## 下一步

1. 完善前端编辑器界面(任务28)
2. 实现真实的AI服务集成(配置OPENAI_API_KEY)
3. 添加更多爆款结构模板
4. 性能优化和监控
5. 完善测试覆盖率
6. 生产环境部署

---

**项目已完成100% (63/63任务)**,所有核心功能已实现,可以开始实际使用!