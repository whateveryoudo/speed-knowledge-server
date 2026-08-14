# 权限架构 V2 改造交接说明

> 用途：新会话开始时，先完整阅读本文，再检查当前 Git 工作区和实际代码。  
> 原则：本文记录已经确定的架构结论和实施顺序；实际代码状态以工作区为准，不根据旧对话猜测。

## 1. 项目与协作方式

后端项目：

```text
/Volumes/ykxDrive/gitee/speed-knowledge-server/python-fastapi
```

前端项目：

```text
/Volumes/ykxDrive/gitee/speed-knowledge-client
```

协作约定：

- 用户手动修改后端，以熟悉 Python、Repository 分层和权限业务。
- Codex 负责审查实际代码、指出文件和行号、按阶段给出可粘贴代码。
- 未明确要求时，Codex 不直接修改业务代码。
- 本次允许整体重新设计，不要求兼容旧 `Collaborator` 架构。
- 但是改造期间应按阶段收口，不能同时留下多个半成品模块。
- 每次给代码前必须重新读取工作区，不能依赖旧聊天中的变量名或假定用户已完成某一步。

## 2. 已确定的总体领域模型

### 2.1 资源权限域

```text
ResourceInvitation
        │
        ├── 无需审批 ──→ ResourceGrant
        │
        └── 需要审批 ──→ ResourceAccessRequest
                              │
                              └── approved → ResourceGrant
```

职责：

```text
ResourceInvitation
= 知识库/文档邀请链接配置

ResourceAccessRequest
= 知识库/文档访问申请及单步审批历史

ResourceGrant
= 当前已经生效的资源授权
```

资源角色：

```text
ResourceRole.ADMIN
ResourceRole.EDIT
ResourceRole.READ
ResourceRole.NONE
```

### 2.2 组织成员域（后续阶段，当前不要实现）

```text
MembershipInvitation
        │
        ├── 无需审批 ──→ SpaceMember / TeamMember
        │
        └── 需要审批 ──→ MembershipJoinRequest
                              │
                              └── approved
                                    ├── SpaceMember
                                    └── TeamMember
```

不为空间和团队分别创建两套邀请申请表。组织成员域共用：

```text
MembershipInvitation
MembershipJoinRequest
```

使用 `target_type=space/team` 区分目标。

资源邀请和成员邀请不共表，因为审批通过后的落地结果不同：

```text
资源邀请 → ResourceGrant
成员邀请 → SpaceMember / TeamMember
```

### 2.3 权限组和能力

角色到能力的配置机制继续共用：

```text
PermissionGroup
└── PermissionAbility
```

但后续需要泛化现有字段：

```text
PermissionGroup.resource_role → role_key
PermissionGroup.target_type   → scope_type
PermissionGroup.target_id     → scope_id
PermissionAbility.enable      → enabled
```

支持作用域：

```text
space
team
knowledge
document
```

角色枚举仍按语义分开：

```text
SpaceMemberRole
TeamMemberRole
ResourceRole
```

能力枚举也分开：

```text
SpaceAbility
TeamAbility
KnowledgeAbility
DocumentAbility
```

数据库中的 `role_key`、`ability_key` 使用字符串；Service 根据 `scope_type` 使用对应 Python Enum 校验。

## 3. 审批单规则

`ResourceAccessRequest` 是轻量单步审批，不是通用工作流引擎：

```text
申请 → pending
同意 → approved + 写 ResourceGrant
拒绝 → rejected
取消 → cancelled
```

历史规则：

- 只复用当前 `pending` 申请。
- `approved/rejected/cancelled` 保留历史。
- 已结束后重新申请，应创建新的审批单。

MySQL 并发幂等：

```text
pending_key = resource_type:resource_id:applicant_user_id
```

- 仅 pending 时 `pending_key` 有值。
- 审批结束后把 `pending_key` 设为 `NULL`。
- 唯一约束保证同一个用户对同一资源同时只有一条 pending。
- `begin_nested() + flush() + 捕获唯一键冲突` 用于并发补偿。

`invitation_id` 表示申请来源于哪个邀请配置。申请单必须保存 `requested_role` 快照，后续修改邀请链接角色不能影响已经提交的申请。

## 4. 权限页聚合

权限页不是直接对应一张表，而是聚合：

```text
ResourceGrant
+
ResourceAccessRequest(status=pending)
```

- 已通过申请只显示 Grant，不重复显示 Request。
- rejected/cancelled 不显示在当前权限页，可出现在审批历史。
- 前端可以使用统一的聚合响应，但后端数据仍保持授权与审批分离。

## 5. Repository 分层规则

目标分层：

```text
Endpoint
- HTTP 参数、Depends、当前用户、commit/rollback、响应
        ↓
Service
- 业务规则、状态变化、跨 Repository 编排
        ↓
Repository
- db.query/filter/join/joinedload/锁/add/delete/flush
        ↓
Model
```

明确规则：

- Service 最终不出现 `db.query/filter/join/joinedload/with_for_update`。
- Service 可以持有 Session，并可使用 `begin_nested()` 做并发事务编排。
- Repository 不抛 `HTTPException`。
- Repository 不返回 Pydantic Response。
- Repository 不做权限或业务决策。
- Service 可以修改 Repository 返回的 ORM 对象属性。
- Repository 可以 `flush()`，但不能 `commit()`。
- Endpoint 负责 `commit()/rollback()`。
- 暂不引入 UnitOfWork。
- 不按 Model 数量机械创建 Repository，而按业务聚合和查询边界划分。

## 6. Repository 最终规划

资源域：

```text
KnowledgeRepository
DocumentRepository
ResourceGrantRepository
ResourceAccessRequestRepository
ResourceInvitationRepository
PermissionRepository
```

组织域（后续）：

```text
SpaceRepository
SpaceMembershipRepository
SpaceDepartmentRepository
TeamRepository
TeamMembershipRepository
```

不要创建抽象的通用 `MembershipRepository`。

## 7. 空间通讯录与部门（仅记录未来设计）

由于空间存在部门、外部联系人和离职人员，不能把所有逻辑塞进 `SpaceRepository`。

建议维度：

```text
SpaceMember.role
= owner/admin/member

SpaceMember.member_type
= internal/external

SpaceMember.status
= active/left
```

部门结构：

```text
SpaceDepartment
- space_id
- parent_id（部门树）

SpaceDepartmentMember
- department_id
- space_member_id
```

当前 `TeamMember.dept_id -> SpaceDept` 的方向不合理，未来应删除。部门属于空间通讯录成员，不属于某一条团队成员关系。

空间成员正常离开建议使用显式 `status=left` 保留离职记录，而不是复用知识库/文档回收站的软删除 Mixin。

## 8. 已确定的实施顺序

必须严格按以下顺序推进。

### 阶段一：Repository 基础层与现有错误修复

检查并稳定：

```text
BaseRepository
KnowledgeRepository
DocumentRepository
ResourceGrantRepository
ResourceAccessRequestRepository
ResourceInvitationRepository
PermissionRepository（暂时维持现有字段）
```

当前已发现问题：

- `PermissionRepository` 曾错误导入不存在的 `app.models.permission.Permission`。
- `PermissionAbility` 正确外键字段是 `permission_group_id`，不是 `group_id`。
- 当前 `space_member_repository.py` 曾错误使用不存在的 `Membership` Model；现阶段不要开展 Space Repository，应删除该半成品文件，未来重新实现 `SpaceMembershipRepository`。
- `PermissionAbility.permission_group` 的 many-to-one 关系不应设置 `cascade="all, delete"`；级联应放在 `PermissionGroup.abilities`，使用 `cascade="all, delete-orphan"`。

### 阶段二：完成资源权限链路

顺序：

```text
2.1 ResourceAccessRequestService 接入 Repository
2.2 ResourceGrantService 接入 Repository
2.3 Invitation 正式改名为 ResourceInvitation 并接入 Repository
2.4 完成资源邀请和审批路由
```

### 阶段三：泛化 PermissionGroup / PermissionAbility

资源邀请链路稳定后，才改：

```text
target_type   → scope_type
target_id     → scope_id
resource_role → role_key
enable        → enabled
```

该阶段必须同时修改 Model、Repository、Schema、PermissionGroupService、PermissionAbilityService 和默认能力初始化，不可只改字段。

### 阶段四：重写 PermissionService

目标入口：

```text
resolve_effective_role
resolve_effective_abilities
assert_can_read
assert_can_edit
assert_can_manage_access_setting
```

权限计算顺序：

```text
先判断身份/授权来源是否覆盖当前资源
→ 查找对应 PermissionGroup
→ 合并 enabled abilities
```

不能无条件 OR 空间、团队、知识库和文档能力。例如空间管理员不能自动进入未加入的私密团队。

### 阶段五：KnowledgeService / DocumentService

替换旧 `Collaborator` 和旧权限依赖，迁移查询到 Repository，统一调用新的 PermissionService。

### 阶段六：空间、团队、部门 Repository 与成员模型

到此阶段才开始：

```text
SpaceRepository
SpaceMembershipRepository
SpaceDepartmentRepository
TeamRepository
TeamMembershipRepository
```

### 阶段七：成员邀请与成员申请

新增：

```text
MembershipInvitation
MembershipJoinRequest
```

### 阶段八：聚合接口、迁移脚本、删除旧 Collaborator、调整前端

最后完成：

```text
权限页聚合接口
数据库 Migration
现有数据批处理脚本
删除 Collaborator Model/Service/Route
speed-knowledge-client 调整
```

## 9. 当前正在做的唯一任务

当前只做：

```text
ResourceAccessRequestService
    ↓
ResourceAccessRequestRepository
KnowledgeRepository
DocumentRepository
```

暂时不要做：

```text
ResourceGrantService 后续步骤
ResourceInvitation 改名
PermissionGroup 字段泛化
Space / Team / Department
MembershipInvitation / MembershipJoinRequest
```

当前 Service 构造器实际采用的实例名是：

```python
self.request_repository = ResourceAccessRequestRepository(db)
```

本阶段固定使用这个名字，不再无理由改成：

```text
self.access_request_repository
self.resource_access_request_repository
```

对应 Repository 已存在的方法：

```text
get_by_id
get_pending
list_pending_by_resource
paginate_by_resource
paginate_by_applicant
```

Service 应迁移的方法：

```text
get_by_id
get_pending_request
get_requests_by_resource
get_requests_by_applicant
_get_resource
```

`ensure_pending_request` 中创建对象改用：

```python
self.request_repository.add(access_request)
self.request_repository.flush()
```

审批状态更新后的 flush 也统一使用：

```python
self.request_repository.flush()
```

本阶段完成标准：

```bash
rg -n "db\.query|joinedload|paginate_query|PaginationQuery" \
  app/services/resource_access_request_service.py
```

结果应为空；允许保留：

```python
self.db = db
with self.db.begin_nested():
```

## 10. 当前工作区特别提醒

上次读取时，`ResourceAccessRequestService` 正处于手动修改一半的状态，存在实例变量不一致和未完成代码，不能直接运行：

```python
self.request_repository = ResourceAccessRequestRepository(db)
```

但部分方法错误使用了：

```python
self.resource_access_request_repository
```

`get_requests_by_resource()` 也处于未完成的括号和旧代码混合状态。

新会话必须先完整读取以下两个文件，基于实际内容给出修复，不要继续叠加片段：

```text
app/services/resource_access_request_service.py
app/repositories/resource_access_request_repository.py
```

建议新会话的第一条请求：

```text
请先完整阅读 docs/permission-refactor-handoff.md，随后审查当前
ResourceAccessRequestService 和 ResourceAccessRequestRepository。
不要修改文件，先给我这一步的完整替换代码；实例变量固定使用
self.request_repository，不要推进到后续阶段。
```

