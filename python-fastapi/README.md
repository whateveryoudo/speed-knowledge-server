# FastAPI Server

基于 FastAPI 框架的现代化后端 API 服务器

## 技术栈

- **框架**: FastAPI
- **语言**: Python 3.11+
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT
- **文档**: OpenAPI (Swagger)
- **验证**: Pydantic

## 功能特性

- ✅ RESTful API 设计
- ✅ JWT 身份认证
- ✅ 自动数据验证和序列化
- ✅ 自动生成 API 文档
- ✅ SQLAlchemy 2.0 异步支持
- ✅ 用户管理模块
- ✅ 密码加密
- ✅ 类型提示完善
- ✅ CORS 支持

## 快速开始

### 前置要求

- Python 3.11+
- PostgreSQL 14+
- pip 或 Poetry

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 开发环境安装开发依赖
pip install -r requirements-dev.txt
```

### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接和其他参数。

### 运行应用

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --port 8000

# 或使用 Python 直接运行
python -m app.main

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 访问应用

- API 服务: http://localhost:8000
- API 文档 (Swagger): http://localhost:8000/api/docs
- API 文档 (ReDoc): http://localhost:8000/api/redoc

## 项目结构

```
app/
├── api/                 # API 路由
│   └── v1/
│       ├── endpoints/  # 端点
│       │   ├── users.py
│       │   └── auth.py
│       └── api.py
├── core/               # 核心配置
│   ├── config.py
│   ├── security.py
│   └── deps.py
├── models/             # 数据模型
│   └── user.py
├── schemas/            # Pydantic 模式
│   └── user.py
├── services/           # 业务逻辑
│   └── user_service.py
├── db/                 # 数据库
│   ├── base.py
│   └── session.py
└── main.py             # 应用入口
```

## API 端点

### 健康检查
- `GET /` - 欢迎信息
- `GET /health` - 健康状态

### 认证
- `POST /api/v1/auth/login` - 用户登录

### 用户管理
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users` - 获取所有用户
- `GET /api/v1/users/{id}` - 获取单个用户
- `PATCH /api/v1/users/{id}` - 更新用户
- `DELETE /api/v1/users/{id}` - 删除用户

## 开发指南

### 代码格式化

```bash
# 使用 black 格式化代码
black app/

# 使用 isort 排序导入
isort app/

# 运行代码检查
flake8 app/
pylint app/

# 类型检查
mypy app/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并查看覆盖率
pytest --cov=app tests/

# 生成 HTML 覆盖率报告
pytest --cov=app --cov-report=html tests/
```

### 数据库迁移

```bash
# 初始化 Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t fastapi-app .

# 运行容器
docker run -p 8000:8000 --env-file .env fastapi-app

# 使用 docker-compose
docker-compose up -d
```

### 生产环境注意事项

1. 设置 `ENVIRONMENT=production`
2. 设置 `DEBUG=False`
3. 使用强密钥作为 `SECRET_KEY`（至少 32 字符）
4. 配置正确的 CORS 策略
5. 启用 HTTPS
6. 使用进程管理器（如 Gunicorn + Uvicorn workers）
7. 配置日志和监控
8. 使用数据库迁移而非自动创建表

### 推荐的生产环境启动命令

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

## 性能优化

- 使用连接池管理数据库连接
- 启用查询结果缓存
- 实现分页查询
- 使用异步编程提高并发性能
- 配置适当的 worker 数量

## 许可证

MIT

