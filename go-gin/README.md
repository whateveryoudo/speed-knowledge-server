# Go Gin API Server

基于 Gin 框架的高性能后端 API 服务器

## 技术栈

- **框架**: Gin
- **语言**: Go 1.21+
- **数据库**: PostgreSQL
- **ORM**: GORM
- **认证**: JWT
- **文档**: Swagger
- **热重载**: Air

## 功能特性

- ✅ RESTful API 设计
- ✅ JWT 身份认证
- ✅ 数据验证
- ✅ Swagger API 文档
- ✅ GORM 数据库集成
- ✅ 用户管理模块
- ✅ 密码加密
- ✅ 中间件支持
- ✅ CORS 支持
- ✅ 优雅关闭

## 快速开始

### 前置要求

- Go 1.21+
- PostgreSQL 14+
- Make (可选)

### 安装依赖

```bash
# 下载依赖
go mod download

# 整理依赖
go mod tidy
```

### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接和其他参数。

### 生成 Swagger 文档

```bash
# 安装 swag
go install github.com/swaggo/swag/cmd/swag@latest

# 生成文档
make swag
# 或
swag init -g cmd/server/main.go -o docs
```

### 运行应用

```bash
# 直接运行
make run
# 或
go run cmd/server/main.go

# 使用 Air 热重载（推荐开发环境）
# 先安装 air: go install github.com/cosmtrek/air@latest
make air
# 或
air

# 编译并运行
make build
./bin/server
```

### 访问应用

- API 服务: http://localhost:8080
- API 文档: http://localhost:8080/swagger/index.html
- 健康检查: http://localhost:8080/health

## 项目结构

```
.
├── cmd/
│   └── server/          # 应用入口
│       └── main.go
├── internal/            # 私有代码
│   ├── config/         # 配置
│   ├── database/       # 数据库
│   ├── dto/            # 数据传输对象
│   ├── handlers/       # HTTP 处理器
│   ├── middleware/     # 中间件
│   ├── models/         # 数据模型
│   ├── router/         # 路由
│   └── services/       # 业务逻辑
├── pkg/                # 公共库
│   └── utils/          # 工具函数
├── docs/               # Swagger 文档（自动生成）
├── .air.toml           # Air 配置
├── .env.example        # 环境变量示例
├── Dockerfile          # Docker 配置
├── docker-compose.yml  # Docker Compose 配置
├── Makefile            # Make 命令
└── go.mod              # Go 模块
```

## API 端点

### 健康检查
- `GET /` - 欢迎信息
- `GET /health` - 健康状态

### 认证
- `POST /api/v1/auth/login` - 用户登录

### 用户管理
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users` - 获取所有用户 (需要认证)
- `GET /api/v1/users/:id` - 获取单个用户 (需要认证)
- `PATCH /api/v1/users/:id` - 更新用户 (需要认证)
- `DELETE /api/v1/users/:id` - 删除用户 (需要认证)

## 开发指南

### Make 命令

```bash
make help          # 显示所有可用命令
make run           # 运行应用
make build         # 编译应用
make test          # 运行测试
make clean         # 清理编译产物
make swag          # 生成 Swagger 文档
make install       # 安装依赖
make lint          # 运行代码检查
make format        # 格式化代码
make docker-build  # 构建 Docker 镜像
make docker-up     # 启动 Docker 容器
make docker-down   # 停止 Docker 容器
make air           # 使用 Air 热重载
```

### 运行测试

```bash
# 运行所有测试
go test -v ./...

# 运行测试并查看覆盖率
go test -v -cover ./...

# 生成覆盖率报告
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

### 代码格式化

```bash
# 格式化代码
gofmt -s -w .

# 使用 goimports
goimports -w .

# 或使用 Make
make format
```

### 代码检查

```bash
# 安装 golangci-lint
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# 运行检查
golangci-lint run

# 或使用 Make
make lint
```

## 部署

### Docker 部署

```bash
# 构建镜像
make docker-build
# 或
docker build -t go-gin-api .

# 运行容器
docker run -p 8080:8080 --env-file .env go-gin-api

# 使用 docker-compose
make docker-up
# 或
docker-compose up -d

# 查看日志
make docker-logs
# 或
docker-compose logs -f
```

### 生产环境注意事项

1. 设置 `ENVIRONMENT=production`
2. 使用强密钥作为 `JWT_SECRET`
3. 配置正确的 CORS 策略
4. 启用 HTTPS
5. 配置适当的数据库连接池
6. 实施日志和监控
7. 使用反向代理（如 Nginx）
8. 设置适当的超时时间

### 推荐的生产环境配置

```bash
# 使用多个进程
./server &
./server &
./server &

# 或使用进程管理器（如 systemd, supervisor）
```

## 性能优化

- 使用连接池管理数据库连接
- 启用 GZIP 压缩
- 实现缓存策略
- 使用索引优化数据库查询
- 实现分页
- 使用 Goroutines 处理并发任务

## 工具推荐

- **热重载**: Air
- **代码检查**: golangci-lint
- **API 测试**: Postman, Insomnia
- **数据库管理**: pgAdmin, DBeaver
- **日志**: zap, logrus
- **监控**: Prometheus, Grafana

## 许可证

MIT

