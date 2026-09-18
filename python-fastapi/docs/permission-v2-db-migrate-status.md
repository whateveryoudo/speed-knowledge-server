# 权限 V2：数据库迁移现状与下一步

> 更新时间：2026-09-15  
> 范围：本地开发库的 Expand / Migrate 进度  
> 相关文档：[permission-v2-current-progress.md](./permission-v2-current-progress.md)、[permission-architecture-v2.md](./permission-architecture-v2.md)

## 1. 一句话结论

**结构 Expand 和「旧列 → 新列」回填已在本地跑通；鉴权真正依赖的 `resource_grant` 尚未从旧 `collaborator` 回填。**  
有存量数据时，下一步必须先做 Grant 回填，再启动后端用 Swagger 验收。

策略仍是：

```text
Expand → Migrate（列回填 → Grant 回填）→ Switch（业务只读 V2）→ Contract（删旧列/旧表）
```

**现在不要做 Contract**（不要删 `collaborator`、`user_id`、`is_public`、`enable`、`target_*` 等）。

---

## 2. 已完成

### 2.1 Expand：`f85b5aac6c6e`

文件：`alembic/versions/f85b5aac6c6e_v2_增加一些授权表.py`

| 动作 | 状态 |
| --- | --- |
| 新建 `resource_grant` | ✅ |
| 新建 `resource_invitation` | ✅ |
| 新建 `resource_access_request` | ✅ |
| `knowledge_base.visibility`（保留 `is_public`） | ✅ |
| `document_base.visibility`（保留 `is_public`） | ✅ |
| `knowledge_base.creator_id`（可空先加） | ✅ |
| `permission_groups.scope_type / scope_id / role_key`（可空先加） | ✅ |
| `permission_abilities.enabled`（保留旧 `enable`） | ✅ |
| 不删除旧表/旧列 | ✅ |

### 2.2 列回填：`254b5f4dcdb0`

文件：`alembic/versions/254b5f4dcdb0_v2_数据回填权限列.py`

| 动作 | 状态 |
| --- | --- |
| `creator_id ← user_id` | ✅ |
| 知识库 `is_public=1 → public`，否则 `private` | ✅ |
| 文档 `is_public=1 → public`，否则 `inherit` | ✅ |
| `permission_groups`：`target_* → scope_*`，`role → role_key` | ✅ |
| `permission_abilities.enabled ← enable` | ✅ |
| 收紧 `creator_id` / `scope_*` / `role_key` 为 NOT NULL | ✅ |

角色映射（已核对业务枚举，**当前脚本正确**）：

```text
CollaboratorRole / 旧 permission_groups.role
  1 → read
  2 → edit
  3 → admin

定义见：app/common/enums/collaborator.py
V2 字符串角色：app/common/enums/resource.py → ResourceRole
```

注意：曾有一版草稿写成 `1→admin、3→read`，那是错的。以仓库里现文件为准。

### 2.3 本地库现状（有存量）

- `collaborator` 表仍有历史数据（例如 `status=2` 已接受、`role=3` 管理员、`source=0` 创建者）。
- `resource_grant` 在列回填后通常仍为空或远少于协作者数。
- V2 鉴权读的是 `ResourceGrant`，不是 `collaborator`。

---

## 3. 未完成（Migrate 后半段）

| 项 | 状态 | 说明 |
| --- | --- | --- |
| `collaborator(status=已接受) → resource_grant` | ❌ | **下一步优先** |
| 知识库/文档创建者 Grant（`USER + none → admin`，source=creator） | ❌ | 防止 collaborator 漏 creator |
| 团队知识库 `TEAM_ROLE` 默认 Grant | ❌ | 有团队数据时需要 |
| 空间公共区 `SPACE_ROLE owner/admin` 基线 Grant | ❌ | 有公共区知识库时需要 |
| visibility 对应的范围 Grant（space/public） | ❌ | 按现有 `ResourceGrantService` 规则补 |
| pending 协作者 → `resource_access_request` | 可选 | 或迁移策略直接丢弃历史 pending |
| 默认 PermissionGroup / Ability 查漏补缺 | 视库而定 | 旧组若已按 knowledge/document 存在，可先核验再补 |
| 核验 SQL / 幂等脚本 | ❌ | Grant 回填后一并写 |
| Contract（删旧列） | 🚫 暂不做 | API + 前端稳定后再单独 revision |

---

## 4. 代码侧对照（方便排期）

已挂载的 V2 相关路由（`app/api/v1/api.py`）：

```text
/resource-invitation   邀请链接
/access-request        访问申请与审批
/resource              资源访问配置
```

仍存在的旧链路（不能当 V2 写入口）：

```text
collaborator Model / Service / Route
通知 payload 中的 collaborator_id
```

风险：

```text
旧 Collaborator API 写 collaborator 表
V2 PermissionService 读 ResourceGrant
=> 旧接口「邀请成功」≠ 获得 V2 权限
```

协作者列表聚合接口、前端整体切换，仍按总进度文档后续阶段做；**有存量数据时，数据库 Grant 回填应先于认真的 API 验收**。

---

## 5. 接下来干什么（推荐顺序）

### Step A：核验列回填（若还没查）

```sql
SELECT version_num FROM alembic_version;
-- 期望：254b5f4dcdb0

SELECT COUNT(*) FROM knowledge_base WHERE creator_id IS NULL;
SELECT role, role_key, COUNT(*) FROM permission_groups GROUP BY role, role_key;
SELECT visibility, COUNT(*) FROM knowledge_base GROUP BY visibility;
SELECT visibility, COUNT(*) FROM document_base GROUP BY visibility;
SELECT COUNT(*) FROM resource_grant;
SELECT status, COUNT(*) FROM collaborator GROUP BY status;
```

期望：

- 新列无脏 NULL（你已 NOT NULL）
- `role=3` 对应 `role_key='admin'`
- `resource_grant` 仍接近 0 → 进入 Step B

### Step B：手写下一份 Migrate（Grant 回填）

```bash
cd python-fastapi
alembic revision -m "v2 migrate backfill resource_grant from collaborator"
```

**只用 `revision -m`，不要 `--autogenerate`。**  
autogenerate 不会写 `INSERT`，还可能误生成 drop 旧列。

回填要点：

1. **只迁 `collaborator.status = 2`（ACCEPTED）**
2. 映射：

   ```text
   target_type              → resource_type
   COALESCE(knowledge_id, document_id) → resource_id
   user_id                  → principal_id（principal_type=user, principal_role=none）
   role 1/2/3               → resource_role read/edit/admin
   source 0/1/2             → creator / invitation / direct
   ```

3. 再补 `knowledge_base.creator_id` 的 creator Grant（`ON DUPLICATE KEY UPDATE` 保证幂等）
4. 有团队/公共区数据时，再按架构文档补 `TEAM_ROLE` / `SPACE_ROLE` / visibility 范围 Grant
5. `downgrade` 本地可先 `pass`，或只删本 revision 插入的 grant（按需）

### Step C：核验 Grant

```sql
SELECT resource_type, resource_role, source, COUNT(*)
FROM resource_grant
GROUP BY resource_type, resource_role, source;

-- 已接受协作者是否都有对应 user Grant（抽样）
SELECT c.id, c.user_id, c.target_type, c.role
FROM collaborator c
LEFT JOIN resource_grant g
  ON g.resource_type = c.target_type
 AND g.resource_id = COALESCE(c.knowledge_id, c.document_id)
 AND g.principal_type = 'user'
 AND g.principal_id = CAST(c.user_id AS CHAR)
WHERE c.status = 2
  AND g.id IS NULL;
```

期望：最后一条查询结果为 0 行（或仅有你主动排除的脏数据）。

### Step D：启动后端，Swagger 手工验收

1. 用存量账号访问其已协作的知识库/文档（应不再因无 Grant 被拒）
2. 走一遍：创建知识库 → 改 visibility → 邀请 → 申请 → 审批 → 再查权限
3. 重点路由：`/resource-invitation`、`/access-request`、知识库/文档读写接口

### Step E：业务 Switch（可与前端并行规划）

- 前端停写旧 Collaborator API
- 补协作者列表聚合接口（若产品页需要）
- 通知等仍依赖 `collaborator_id` 的链路逐步改掉

### Step F：Contract（最后）

单独 revision：删旧列/旧表。仅在 V2 读写稳定、旧入口下线后做。

---

## 6. 当前执行路线图

```text
✅ Expand（新表新列）
✅ Migrate-列回填（creator / visibility / scope / enabled）
→ ③ Migrate-Grant 回填（collaborator → resource_grant + 默认策略）  ← 你现在在这
→ ④ SQL 核验
→ ⑤ 启后端 + Swagger 验收
→ ⑥ 协作者聚合 API / 前端切 V2（Switch）
→ ⑦ Contract 删旧列（很后）
```

---

## 7. 进入 Docker MySQL（备忘）

```bash
# 容器名见 docker-compose：speed-knowledge-db
docker exec -it speed-knowledge-db mysql -uroot -p speed-knowledge
```

每条 SQL 必须以 `;` 结束；若提示符变成 `->`，说明语句未结束，补 `;` 或 `\c` 取消。

也可用 phpMyAdmin：默认 `http://localhost:8082`。

---

## 8. 角色对照速查

| 旧整数 `role` | 含义 | V2 `role_key` / `resource_role` |
| ---: | --- | --- |
| 1 | 只读 | `read` |
| 2 | 可编辑 | `edit` |
| 3 | 管理员 | `admin` |

| 旧 `source` | 含义 | V2 `source` |
| ---: | --- | --- |
| 0 | 创建者 | `creator` |
| 1 | 邀请 | `invitation` |
| 2 | 搜索加入等 | `direct` |

| 旧 `status` | 含义 | 回填去向 |
| ---: | --- | --- |
| 1 | pending | 可选 → `resource_access_request`，或丢弃 |
| 2 | accepted | → `resource_grant` |

---

## 9. 明确不做的事

- 不要 `alembic revision --autogenerate` 生成 Grant 回填
- 不要现在 drop `collaborator` / `is_public` / `user_id` / `enable` / `target_*`
- 不要假设「列回填完成 = 权限可用」；没有 Grant，V2 鉴权仍会失败
- 不要再把角色映射写成 `1=admin、3=read`
