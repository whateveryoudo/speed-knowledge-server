# 空间 Host 隔离 & 后续调整清单

> 更新背景：组织子域 / 个人站共用一套后端；**当前空间由请求 Host 解析**，列表类接口不再依赖前端传 `space_id`。  
> 本文记录：**已完成项**、**接下来要改什么**、**Host 相关注意点**（本地 Vite + 生产 Nginx）。

---

## 1. 产品与数据层级（对齐语雀）

```text
Host 子域 → Space（空间）
  ├── 公共区（Knowledge.team_id IS NULL）
  └── Team（团队）
        └── Knowledge（知识库）
              └── Document
```

| 概念 | 路由/入口示例 | 列表过滤 |
|------|----------------|----------|
| 空间 | `ykxspace1.speed.localhost` | `Knowledge.space_id = 当前空间`（Host） |
| 公共区 | 侧栏「公共区」/ 预留页 | `space_id` + `team_id IS NULL` |
| 团队 | `/dashboard/team`、`/dashboard/team/:team_slug` | `space_id` + `team_id = 该团队` |
| 仪表盘「我的知识库」 | `/dashboard/knowledge` | 通常只要 `space_id`（公共区+各团队汇总） |

**团队列表不拆「我创建 / 被邀请」**（与知识库 `own|collaboration` 不同）；按「当前空间 + 我是成员」一条列表即可。

**知识库分组（group / book_stacks）**：个人货架 vs 团队货架结构类似，但归属不同；**分组表 owner 改造暂缓**，先打通空间隔离与团队页骨架。

---

## 2. 已完成（当前代码）

### 2.1 后端：按 Host 定空间 + 列表过滤

| 接口 | 行为 |
|------|------|
| `POST /knowledge/list` | `Depends(get_current_space)` → `space_id=space.id` |
| `POST /knowledge/mine/list` | 同上 |
| `GET /knowledge/common-pin/list` | join `Knowledge`，按 `space_id` 过滤 |
| `GET /space/current/access` | **仅 Host**（`get_space_by_host`），组织非成员 403 |
| Schema | `KnowledgeListQuery` / `Mine` 含可选 `team_id`、`only_public_area`；**不含** `space_id`（不交给前端传） |
| Service | `KnowledgeService._apply_space_scope` |

### 2.2 前端：Layout 空间 403

| 项 | 说明 |
|----|------|
| `GET /space/current/access` | 已登录 + 组织子域才调 |
| `BasicLayout` | 403 页内展示 `NoAuthPage`；邀请 / `guestEntry` 放行 |
| Vite | `changeOrigin: false`（保留浏览器 Host） |
| 环境 | `VITE_SPACE_ROOT_DOMAIN=speed.localhost` |

### 2.3 登录

组织空间成员校验在登录里 **已注释**（`assert_org_space_member`），准入交给 Layout `current/access`（更贴近语雀：能登录，进空间再 403）。

---

## 3. 接下来要调整（优先级）

### P0 — 巩固空间隔离（写接口 / 其它列表）

- [ ] **写接口组合 Depends**：需要「组织空间成员」的写操作挂 `require_org_space_member`（或复用 `assert_org_space_member` 的 Depends 版），**不要塞进 `get_current_user`**。
- [ ] 排查其它「当前工作台」列表是否仍跨空间：如 **知识库分组 list**、**dashboard 最近文档**、**团队 list**（仍靠 query `space_id` 的应改为 Host）。
- [ ] `create` 知识库：body 的 `space_id` 建议与 `get_current_space.id` 一致性校验，防伪造。

### P1 — 团队页打通（路由已留 `/dashboard/team`、`team/:team_slug`）

- [ ] `GET /team/list`：改为 `get_current_space`，按成员过滤；响应补 **成员数 / joined_at / role**（语雀列表列）。
- [ ] `GET /team/by_slug/{slug}`（或等价）：详情页用 slug，不要只用 id。
- [ ] 挂上 **软删团队** 路由（service 已有 `delete_team`）。
- [ ] 团队首页知识库：复用 `/knowledge/list` 或 `/mine/list`，传 `team_id`；**不新建知识库表**。
- [ ] 侧栏团队入口、团队列表页 UI。

### P2 — 公共区

- [ ] 固定路由（如 `/dashboard/org_wiki` 或现有菜单）+ list 传 `only_public_area=true`。

### P3 — 分组（book_stacks）owner 改造（暂缓）

- [ ] `knowledge_group` 增加 `owner_type` / `owner_id`，回填历史 `user → owner`。
- [ ] 个人：`/group/list` 仍 `owner=user`；团队：`owner=team`。
- [ ] **不要**在未改表前把个人 `user_id` 分组硬套到团队页。

### 前端其它

- [ ] 跨子域 **localStorage 不共享**；若要「登一次各子域通用」需 Cookie `Domain=.根域` 或 SSO（非当前必做）。
- [ ] 团队页复用「我的知识库」卡片/列表组件时，只换 `team_id` 参数。

---

## 4. Host 注意点（必读）

### 4.1 后端怎么解析空间

| Dep | 行为 | 用途 |
|-----|------|------|
| `get_space_by_host` | **只认 Host 子域**；无子域 → 404 | `current/access` 等「必须是组织上下文」 |
| `get_current_space` | 有子域 → 该组织空间；无子域 → **当前用户个人空间** | list / pin 等「当前工作台」 |

子域解析：`get_space_subdomain(host)`（`app/common/utils.py`）  
- `ykxspace1.speed.localhost:5173` → `ykxspace1`  
- `localhost` / IP → `None` → 走个人空间分支  

### 4.2 本地 Vite 代理（已踩坑）

`changeOrigin: true` 时，代理到 `localhost:8010` 会把 **Host 改成后端地址**，后端永远看到 `localhost`，组织过滤失效。

**正确（当前）：**

```ts
// apps/web/vite.config.mts
proxy: {
  [apiBaseUrl]: {
    target: apiProxyUrl,
    changeOrigin: false, // 保留浏览器 Host
    rewrite: (path) => path.replace(new RegExp(`^${apiBaseUrl}`), ''),
  },
},
```

备选：`changeOrigin: true` + 转发 `X-Forwarded-Host`，后端优先读该头（生产反代也可能需要）。

本地访问组织站示例：

```text
http://ykxspace1.speed.localhost:5173/dashboard
```

需：`VITE_SPACE_ROOT_DOMAIN=speed.localhost`；现代 Chrome 下 `*.localhost` 一般指向 127.0.0.1。

### 4.3 生产 Nginx

生产**不走 Vite proxy**。保证上游收到浏览器 Host：

```nginx
proxy_set_header Host $host;
# 若必须改写 Host，则额外：
# proxy_set_header X-Forwarded-Host $host;
```

后端若上了 `X-Forwarded-Host`，与本地方案 B 对齐。

### 4.4 安全约定

| 做法 | 说明 |
|------|------|
| ✅ `space_id` 由 Host / `get_current_space` 注入 | 列表、pin、access |
| ❌ 信任 body/query 里的 `space_id` 做唯一边界 | 可被伪造 |
| ✅ `team_id` / `only_public_area` 可作为**第二层**客户端条件 | 仍须落在当前 `space_id` 内 |
| ✅ 身份与空间授权分离 | `get_current_user` 不内置成员校验；需要时组合 Depends |

### 4.5 联调自检

1. 组织子域 Network → 后端日志 Host 应为 `ykxspace1.speed.localhost:xxxx`（不是裸 `localhost:8010`）。  
2. `/knowledge/list` 不应返回其它空间知识库。  
3. 非成员组织子域 → `/space/current/access` 403 → Layout `NoAuthPage`。  
4. 个人站（无子域）→ `get_current_space` 个人空间 → 列表仅为个人库。

---

## 5. 相关代码索引

| 位置 | 说明 |
|------|------|
| `app/core/deps.py` | `get_current_space` / `get_space_by_host` / `assert_org_space_member` |
| `app/common/utils.py` | `get_space_subdomain` |
| `app/api/v1/endpoints/space.py` | `GET /current/access` |
| `app/api/v1/endpoints/knowledge.py` | list / mine / common-pin |
| `app/services/knowledge_service.py` | `_apply_space_scope` |
| `app/services/knowledge_common_pin_service.py` | pin 按 space 过滤 |
| `apps/web/vite.config.mts` | `changeOrigin: false` |
| `apps/web/src/layouts/BasicLayout.vue` | 空间 403 |
| `apps/web/src/store/useSpaceStore.ts` | `checkSpaceAccess` |

---

## 6. 一句话

**空间靠 Host；团队/公共区靠可选第二层参数；分组 owner 改造往后放；本地/生产都要保证 Host（或 X-Forwarded-Host）别丢。**
