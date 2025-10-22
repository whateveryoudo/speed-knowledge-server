# NestJS API Server

基于 NestJS 框架的后端 API 服务器

## 技术栈

- **框架**: NestJS 10
- **语言**: TypeScript
- **数据库**: PostgreSQL
- **ORM**: TypeORM
- **认证**: JWT + Passport
- **文档**: Swagger/OpenAPI
- **验证**: class-validator

## 功能特性

- ✅ RESTful API 设计
- ✅ JWT 身份认证
- ✅ 数据验证和转换
- ✅ Swagger API 文档
- ✅ TypeORM 数据库集成
- ✅ 用户管理模块
- ✅ 密码加密
- ✅ 全局异常处理
- ✅ CORS 支持

## 快速开始

### 前置要求

- Node.js 18+
- PostgreSQL 14+
- pnpm (推荐) 或 npm

### 安装依赖

```bash
# 使用 pnpm (推荐)
pnpm install

# 或使用 npm
npm install
```

### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接和其他参数。

### 运行应用

```bash
# 开发模式
pnpm run start:dev

# 生产模式
pnpm run build
pnpm run start:prod
```

### 访问应用

- API 服务: http://localhost:3000
- API 文档: http://localhost:3000/api/docs

## 项目结构

```
src/
├── modules/              # 功能模块
│   ├── users/           # 用户模块
│   │   ├── dto/         # 数据传输对象
│   │   ├── entities/    # 数据库实体
│   │   ├── users.controller.ts
│   │   ├── users.service.ts
│   │   └── users.module.ts
│   └── auth/            # 认证模块
│       ├── strategies/  # Passport 策略
│       ├── guards/      # 守卫
│       ├── dto/
│       ├── auth.controller.ts
│       ├── auth.service.ts
│       └── auth.module.ts
├── app.module.ts        # 根模块
├── app.controller.ts
├── app.service.ts
└── main.ts              # 应用入口
```

## API 端点

### 健康检查
- `GET /` - 欢迎信息
- `GET /health` - 健康状态

### 认证
- `POST /auth/login` - 用户登录

### 用户管理
- `POST /users` - 创建用户
- `GET /users` - 获取所有用户
- `GET /users/:id` - 获取单个用户
- `PATCH /users/:id` - 更新用户
- `DELETE /users/:id` - 删除用户

## 开发指南

### 创建新模块

```bash
nest g module modules/[module-name]
nest g controller modules/[module-name]
nest g service modules/[module-name]
```

### 运行测试

```bash
# 单元测试
pnpm run test

# e2e 测试
pnpm run test:e2e

# 测试覆盖率
pnpm run test:cov
```

### 代码格式化

```bash
# 格式化代码
pnpm run format

# 检查代码质量
pnpm run lint
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t nestjs-api .

# 运行容器
docker run -p 3000:3000 --env-file .env nestjs-api
```

### 生产环境注意事项

1. 设置 `NODE_ENV=production`
2. 使用强密码作为 `JWT_SECRET`
3. 设置 `DB_SYNCHRONIZE=false`，使用数据库迁移
4. 配置正确的 CORS 策略
5. 启用 HTTPS
6. 设置日志级别
7. 配置监控和告警

## 许可证

MIT

