# Speed Knowledge Server - 多语言后端脚手架

这是一个包含三种主流后端技术栈的完整项目脚手架，适合快速启动 API 服务开发。

## 📚 技术栈选择

### 1. **Node.js + NestJS** (`nodejs-nestjs/`)
- **框架**: NestJS 10
- **语言**: TypeScript
- **ORM**: TypeORM
- **特点**: 企业级框架，模块化设计，依赖注入，适合大型项目

### 2. **Python + FastAPI** (`python-fastapi/`)
- **框架**: FastAPI
- **语言**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **特点**: 现代化、高性能、自动文档生成，类型提示完善

### 3. **Go + Gin** (`go-gin/`)
- **框架**: Gin
- **语言**: Go 1.21+
- **ORM**: GORM
- **特点**: 高性能、轻量级、编译型语言，适合高并发场景

## 🎯 共同特性

所有三个脚手架都包含以下功能：

- ✅ RESTful API 设计
- ✅ JWT 身份认证
- ✅ 用户管理模块（CRUD）
- ✅ 数据验证和类型安全
- ✅ API 文档（Swagger/OpenAPI）
- ✅ 数据库集成（PostgreSQL）
- ✅ 密码加密存储
- ✅ CORS 支持
- ✅ Docker 容器化
- ✅ 开发环境热重载
- ✅ 统一的响应格式
- ✅ 错误处理

## 📂 项目结构

```
speed-knowledge-server/
├── .cursorrules           # Cursor AI 编码规则
├── nodejs-nestjs/         # NestJS 项目
├── python-fastapi/        # FastAPI 项目
├── go-gin/                # Gin 项目
└── README.md              # 本文件
```

## 🚀 快速开始

### 选择你的技术栈

根据你的需求和偏好，进入对应的目录：

#### Node.js + NestJS

```bash
cd nodejs-nestjs
pnpm install
cp .env.example .env
# 编辑 .env 配置数据库
pnpm run start:dev
```

访问: http://localhost:3000/api/docs

#### Python + FastAPI

```bash
cd python-fastapi
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置数据库
python -m app.main
```

访问: http://localhost:8000/api/docs

#### Go + Gin

```bash
cd go-gin
go mod download
cp .env.example .env
# 编辑 .env 配置数据库
make swag  # 生成 Swagger 文档
make run
```

访问: http://localhost:8080/swagger/index.html

## 🐳 Docker 快速启动

每个项目都包含 Docker 支持，可以一键启动：

```bash
# 进入任意项目目录
cd nodejs-nestjs  # 或 python-fastapi 或 go-gin

# 启动服务（包含数据库）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📊 技术栈对比

| 特性 | NestJS | FastAPI | Gin |
|------|--------|---------|-----|
| **语言** | TypeScript | Python | Go |
| **性能** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **学习曲线** | 中等 | 简单 | 中等 |
| **类型安全** | 强 | 强 | 强 |
| **生态系统** | 丰富 | 丰富 | 丰富 |
| **部署** | 容器/云平台 | 容器/云平台 | 单二进制文件 |
| **适用场景** | 企业应用 | AI/ML集成 | 高并发服务 |
| **开发速度** | 快 | 非常快 | 快 |
| **内存占用** | 中 | 中 | 低 |

## 🎓 学习路径

### 前端工程师转后端建议

如果你主要做前端开发，建议学习顺序：

1. **首选 NestJS** (Node.js + TypeScript)
   - 与前端技术栈相似
   - TypeScript 语法熟悉
   - npm 生态系统熟悉
   - 容易理解和上手

2. **进阶 FastAPI** (Python)
   - 语法简洁易学
   - 适合数据处理和 AI 集成
   - 开发效率高

3. **高级 Gin** (Go)
   - 学习编译型语言
   - 理解高性能服务设计
   - 掌握并发编程

## 📖 API 文档

每个项目都提供完整的 API 文档：

- **NestJS**: http://localhost:3000/api/docs
- **FastAPI**: http://localhost:8000/api/docs
- **Gin**: http://localhost:8080/swagger/index.html

## 🔐 默认 API 端点

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

## 🛠️ 开发工具推荐

### 通用工具
- **API 测试**: Postman, Insomnia, HTTPie
- **数据库管理**: pgAdmin, DBeaver, TablePlus
- **容器管理**: Docker Desktop, Portainer
- **版本控制**: Git

### 各技术栈专用工具

**NestJS**:
- VSCode + TypeScript 扩展
- ESLint + Prettier
- Jest (测试)

**FastAPI**:
- VSCode/PyCharm
- Black (格式化)
- Pytest (测试)

**Go**:
- VSCode + Go 扩展 / GoLand
- Air (热重载)
- golangci-lint (代码检查)

## 📝 环境变量配置

每个项目都需要配置 `.env` 文件，主要配置项：

- `PORT` - 服务端口
- `DATABASE_URL` - 数据库连接
- `JWT_SECRET` - JWT 密钥
- `CORS_ORIGINS` - 跨域配置

详细配置请查看各项目的 `.env.example` 文件。

## 🧪 测试

```bash
# NestJS
cd nodejs-nestjs
pnpm run test

# FastAPI
cd python-fastapi
pytest

# Go
cd go-gin
go test -v ./...
```

## 📦 生产部署

### 推荐部署方式

1. **Docker 容器化部署** (推荐)
   - 使用 `docker-compose` 或 Kubernetes
   - 配置环境变量
   - 设置健康检查

2. **云平台部署**
   - AWS (ECS, Lambda)
   - Google Cloud (Cloud Run)
   - Azure (App Service)
   - 阿里云/腾讯云

3. **传统服务器**
   - Nginx 反向代理
   - PM2/Supervisor/Systemd 进程管理
   - 配置 HTTPS

## 🔒 安全建议

1. 使用强 JWT 密钥（至少 32 字符）
2. 启用 HTTPS
3. 配置合适的 CORS 策略
4. 实施请求限流
5. 定期更新依赖
6. 使用环境变量管理敏感信息
7. 实施日志监控
8. 数据库连接使用密码认证

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT

## 🙋 常见问题

**Q: 我应该选择哪个技术栈？**
A: 如果你是前端工程师，推荐从 NestJS 开始。如果需要高性能，选择 Go。如果做数据分析或 AI，选择 FastAPI。

**Q: 可以同时学习多个吗？**
A: 建议先精通一个，再学习其他的。基础的 REST API 概念是相通的。

**Q: 生产环境使用哪个？**
A: 三个都可以用于生产环境。NestJS 适合企业应用，FastAPI 适合快速迭代，Gin 适合高并发场景。

**Q: 如何切换数据库？**
A: 修改 ORM 配置和连接字符串即可。代码层面改动较小。

## 📞 联系方式

如有问题，欢迎提 Issue 或联系维护者。

---

**祝你开发愉快！🎉**

