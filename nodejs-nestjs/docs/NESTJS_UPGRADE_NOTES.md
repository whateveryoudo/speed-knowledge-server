# NestJS 11 升级说明与踩坑记录

本文记录 `nodejs-nestjs` 从 Nest 10 升级到 Nest 11 时的依赖变更、编译报错处理，以及 Socket.IO WebSocket 升级失败的根因与修复方式。

---

## 1. 依赖升级清单

升级原则：**所有 `@nestjs/*` 核心包保持同一主版本（11.x）**，避免混用 10/11 导致 WebSocket 适配器行为异常。

| 包名 | 升级前 | 升级后 |
|------|--------|--------|
| `@nestjs/common` / `core` / `platform-express` | 10.x | **11.1.27** |
| `@nestjs/jwt` | 10.x | **11.0.2** |
| `@nestjs/passport` | 10.x | **11.0.5** |
| `@nestjs/platform-socket.io` / `websockets` | 10.x / 11.1.19 | **11.1.27** |
| `@nestjs/config` | 3.x | **4.0.x** |
| `@nestjs/swagger` | 7.x | **11.x** |
| `@nestjs/cache-manager` | 2.x | **3.x** |
| `@nestjs/cli` / `schematics` / `testing` | 10.x | **11.x** |

### Cache 模块额外变更

`@nestjs/cache-manager` v3 不再支持 `cache-manager` v5 和 `cache-manager-ioredis-yet`，需迁移到 **Keyv**：

```diff
- "cache-manager": "^5.x"
- "cache-manager-ioredis-yet": "^2.x"
+ "cache-manager": "^6.x"
+ "@keyv/redis": "^4.x"
+ "keyv": "^5.x"
```

`app.module.ts` 配置从 `store: await redisStore(...)` 改为：

```typescript
import { createKeyv } from '@keyv/redis';

CacheModule.registerAsync({
  isGlobal: true,
  useFactory: async () => ({
    stores: [createKeyv('redis://localhost:6379/0')],
  }),
}),
```

业务代码中 `@Inject(CACHE_MANAGER)` 和 `cacheManager.get/set/del` 用法不变。TTL 仍为**毫秒**。

> **注意**：Keyv 在 Redis 中的存储格式与旧版不同（`{ value, expires }` 结构）。升级后旧缓存 key 需自然过期或手动清理，不影响业务逻辑，但短期内可能出现缓存未命中。

---

## 2. 升级后编译报错（JWT 相关）

Nest 11 + `@nestjs/jwt` 11 + `@types/passport-jwt` 4 对类型更严格，`configService.get()` 返回 `string | undefined`，而 JWT 配置要求必填。

### 报错 1：`jwt.strategy.ts` — `secretOrKey`

```
Type 'string | undefined' is not assignable to type 'string | Buffer'
```

**修复**：使用 `getOrThrow`，缺失配置时启动即失败，而不是运行时才出错。

```typescript
// src/modules/auth/strategies/jwt.strategy.ts
secretOrKey: configService.getOrThrow<string>('JWT_SECRET'),
```

### 报错 2：`auth.module.ts` — `JwtModule.registerAsync`

```
signOptions.expiresIn: Type 'string | undefined' is not assignable to ...
```

**修复**：

```typescript
import { JwtModule, type JwtModuleOptions } from '@nestjs/jwt';

useFactory: (configService: ConfigService): JwtModuleOptions => ({
  secret: configService.getOrThrow<string>('JWT_SECRET'),
  signOptions: {
    expiresIn: configService.getOrThrow<string>('JWT_EXPIRES_IN')
      as NonNullable<JwtModuleOptions['signOptions']>['expiresIn'],
  },
}),
```

`expiresIn` 需要 `StringValue | number`（来自 `jsonwebtoken` / `ms` 包），普通 `string` 不能直接赋值，需类型断言。环境变量示例：`JWT_EXPIRES_IN=10080s`。

### 必配环境变量

```env
JWT_SECRET=...
JWT_EXPIRES_IN=10080s
```

---

## 3. WebSocket 升级失败（Socket.IO 一直 polling）

### 现象

- 前端控制台：`connected` 有输出，但 `socket.io.engine.transport.name === "polling"`
- DevTools Network：大量 `transport=websocket` 请求失败，响应头为空或 **400 Bad Request**
- 后端 Nest 日志：`joined room=user:2` 正常（polling 通道可用）

### 根因（与 Nest 版本无关）

项目在同一 HTTP 服务器（端口 3004）上挂载了**两套 WebSocket**：

| 路径 | 技术栈 | 用途 |
|------|--------|------|
| `/collaboration` | 原生 `ws` + Hocuspocus | 文档协同编辑 |
| `/socket.io` | Socket.IO + Nest Gateway | 通知推送 |

原先 `CollaborationGateway` 写法：

```typescript
// ❌ 错误写法
new WebSocketServer({ server, path: '/collaboration' });
```

`ws` 库会在 HTTP 的 `upgrade` 事件上监听**所有** WebSocket 升级请求。路径不是 `/collaboration` 时（例如 `/socket.io/...`），`ws` 不会放行，而是直接 `abortHandshake(socket, 400)` 关闭连接。

因此 Socket.IO 的 polling 握手能成功（普通 HTTP），但升级到 WebSocket 时被协作网关拦截。

可用 curl 快速验证：

```bash
curl -i --max-time 3 \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  "http://localhost:3004/socket.io/?EIO=4&transport=websocket"
```

修复前返回 `400 Bad Request`，修复后返回 `101 Switching Protocols`。

### 修复

使用 `noServer: true`，手动处理 upgrade，**只接管 `/collaboration`**，其他路径直接 `return` 交给 Socket.IO：

```typescript
// src/modules/collaboration/collaboration.gateway.ts
initialize(server: any) {
  this.wss = new WebSocketServer({ noServer: true });

  server.on('upgrade', (request, socket, head) => {
    const url = new URL(request.url, `http://${request.headers.host}`);
    if (url.pathname !== '/collaboration') {
      return; // 不处理，让 Socket.IO 接管
    }
    this.wss.handleUpgrade(request, socket, head, (ws) => {
      this.wss.emit('connection', ws, request);
    });
  });

  this.wss.on('connection', (ws, request) => {
    // ...
  });
}
```

### 为什么最初没排查出来

1. **polling 能连上**：通知功能通过长轮询可用，表面上"连接成功"，容易误判为版本问题。
2. **症状像 Nest 版本混用**：社区里 Socket.IO 降级到 polling 的常见原因确实是 `@nestjs/websockets` 版本不一致，优先排查了依赖，没有第一时间验证 HTTP upgrade 是否被拦截。
3. **`ws` 的默认行为不直观**：`{ server, path }` 模式会**主动拒绝**非匹配路径的 upgrade，而不是忽略它们——这是 `ws` 库的设计，需要阅读源码或文档才能发现。

### 同类问题预防

同一 HTTP Server 上挂多个 WebSocket 服务时：

- **推荐**：`noServer: true` + 在 `upgrade` 里按 `pathname` 分发
- **避免**：多个 `new WebSocketServer({ server, path: '...' })` 直接挂同一 server
- **新增 WebSocket 路径前**：用 curl 测 upgrade 是否返回 101

---

## 4. 前端 Socket.IO 客户端

```typescript
// apps/web/src/layouts/BasicLayout.vue
socket = io(`${import.meta.env.VITE_NOTIFICATION_URL}/notification`, {
  path: '/socket.io',
  auth: { token },
});
```

- `VITE_NOTIFICATION_URL` 指向 Nest 服务，如 `http://localhost:3004`
- namespace 为 `/notification`，与后端 `@WebSocketGateway({ namespace: '/notification' })` 对应
- 连接成功后 `transport.name` 应为 `websocket`

---

## 5. 生产环境（ECS + Nginx）补充

本地直连 Nest 端口时，修复协作网关后 WebSocket 即可正常升级。生产环境若通过 Nginx 反代，还需为 `/socket.io/` 配置 WebSocket 代理（与 `/collaboration` 类似）：

```nginx
location /socket.io/ {
    proxy_pass http://nestjs_upstream;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

缺少此配置时，生产环境会复现与本地类似的 polling 降级现象。

---

## 6. 升级后自检清单

- [ ] `pnpm install && pnpm run build` 无 TS 报错
- [ ] `.env` 中 `JWT_SECRET`、`JWT_EXPIRES_IN` 已配置
- [ ] 启动后 Redis 缓存读写正常（浏览计数、幂等拦截等）
- [ ] 前端控制台 `transport.name === 'websocket'`
- [ ] curl 测试 `/socket.io/?transport=websocket` 返回 101
- [ ] 协同编辑 `/collaboration` 连接正常
- [ ] 生产 Nginx 已配置 `/socket.io/` 代理（如适用）
