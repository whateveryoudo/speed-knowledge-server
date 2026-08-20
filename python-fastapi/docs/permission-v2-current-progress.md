# 权限 V2：当前进度与下一阶段计划

> 更新时间：2026-08-19  
> 说明：本文以当前工作区代码为准，记录 V2 的真实完成状态、已确认的业务结论和下一阶段顺序。  
> 相关历史设计见 [permission-architecture-v2.md](./permission-architecture-v2.md)；旧快照见 [permission-v2-migration-summary.md](./permission-v2-migration-summary.md)。

## 1. 当前目标与边界

本轮目标不是兼容旧 `Collaborator` 体系，而是完成一套可覆盖以下资源范围的 V2 权限内核：

```text
个人知识库 / 团队知识库 / 空间公共区
知识库 / 文档
直接协作者 / 团队角色 / 空间角色 / 公开范围
邀请链接 / 访问申请 / 审批
```

权限的职责分层已经固定：

```text
ResourceGrant
    = 已经生效的资源授权事实

PermissionGroup + PermissionAbility
    = 某个资源中 admin/edit/read 角色实际拥有的能力

ResourceInvitation
    = 邀请链接配置

ResourceAccessRequest
    = 访问申请及单步审批历史
```

邀请或审批记录不参与最终鉴权；只有 `ResourceGrant` 参与授权解析。

## 2. 已完成的部分

### 2.1 核心权限模型：约 80%

已完成：

- `ResourceGrant`、唯一约束、Repository、Grant 写入与删除；
- 用户直接授权、团队角色授权、空间具体角色授权、空间内部成员整体授权；
- 资源角色 `admin / edit / read` 与最高角色合并；
- 知识库创建者默认 `USER -> admin`；
- 团队知识库默认 `TEAM_ROLE` 授权；
- 公共区知识库默认 `SPACE_ROLE owner/admin -> admin`；
- Grant 冲突时使用保存点隔离唯一约束异常；
- 知识库单资源、批量资源角色解析；
- `PermissionGroup + PermissionAbility` 按资源独立配置角色能力；
- 路由依赖通过具体 Ability 鉴权，而非仅按角色判断。

当前主体语义：

| principal_type | 语义 |
| --- | --- |
| `USER + NONE` | 创建者、直接协作者、邀请/审批后生效的用户 |
| `TEAM_ROLE + role` | 团队成员角色继承 |
| `SPACE_ROLE + role` | 公共区的空间具体角色 |
| `SPACE + NONE` | 空间内部成员整体，排除 external |

### 2.2 邀请与审批：约 75%

已建立：

- `ResourceInvitation` Model / Schema / Service / Route；
- `ResourceAccessRequest` Model / Schema / Repository / Service / Route；
- 无审批邀请直接写入 `ResourceGrant`；
- 需要审批时创建 `pending` 申请；
- `pending_key` 唯一约束 + `begin_nested()` 实现同一用户同一资源的 pending 幂等；
- 审批通过、拒绝、取消；
- 审批通过后写入或保留更高的用户直接 Grant；
- 邀请链接角色修改不会改变已提交审批单的 `requested_role` 快照。

### 2.3 知识库 visibility：约 80%

已实现并纳入 Grant：

```text
团队知识库 visibility=space
→ SPACE + NONE -> read

公共区 knowledge visibility=space
→ SPACE_ROLE + member -> read

公共区 owner/admin
→ 始终保留 admin 基线
```

从 `space` 切离时，只删除对应的普通范围 Grant；不删除公共区空间 owner/admin 的管理授权。

### 2.4 文档可见范围：约 60%，仍需测试确认

已落代码：

- `DocumentVisibility` 已有 `inherit / private / space / public`；
- 新文档默认 `inherit`；
- 文档创建者拥有 `DOCUMENT + USER -> admin`；
- 文档 `space` 会写入文档自身 `SPACE + NONE -> read`；
- 文档 Ability 会合并知识库能力和文档自身能力；
- 文档 `private / space / public` 解析父知识库时会排除普通空间范围与父级公开入口；
- 团队角色、知识库直接协作者、公共区空间 owner/admin 仍继承；
- 文档读取与搜索已开始按文档 visibility 而非只看知识库 visibility 判断；
- 文档访问配置统一要求 `DOC_SHARE`，不再额外要求 `MODIFY_BOOK_PERMISSION`。

已通过语雀人工观察确认：

```text
团队成员权限会继承到文档，且文档协作者面板会展开显示团队成员。
公共区空间 owner/admin 是隐含管理权限，不必作为文档直接协作者存在。
```

仍未最终验证：

```text
父知识库为 space/public 时，文档 private 是否完全阻断普通空间成员/游客。
```

在该矩阵验证前，不应把文档 visibility 规则视为生产完成。

### 2.5 搜索与上下文用户：约 55%

已调整：

- 公开搜索只返回 `document.public`，或 `document.inherit + knowledge.public`；
- 登录态文档搜索在候选资源筛选后再调用 `can_read_document()`；
- 文档 `@` 候选在非 `inherit` 时过滤父知识库的普通空间范围 Grant。

当前搜索使用 `limit * 5` 取候选再在内存中过滤；安全性优先，后续应改为批量文档能力解析以保证精确分页和性能。

## 3. 当前未完成或不可发布部分

### 3.1 旧 Collaborator 链路仍是活跃代码

以下旧体系仍存在并被旧路由使用：

```text
app/models/collaborator.py
app/schemas/collaborator.py
app/services/collaborator_service.py
app/api/v1/endpoints/collaborator.py
Notification 中的 collaborator_id payload
Knowledge / Document / User 上的旧 relationship
```

风险：

```text
旧 Collaborator API 写 collaborator 表
V2 PermissionService 读取 ResourceGrant
=> 使用旧接口邀请成功，不等于获得 V2 权限
```

旧表与旧路由暂时不能删除，但新前端不能继续依赖它们。

### 3.2 协作者聚合接口尚未完成

当前工作区已有未完成的：

```text
app/schemas/resource_collaboration.py
```

其中 `ResourceCollaborationOverview(items=...)` 不符合当前决定，应删除这个额外包装层，改为项目统一分页响应：

```text
PaginationResponse[ResourceCollaborationListItem]
```

协作者列表必须聚合：

```text
ResourceGrant            已生效协作来源
ResourceAccessRequest    pending 审批用户
```

邀请链接配置不放入该列表；在用户打开链接邀请/高级设置弹框时单独读取 `ResourceInvitation`。

### 3.3 尚无迁移、回填、自动化测试

当前没有：

- 本次 V2 的 Alembic migration；
- 历史 Grant / 权限组 / 文档 visibility 的回填脚本；
- 数据核验脚本；
- 权限矩阵自动化测试；
- 前端 V2 接口迁移。

## 4. 当前完成量判断

| 范围 | 完成度 | 是否可交付 |
| --- | ---: | --- |
| 权限计算内核 | 80% | 仍需文档范围矩阵测试 |
| 知识库授权与 visibility | 75% | 仍需列表链路核验 |
| 文档授权与 visibility | 60% | 尚未完成业务矩阵测试 |
| 邀请与审批内核 | 75% | 旧协作者入口尚未切走 |
| 协作者页面读取接口 | 15% | 尚未实现聚合 Service / Route |
| 搜索与 `@` 候选 | 55% | 有临时性能方案 |
| 数据库迁移与回填 | 0% | 未开始 |
| 前端迁移 | 0% | 未开始 |
| 可部署 V2 | 约 25% | 不可部署 |

`python3 -m compileall -q app` 与 `git diff --check` 当前通过；这只说明语法和 diff 基本健康，不代表 API、数据库或权限语义已验收。

## 5. 下一阶段计划

### 阶段 1：收口文档权限规则（先做）

目标：让单资源读取、搜索、`@` 候选遵循相同的 visibility 规则。

1. 修正 `_is_visibility_scope_grant()`：只识别：

   ```text
   SPACE + none
   SPACE_ROLE + member/external
   ```

   不能将 `SPACE_ROLE + owner/admin` 过滤。

2. 验证以下账户矩阵：

   | 账户身份 | inherit | private | space | public |
   | --- | --- | --- | --- | --- |
   | 知识库直接协作者 | 读/写能力继承 | 应继承 | 应继承 | 应继承 |
   | 团队成员 / 只读成员 | 继承 | 应继承 | 应继承 | 应继承 |
   | 仅空间普通成员 | 按父知识库范围 | 待验证应拒绝 | 文档 read | 文档 public 不影响其登录权限 |
   | 空间 owner/admin（公共区） | admin | admin | admin | admin |
   | 游客 | 仅父级 public | 应拒绝 | 应拒绝 | read |

3. 核对文档目录树、历史记录、收藏、导出等所有文档入口，不能只修详情页与搜索页。

完成标准：同一用户对同一文档，无论从详情、搜索、目录或 API 读取，结果一致。

### 阶段 2：实现 V2 协作者列表聚合（随后做）

目标：为前端权限页提供唯一的 V2 列表读取契约。

1. 将 `ResourceCollaborationOverview` 改为 `ResourceCollaborationListItem`；
2. 新建 `ResourceCollaborationService`；
3. 新建 `GET /resource-collaborations/{resource_type}/{resource_id}`；
4. 先校验当前用户拥有对应资源的访问配置管理能力；
5. 展开 Grant：

   ```text
   USER Grant       -> 用户行
   TEAM_ROLE Grant  -> TeamMember 用户行
   SPACE_ROLE Grant -> SpaceMember 用户行
   SPACE + NONE     -> 空间内部成员用户行（排除 external）
   ```

6. 将 `pending` 的 `ResourceAccessRequest` 作为同一分页列表中的状态项混入；
7. 按“用户 + 来源”去重，避免一个用户同时是团队管理员、知识库协作者时被错误覆盖；
8. 继续保留来源文案，例如“知识库可编辑成员”“团队成员”“空间管理员”“等待审批”。

接口返回项目既有 `PaginationResponse`，不增加 `overview.items` 包装。

### 阶段 3：邀请配置与动作切换

目标：让新前端彻底不调用旧 `Collaborator` 写接口。

```text
协作者列表
GET /resource-collaborations/{resource_type}/{resource_id}

打开邀请链接弹框
GET /resource-invitations/{resource_type}/{resource_id}

创建邀请链接
POST /resource-invitations

修改邀请链接配置
PATCH /resource-invitations/{id}

加入、申请、审批
ResourceInvitationService + ResourceAccessRequestService
```

邀请配置不塞入协作者列表响应；它是弹框打开时的懒加载详情。

### 阶段 4：开发数据库迁移与历史回填

前提：阶段 1 至 3 已完成并通过手工 API 验收。

1. Alembic Expand migration：新表、字段、索引、唯一约束；
2. 文档 `visibility` 回填：旧 `is_public=1 -> public`，其余默认 `inherit`；
3. 重建每个知识库、文档的默认 PermissionGroup / PermissionAbility；
4. 回填创建者、团队角色、公共区空间 owner/admin、已接受旧协作者的 ResourceGrant；
5. 未接受旧协作者回填为 `ResourceAccessRequest` 历史，或按迁移策略丢弃；
6. 写幂等回填脚本和核验脚本；
7. 在生产数据副本演练，而非直接在生产库运行。

开发分支可清库重建；真实发布仍采用：

```text
Expand -> Migrate -> Switch -> Contract
```

### 阶段 5：启动后端、迁移前端

1. 在本地迁移后的数据库启动后端；
2. 用阶段 1 的账户矩阵和邀请审批流程验收 API；
3. 前端统一切换到 V2 协作者、邀请、审批和 visibility 接口；
4. 前后端联调通过后，旧前端停止调用旧 Collaborator API；
5. 稳定期后删除旧 Model / Schema / Service / Route / relationship / 表。

## 6. 当前建议的执行顺序

```text
修正当前文档范围小问题
    ↓
文档权限矩阵验收
    ↓
协作者列表聚合接口
    ↓
邀请动作切到 V2
    ↓
迁移脚本 + 数据核验
    ↓
启动本地 V2 后端
    ↓
前端整体迁移
    ↓
删除旧 Collaborator
```

在完成“协作者列表聚合 + 新邀请动作”之前，不进行正式数据迁移；否则前端仍可能写旧 `Collaborator` 表，而 V2 鉴权已经读取 `ResourceGrant`，会形成两套事实来源。
