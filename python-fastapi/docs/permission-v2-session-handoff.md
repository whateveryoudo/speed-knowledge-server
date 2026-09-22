# 权限 V2：近期讨论与交接（迁移 / 语雀对齐 / 聚合 / 下一步）

> 更新时间：2026-09-21  
> 用途：汇总本阶段对话中已确认的结论、落地代码与建议下一步，便于续作。  
> 相关文档：
>
> - 架构设计：[permission-architecture-v2.md](./permission-architecture-v2.md)
> - 历史进度快照：[permission-v2-current-progress.md](./permission-v2-current-progress.md)
> - 库迁移状态：[permission-v2-db-migrate-status.md](./permission-v2-db-migrate-status.md)
> - 语雀产品对照：[yuque-permission-model-understanding.md](./yuque-permission-model-understanding.md)
> - 读取链路：[resource-read-path-understanding.md](./resource-read-path-understanding.md)

---

## 1. 本阶段目标回顾

```text
Expand → Migrate → Switch → Contract
```

本阶段实际完成到：

```text
✅ Expand（新表）
✅ Migrate（列回填 + Grant 从 collaborator 回填 + schema drift 收口）
✅ 鉴权内核可跑（个人库读写、邀请/审批链路已有）
✅ 知识库权限页「协作者聚合列表」只读 API（个人 / 团队 / 公共区）
→ Switch：前端停写旧 Collaborator，改接 V2 列表 / 邀请
→ 写接口：改角色、删人、文档聚合（未做）
→ Contract：删旧表旧列（很后）
```

---

## 2. 库迁移结论

### 2.1 已完成的 revision（顺序）

| Revision | 内容 |
| --- | --- |
| `f85b5aac6c6e` | Expand：ResourceGrant / Invitation / AccessRequest 等 |
| `254b5f4dcdb0` | 列回填：creator_id / visibility / scope_* 等 |
| `4a10a73e9538` | Collaborator → ResourceGrant 回填 |
| `e5a743231c72` | schema drift 收口（public_area_slug、可空列、collect 等） |

本地若表结构已手工对齐过，对该 revision 使用 `alembic stamp`，不要重复 `upgrade`。

### 2.2 回填原则（已确认）

- `collaborator(status=accepted)` → `USER` Grant
- 知识库 `creator_id` 兜底 creator Grant
- pending 协作者默认不迁（可后续单独迁 AccessRequest）
- 个人库场景不强制写 TEAM_ROLE / SPACE 范围 Grant

### 2.3 环境注意

- Settings 需要 `DEBUG`（或与 `.env` 字段名对齐），不要只写 `APP_DEBUG` 却读 `DEBUG`
- AI 路由受 `ENABLE_AI` 控制；开启需 `uv sync --group ai`（命令是 `uv sync`，不是 `uv run sync`）

---

## 3. 语雀对齐后的产品结论

官方对照：

- 个人版：知识库 → 文档（两层）
- 空间版：团队 → 知识库 → 文档（三层）

对本仓库权限页最关键的几条：

```text
1. 协作列表展示「角色组行 + 用户行」，不要默认展开成真人列表
2. 团队管理员（owner/admin）对知识库锁定「可管理」
3. 团队成员 / 只读可改，可改为无权限
4. 单独加人与组权限并存时鉴权「就高」
5. 公开性（visibility）管「路人」，不管协作者列表行数
6. 文档公开性可突破知识库；文档单独协作者无知识库权限
```

详细矩阵见 [yuque-permission-model-understanding.md](./yuque-permission-model-understanding.md)。

---

## 4. 核心模型怎么记

### 4.1 一张 Grant 在说什么

```text
谁（principal）在某资源上有什么角色（resource_role）
```

| 字段 | 含义 |
| --- | --- |
| `principal_type` | 主体类别：`user` / `team_role` / `space_role` / `space` |
| `principal_id` | 用户 ID / 团队 ID / 空间 ID |
| `principal_role` | 该类内身份；`user`/`space` 用 `none` 表示不再细分 |
| `resource_role` | 对资源的权限：`admin` / `edit` / `read` / `none` |
| `source` | 审计来源；**不参与鉴权计算** |

注意：

- `principal_role = none` ≠ 无权限  
- 无权限 = `resource_role = none`，或没有这条 Grant（列表可用「缺行展示 none」）

### 4.2 常见组合

| 场景 | principal_type | principal_role |
| --- | --- | --- |
| 某个用户 | `user` | `none` |
| 团队所有者 / 管理员 / 成员 / 只读 | `team_role` | `owner` / `admin` / `member` / `readonly` |
| 空间管理员基线 | `space_role` | `owner` / `admin` |
| 公共区空间成员可读 | `space_role` | `member` |
| 团队库「空间可见」 | `space` | `none` |

团队角色 Grant **按身份一条**，不是按人头一条。团队有多个管理员，库里仍只有一条 `team_role + admin`。

### 4.3 创建时默认写入

| 知识库类型 | 默认 Grant |
| --- | --- |
| 所有 | `USER(creator) → admin` |
| 团队库 | 另写 4 条 TEAM_ROLE：owner/admin→admin，member→edit，readonly→read |
| 公共区 | 另写 SPACE_ROLE owner/admin → admin |
| 个人库 | 通常只有 creator USER |

---

## 5. 公开性（visibility）设计取舍

### 5.1 已确认选择

**公开性物化成 Grant**（`source = visibility_policy`），换来：

```text
鉴权统一：principals → 命中 Grant → 就高 role → Ability
批量「我能访问的资源 id」主要靠查 Grant
```

代价是切换 visibility 时要 sync 增删对应政策行。

备选方案（visibility 只留字段、resolve 里补 read）也能做，但批量列举要 `grant ∪ knowledge.visibility` 双路径；当前已铺开 Grant 路径，**维持物化**。

### 5.2 与协作者列表的关系

```text
公开性 UI（详情 visibility）  ≠  协作者表行
```

切到「空间所有成员可访问」会写入政策 Grant，**协作者列表不应多出一行「空间成员假协作者」**（团队库的 `SPACE` 行要跳过；公共区的 `SPACE_ROLE+member` 则是语雀「空间成员」角色行本身，要展示）。

`public` 在 resolve 里直接补 read，通常不写 Grant，也不进「我的列表」全量扫描。

### 5.3 文档 inherit

文档能力 = 知识库能力 ∪ 文档自身能力。  
仅当文档 `visibility = inherit` 时，才带上知识库的 visibility 范围权限；文档可突破上级公开性。

批量文档当前多为「先候选再 `filter_readable_documents`」，不是完整的「从用户反查全部文档 id」。

---

## 6. 知识库协作聚合 API（已落地）

### 6.1 接口

```text
GET /api/v1/resource-collaboration/knowledge/{knowledge_id}
Query:
  keyword?: string          # 只搜用户行 / pending（用户名、昵称）
  resource_role?: read|edit|admin   # 权限列过滤；角色行和用户行都筛
```

代码位置：

- Schema：`app/schemas/resource_collaboration.py`
- Service：`app/services/resource_collaboration_service.py`
- Route：`app/api/v1/endpoints/resource_collaboration.py`
- 挂载：`app/api/v1/api.py` → prefix `/resource-collaboration`

权限：需能管理权限设置（`assert_can_manage_access_setting`）。

响应：直接 `list[ResourceCollaborationItem]`（不外包装 visibility；公开性走知识库详情）。

### 6.2 各类型知识库返回什么

| 类型 | 角色组行 | 用户行 | pending |
| --- | --- | --- | --- |
| 个人库 | 无 | 有（创建者 locked） | 有 |
| 团队库 | 团队管理员(owner+admin 合成, locked) / 成员 / 只读 | 有 | 有 |
| 公共区 | 空间管理员(owner+admin 合成, locked) / 空间成员 / 外部联系人 | 有 | 有 |

说明：

- 库内 TEAM_ROLE 仍是 4 条 Grant（含 owner）；列表展示合并成 3 行（管理员一行）
- 成员/只读/外部无 Grant 时仍展示行，`resource_role = none`
- 合并管理员行 `grant_id = null`（展示用，改库不要用这一行的 principal 去删）

### 6.3 过滤约定

- `keyword`：只过滤 `row_type in (user, pending)`；角色组行保留
- `resource_role`：所有行按权限列过滤
- `query: ResourceCollaborationQuery = Depends()` 在当前 FastAPI 版本可摊成 query 参数（项目内 access-request 同款写法）

### 6.4 本接口明确不做

- 改角色 / 删人 / 退出协作（写接口未做）
- 文档权限聚合（建议后续 `list_document_collaborations`，可共 service）
- 人数统计如「团队成员(1人)」（需要另查 TeamMember / SpaceMember）

---

## 7. 文档树与权限裁剪（旁路结论）

知识库文档树：`get_document_tree_nodes` 会过滤不可读文档节点；目录节点仍返回。  
库内 `prev_id` / `next_id` **不因权限重写**；无权限用户看到的是断链子集，前端有兜底排序。关权限再开，节点回到原位置。这是已存在行为，与聚合 API 独立。

---

## 8. 前端现状

权限页仍走旧链路：

- `useCollaborator` → `collaboratorApi.getCollaboratorList`
- 邀请 token 也仍偏旧 collaborator / invitation 形态

V2 已有但前端未切：

- `/resource-invitation`
- `/access-request`
- `/resource-collaboration/knowledge/{id}`

本地前端曾卡在包导出：`speed-components-ui-dev/debug`、`speed-tiptap-editor/components` 等与 `package.json` exports 不一致，需先跑通再联调。

---

## 9. 建议下一步（按优先级）

### P0：把列表验通（后端 Swagger 即可）

1. 个人库：只有创建者用户行，`locked=true`
2. Swagger 建团队 → 建团队知识库 → 见团队三角色行
3. 组织空间下建公共区知识库 → 见空间三角色行
4. 切 visibility=space → 公共区「空间成员」变为 read；切回 private → 成员行 none
5. `keyword` / `resource_role` 过滤

### P1：前端最小联调

```text
1. 前端能启动
2. 权限页列表改打 V2 聚合（先个人库只读展示）
3. 公开性继续用知识库详情 visibility
4. 暂不接改角色 / 删人
```

可选：补「创建空间 / 创建团队」简单入口造数据（后端 CRUD 已有，不必先做完整管理后台）。

### P2：写能力与文档

- 改角色组 / 用户角色、移除用户、退出协作
- 文档协作聚合
- 邀请/审批前端切 V2，停写旧 Collaborator

### P3：很后

- Contract 删旧表旧列
- 团队上级能力开关下发、列表「人数」等体验项

---

## 10. 一句话状态

```text
鉴权内核 + 迁移 + 知识库协作者只读聚合：可用
公开性物化 Grant：刻意保留
前端仍旧 Collaborator：待 Switch
改角色/删人/文档聚合：未做
```

续作时优先：Swagger 验三种知识库列表 → 前端跑通 → 权限页接聚合只读 → 再写改删。
