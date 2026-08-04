# 权限架构 V2 改造说明

## 1. 改造目标

当前权限体系主要围绕个人知识库设计，`Collaborator` 同时承担了以下职责：

- 用户在知识库或文档上的角色；
- 邀请加入后的协作记录；
- 待审批和已通过状态；
- 实际权限判断的数据来源。

V2 需要支持“个人空间、空间公共区、团队”三类知识库归属，并将邀请、审批、有效授权和资源能力拆分，避免一个协同表同时表达多个不同概念。

本次改造不改变已有的资源能力设计：每个知识库或文档仍然拥有自己的一套角色能力配置，以支持在权限高级设置中自定义某个资源的 `admin/edit/read` 能力。

## 2. 资源归属

知识库归属由 `space_id` 和可空的 `team_id` 表达：

| 场景 | Space 类型 | team_id | 路由作用域 |
| --- | --- | --- | --- |
| 个人知识库 | `personal` | `NULL` | 创建者用户名 |
| 空间公共区 | `organization` | `NULL` | `space.public_area_slug` |
| 团队知识库 | `organization` | 非空 | `team.slug` |

个人空间不是一个特殊团队，不再通过创建默认 Team 来模拟。

## 3. V2 核心模型职责

### 3.1 ResourceGrant：已生效授权

`ResourceGrant` 只表达一个事实：

> 哪个被授权对象，在某个资源上，获得了什么资源角色。

核心字段：

```text
resource_type     knowledge / document
resource_id       资源 ID
principal_type    user / space_role / team_role
principal_id      用户、空间或团队 ID
principal_role    none / owner / admin / member / readonly / external
resource_role     admin / edit / read
source            creator / default_policy / direct / invitation
created_by        授权操作人
```

其中主体类型含义如下：

| principal_type | 含义 | principal_id | principal_role |
| --- | --- | --- | --- |
| `user` | 某个具体用户 | `User.id` | 固定为 `none` |
| `space_role` | 某空间中的一类成员 | `Space.id` | 空间成员角色 |
| `team_role` | 某团队中的一类成员 | `Team.id` | 团队成员角色 |

`ResourceGrant` 不保存待审批状态，也不保存具体能力明细。

### 3.2 PermissionGroup / PermissionAbility：资源能力策略

这部分继续保留，并从旧 `CollaboratorRole` 调整为 `ResourceRole`。

每个知识库初始化三条角色策略：

```text
knowledge K + admin -> 多条能力
knowledge K + edit  -> 多条能力
knowledge K + read  -> 多条能力
```

不同知识库中同一个角色的能力可以不同。例如：

```text
knowledge A + edit -> export_book = true
knowledge B + edit -> export_book = false
```

建议为 `PermissionGroup` 增加唯一约束：

```text
(target_type, target_id, resource_role)
```

概念上可以将它们理解为：

```text
PermissionGroup   = ResourceRolePolicy
PermissionAbility = ResourceRoleAbility
```

初期可以保留原表名，降低无意义的数据库迁移成本。

### 3.3 Invitation：邀请链接配置

`Invitation` 只保存邀请链接本身的规则：

```text
resource_type
resource_id
inviter_id
token
offered_role
need_approval
status
```

建议统一修正旧字段命名：

```text
invitate_user_id -> inviter_id
invitate_type    -> resource_type
role             -> offered_role
knowledge_id/document_id -> resource_type/resource_id
```

### 3.4 ResourceAccessRequest：访问申请

`ResourceAccessRequest` 保存一次具体用户申请及其审批状态：

```text
resource_type
resource_id
applicant_user_id
invitation_id
requested_role
status            pending / approved / rejected / cancelled
reviewed_by
reviewed_at
created_at
updated_at
```

`requested_role` 是申请提交时对 `Invitation.offered_role` 的快照。以后修改邀请链接角色，不应改变已经提交的申请。

待审批记录不参与实际权限判断。

## 4. 默认授权规则

### 4.1 所有知识库

知识库创建者始终获得直接用户授权：

```text
USER / creator_id / none -> admin
source = creator
```

这保证团队普通成员创建知识库后，即使团队成员默认只能 `edit`，创建者本人仍然是该知识库的管理员。

### 4.2 团队知识库

```text
TEAM_ROLE / team_id / owner    -> admin
TEAM_ROLE / team_id / admin    -> admin
TEAM_ROLE / team_id / member   -> edit
TEAM_ROLE / team_id / readonly -> read
```

添加团队成员时写入 `TeamMember`，不为每个知识库逐个创建用户 Grant。

### 4.3 空间公共区知识库

空间管理员授权始终保留：

```text
SPACE_ROLE / space_id / owner -> admin
SPACE_ROLE / space_id / admin -> admin
```

只有 `visibility = space` 时存在：

```text
SPACE_ROLE / space_id / member -> read
```

空间外部联系人默认无权访问公共区知识库。

### 4.4 直接用户授权

`USER ResourceGrant` 主要用于：

- 知识库创建者；
- 某个知识库的单独协作者；
- 某篇文档的单独协作者；
- 空间外部联系人的特定资源授权；
- 对空间或团队继承角色的额外提升。

多条授权同时命中时，取最高角色：

```text
admin > edit > read
```

直接授予较低角色不会削弱用户已经继承的较高角色。V2 暂不设计显式 deny 权限。

## 5. 可见性切换

空间公共区知识库的成员 Grant 随 `visibility` 同步：

```text
private/public -> space
创建 SPACE_ROLE/member -> read

space -> private/public
删除 SPACE_ROLE/member -> read
```

删除时按完整授权坐标定位：

```text
resource_type
resource_id
principal_type = space_role
principal_id   = knowledge.space_id
principal_role = member
```

不要根据 `GrantSource` 删除授权。`source` 只表示授权来源，不参与权限计算或生命周期判断。

空间成员可见产生的 Grant 使用：

```text
source = default_policy
```

不再需要 `GrantSource.VISIBILITY_POLICY`。

## 6. 有效角色解析

`ResourceGrantService.resolve_effective_role()` 负责取代旧的“查询 Collaborator.role”逻辑。

解析顺序不是优先覆盖，而是收集所有命中的角色后取最高值：

```text
当前用户
├── USER Grant
├── TeamMember.role -> TEAM_ROLE Grant
├── SpaceMember.role -> SPACE_ROLE Grant
└── 互联网公开产生的基础 read（仅访问判断）
        ↓
取最高 ResourceRole
```

邀请加入时应使用不包含互联网公开基线的 `resolve_granted_role()`。互联网公开允许访问，但不代表用户已经成为协作者。

## 7. 能力判断链路

V2 只替换“如何获得角色”，不改变资源能力判断方式。

旧链路：

```text
User
-> Collaborator.role
-> PermissionGroup(resource + role)
-> PermissionAbility
```

新链路：

```text
User
-> ResourceGrant Resolver
-> effective ResourceRole
-> PermissionGroup(resource + resource_role)
-> PermissionAbility
```

### 文档能力继承

文档仍保留现有的能力并集逻辑：

```text
最终文档能力
= 知识库角色对应的能力
OR 文档自身角色对应的能力
```

示例：

```text
用户在知识库拥有 edit，文档没有单独 Grant
-> 用户仍然可以编辑该文档

用户在知识库只有 read，某篇文档被单独授予 edit
-> 用户可以编辑该文档
```

团队和空间角色 Grant 不需要复制到每一篇文档。文档 Grant 主要记录文档级单独协作。

## 8. 邀请加入流程

邀请从旧 `collaborator` 路由拆出为独立路由：

```text
POST /invitations/join
```

为保持当前前端体验，请求包含：

```text
token
submit_request
apply_message
```

页面首次进入时：

```text
submit_request = false
```

处理结果：

```text
邀请不需审批
-> 直接创建 USER ResourceGrant
-> 返回 effective
-> 前端进入资源

邀请需要审批
-> 不创建 Request
-> 返回 approval_required 和资源信息
-> 前端显示申请页面
```

用户点击“申请加入”时：

```text
submit_request = true
-> 创建 ResourceAccessRequest(PENDING)
-> 返回 pending
```

接口应当幂等：

- 已有同等或更高的真实授权，直接返回 `effective`；
- 已有 pending 申请，直接返回 `pending`；
- 不重复创建相同的用户 Grant 或 pending Request；
- 互联网公开的游客 read 不视为已加入协作。

## 9. 审批流程

审批接口：

```text
POST /access-requests/{request_id}/approve
POST /access-requests/{request_id}/reject
POST /access-requests/{request_id}/cancel
```

同意时必须在同一事务中：

```text
Request: pending -> approved
+ 创建或更新 USER ResourceGrant
+ reviewed_by / reviewed_at
```

拒绝时：

```text
Request: pending -> rejected
+ reviewed_by / reviewed_at
```

审批时使用行锁或等价的并发控制，避免重复审批。

## 10. 权限页协作者列表

前端仍然可以显示一张统一的“协作者列表”，但后端由多个数据源组装。

团队知识库：

```text
团队角色目录 + TEAM_ROLE Grant + TeamMember 人数
+ ResourceAccessRequest(PENDING)
+ USER ResourceGrant
```

空间公共区：

```text
空间角色目录 + SPACE_ROLE Grant + SpaceMember 人数
+ ResourceAccessRequest(PENDING)
+ USER ResourceGrant
```

个人知识库：

```text
ResourceAccessRequest(PENDING)
+ USER ResourceGrant
```

没有 Grant 的角色组也可以在接口响应中补成 `resource_role = none`，用于前端展示“无权限”；数据库不保存 `NONE` Grant。

## 11. 路由拆分

建议最终拆分：

```text
app/api/v1/endpoints/
├── invitation.py
├── resource_access_request.py
├── resource_grant.py
└── resource_permission.py
```

路由职责：

```text
Invitation
GET   /invitations/{resource_type}/{resource_identifier}
PATCH /invitations/{invitation_id}
POST  /invitations/{invitation_id}/reset
POST  /invitations/join

ResourceAccessRequest
GET  /access-requests/{resource_type}/{resource_identifier}/pending/count
POST /access-requests/{request_id}/approve
POST /access-requests/{request_id}/reject
POST /access-requests/{request_id}/cancel

ResourceGrant
PATCH  /resource-grants/{grant_id}
DELETE /resource-grants/{grant_id}

ResourcePermission
GET /resource-permissions/{resource_type}/{resource_identifier}/subjects
```

旧 `collaborator.py` 在迁移完成后删除。

## 12. 推荐实施顺序

1. 将 `PermissionGroup.role` 从 `CollaboratorRole` 调整为 `ResourceRole`，保留资源能力表。
2. 完成通用 `resolve_effective_role()` 并接入 `PermissionService`。
3. 新增 `ResourceAccessRequest` 模型、Schema 和 Service。
4. 调整 `Invitation` 字段并实现 `POST /invitations/join`。
5. 实现申请批准、拒绝、取消接口。
6. 实现权限页统一 subjects 列表。
7. 迁移“我的知识库”、搜索、通知和退出协作逻辑。
8. 迁移文档级直接授权，保留知识库与文档能力 OR 合并。
9. 确认没有运行代码读取 `Collaborator` 后，再删除旧模型、枚举和接口。
10. 最后单独删除 `Knowledge.is_public` 等废弃数据库字段。

## 13. 数据迁移原则

旧 `Collaborator` 数据迁移：

```text
status = accepted
-> ResourceGrant(USER)

status = pending
-> ResourceAccessRequest(PENDING)
```

旧角色映射：

```text
CollaboratorRole.READ  -> ResourceRole.READ
CollaboratorRole.EDIT  -> ResourceRole.EDIT
CollaboratorRole.ADMIN -> ResourceRole.ADMIN
```

线上发布应采用“先加后删”：

1. 先增加新表和新字段；
2. 批量回填历史数据；
3. 校验新旧权限结果；
4. 发布只读取新架构的代码；
5. 观察稳定后，再单独删除旧表和旧字段。

不要在同一次上线中先删除旧字段再发布依赖新字段的代码。

## 14. 当前明确不做的设计

- 不使用 `ResourceGrant` 替代 `PermissionGroup/PermissionAbility`；
- 不把资源角色能力改成全局静态字典；
- 不给团队/空间每个成员、每个知识库复制用户 Grant；
- 不将 pending Request 参与权限计算；
- 不使用 `GrantSource` 判断有效权限；
- 暂不支持显式 deny 覆盖继承权限；
- 暂不为了旧接口兼容而保留重复业务模型。

