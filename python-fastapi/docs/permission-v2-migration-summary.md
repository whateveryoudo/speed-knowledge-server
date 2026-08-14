# 权限 V2 当前迁移总结

> 更新时间：2026-08-14  
> 用途：记录权限 V2 当前真实进度、尚未迁移的调用链和下一阶段顺序。  
> 注意：本文是阶段快照。继续开发前，应先读取本文，再以当前工作区代码为准重新审查。

## 1. 本次重构的性质

这不是普通字段调整，而是一次权限领域重构，涉及：

```text
权限主体
资源授权
角色与能力
邀请与审批
知识库/文档业务
列表与搜索
通知
API 契约
数据库迁移
前端迁移
```

旧架构主要围绕一张 `Collaborator` 表：

```text
User → Collaborator → Knowledge / Document
```

`Collaborator` 同时承担了：

```text
已生效授权
邀请来源
审批状态
资源角色
协作者列表数据
```

当系统扩展为空间、公共区、团队、知识库和文档后，权限来源变成：

```text
创建者
用户直接授权
团队角色继承
空间角色继承
公开访问
邀请
审批
```

因此 V2 将“最终授权事实”“产生授权的流程”“角色的具体能力”拆开。

## 2. 已确定的核心架构

### 2.1 权限计算主链

```text
用户直接身份 / 团队角色 / 空间角色 / 公开策略
                      ↓
                 ResourceGrant
                      ↓
              解析 ResourceRole
                      ↓
 PermissionGroup(scope_type + scope_id + role_key)
                      ↓
              PermissionAbility
                      ↓
               最终 AbilityMap
```

职责边界：

```text
ResourceGrant
= 某个主体对某个资源拥有什么资源角色

PermissionGroup + PermissionAbility
= 该资源中的某个角色具体能执行哪些操作
```

资源角色：

```text
admin
edit
read
none
```

授权主体：

```text
user
space_role
team_role
```

### 2.2 邀请、审批与授权

```text
ResourceInvitation
├── 无需审批 → ResourceGrant
└── 需要审批 → ResourceAccessRequest
                    └── approved → ResourceGrant
```

职责：

```text
ResourceInvitation
= 邀请链接配置

ResourceAccessRequest
= 单步访问申请和审批历史

ResourceGrant
= 当前真正生效的授权
```

邀请和审批只是产生 `ResourceGrant` 的入口，权限判断不依赖邀请或审批状态。

### 2.3 文档权限继承

```text
知识库 PermissionGroup 提供的能力
                  OR
文档 PermissionGroup 提供的能力
                   ↓
             文档最终能力
```

当前规则是逐能力 OR：

```text
任意有效授权路径允许某能力 → 最终允许
```

当前不支持显式 `DENY`，因此文档级权限不能收回知识库已经授予的能力。

## 3. 当前实现进度

以下百分比用于表达阶段进度，不代表生产可用性。

| 模块 | 完成度 | 状态 |
| --- | ---: | --- |
| 权限枚举与领域拆分 | 85% | 主要枚举已拆分 |
| ResourceGrant | 80% | 单资源、批量知识库角色解析已完成 |
| PermissionGroup / Ability | 75% | 新结构和知识库/文档解析已完成 |
| 单资源鉴权与 Depends | 80% | 具体 Ability 和公开读取已接入 |
| 批量知识库能力 | 90% | 已形成固定批量查询链 |
| ResourceInvitation | 75% | Model、Schema、Service、Route 已建立 |
| ResourceAccessRequest | 80% | 申请、审批、拒绝、取消、幂等已建立 |
| 知识库业务迁移 | 40% | 创建、详情、visibility 完成；列表未完成 |
| 文档业务迁移 | 25% | 路由鉴权部分完成，业务仍依赖旧表 |
| 搜索和通知 | 10% | 仍主要依赖 Collaborator |
| 空间/团队能力组 | 15% | 只有作用域和角色基础 |
| 成员邀请域 | 0% | 暂未实现 |
| Alembic 与数据回填 | 0% | 尚未开始 |
| 前端迁移 | 0%～5% | 保留到后端稳定后集中处理 |
| V2 自动化测试 | 0% | 尚未建立 |

综合判断：

```text
权限计算内核：约 70%～75%
后端业务整体迁移：约 45%
可启动、可联调、可迁移：约 25%～30%
空间—团队—知识库完整产品：约 25%
```

## 4. 已完成的关键能力

### 4.1 ResourceGrant

已经支持：

- 创建者直接授权；
- 用户直接授权；
- 团队角色继承；
- 空间角色继承；
- 公开资源提供最低 `READ`；
- 多条有效授权取最高 `ResourceRole`；
- 知识库创建时建立默认 Grant；
- visibility 切换时同步空间成员默认 Grant；
- 唯一约束防止同主体重复授权；
- 新增授权时使用保存点隔离唯一键冲突。

### 4.2 PermissionGroup 与 Ability

当前结构：

```text
PermissionGroup
- scope_type
- scope_id
- role_key

PermissionAbility
- permission_group_id
- ability_key
- enabled
```

唯一约束：

```text
PermissionGroup:
(scope_type, scope_id, role_key)

PermissionAbility:
(permission_group_id, ability_key)
```

已支持：

- 每个知识库独立配置相同角色的能力；
- 每个文档独立配置相同角色的能力；
- KnowledgeAbility 与 DocumentAbility；
- 知识库和文档 AbilityMap 合并；
- 路由通过具体 Ability 鉴权，而不是只判断角色。

### 4.3 批量知识库权限

当前批量链：

```text
批量 Knowledge
    ↓
批量 ResourceGrant
    ↓
批量 TeamMember + SpaceMember
    ↓
内存中按 principal_type/id/role 匹配
    ↓
每个知识库取最高 ResourceRole
    ↓
批量 PermissionGroup + joinedload abilities
    ↓
knowledge_id → AbilityMap
```

这样避免列表逐条调用单资源方法产生 N+1。

### 4.4 邀请与审批

已支持：

- 一个资源一个邀请配置；
- 创建或更新邀请配置；
- 重置 token；
- 撤销邀请；
- 无审批时直接创建 Grant；
- 有审批时首次访问返回邀请信息；
- 用户主动提交后创建 pending Request；
- pending Request 幂等；
- 通过、拒绝、取消；
- 审批通过创建直接用户 Grant；
- 用户已有更高权限时不重复写入低权限 Grant；
- 申请保存 `requested_role` 和 `invitation_id` 快照。

并发控制：

```text
pending_key
= resource_type:resource_id:applicant_user_id
```

`pending_key` 唯一约束保证同一用户对同一资源只有一条 pending 申请。

```text
begin_nested
= 外层事务中的 SAVEPOINT
```

唯一键冲突时，只回滚保存点内失败的 INSERT，外层事务仍可继续查询已存在记录。

## 5. 当前明确不能运行的原因

当前仓库是新旧架构并存的中间状态。

旧的 `app/common/enums/collaborator.py` 已删除，但下列活跃模块仍导入旧枚举或旧 Model：

```text
KnowledgeService
DocumentService
SearchService
NotificationService
core/deps.py
resource endpoint
ResourceAccessSetting
旧 Collaborator Endpoint/Service/Schema/Model
```

残留类型包括：

```text
CollaboratorRole
CollaboratorStatus
CollaboratorSource
CollaborateResourceType
```

因此：

```text
compileall 可能通过
应用模块导入仍会失败
```

本阶段不恢复旧枚举，而是继续逐模块迁移，直到所有活跃调用链脱离 `Collaborator`。

## 6. 尚未迁移的主要调用链

### 6.1 知识库

已经迁移：

- 创建知识库；
- 默认 Grant；
- 默认 PermissionGroup/Ability；
- 知识库详情 AbilityMap；
- visibility；
- 具体 Ability 路由鉴权；
- 批量 AbilityMap。

尚未迁移：

```text
_build_personal_query
_build_mine_query
_build_collaborate_query
_apply_abilities_filter
leave knowledge
旧 toggle_public
```

旧列表仍使用：

```text
Collaborator.role
Collaborator.source
Collaborator.status
```

旧能力筛选仍读取已删除字段：

```text
PermissionGroup.target_id
PermissionGroup.target_type
PermissionGroup.role
```

### 6.2 文档

已经迁移：

- `DOC_CREATE`；
- `DOC_EXPORT`；
- `DOC_EDIT`；
- `DOC_DELETE`；
- 文档读取和知识库继承的基本入口。

尚未迁移：

- 创建文档时仍写 Collaborator；
- 文档协作者查询仍依赖 Collaborator；
- 文档列表和成员列表未迁移；
- Model relationship 仍保留 collaborators；
- 部分服务仍使用旧 `CollaborateResourceType`。

### 6.3 搜索

仍通过 `Collaborator` 查询“与我相关”。

还存在已删除字段引用：

```python
Knowledge.is_public
```

应改为：

```python
Knowledge.visibility
```

### 6.4 通知

通知 payload 仍使用：

```text
collaborator_id
```

并通过 `CollaboratorService` 还原资源信息。

V2 应逐步使用：

```text
resource_type
resource_id
invitation_id
access_request_id
```

### 6.5 空间与团队

目前已有：

```text
PermissionScopeType.SPACE
PermissionScopeType.TEAM
SpaceMemberRole
TeamMemberRole
```

但 `PermissionAbilityService` 当前只处理：

```text
KNOWLEDGE
DOCUMENT
```

尚未实现：

```text
SpaceAbility
TeamAbility
空间默认权限组
团队默认权限组
空间/团队具体能力鉴权
```

## 7. 成员域未来设计（暂缓）

资源邀请和成员邀请不共表。

未来成员域：

```text
MembershipInvitation
├── 无需审批 → SpaceMember / TeamMember
└── 需要审批 → MembershipJoinRequest
                    └── approved
                        ├── SpaceMember
                        └── TeamMember
```

通过 `target_type=space/team` 区分目标。

当前里程碑不实现这部分，避免权限重构无限扩张。

## 8. 下一阶段实施顺序

### 阶段 A：完成知识库业务迁移

1. 统一知识库列表接口和查询 Schema；
2. 明确三个不同维度：
   - 容器：personal / space public area / team；
   - 访问来源：creator / direct / team / space / public；
   - 页面分类：own / collaboration / space / team；
3. 删除响应中的 `collaborator_id`；
4. 使用 `Knowledge.creator_id` 表达创建者；
5. 使用 Grant + Membership 表达协作权限；
6. 用 `EXISTS` 或分阶段查询重写列表，避免 JOIN 多条 Grant 产生重复行；
7. 重写 Ability 筛选；
8. 重写退出知识库：只允许删除用户直接 Grant；
9. 删除旧 `toggle_public`；
10. 清理 KnowledgeService 的旧 Collaborator 引用。

### 阶段 B：完成文档业务迁移

1. 文档创建不再写 Collaborator；
2. 创建文档默认 Grant 和权限组；
3. 文档详情、列表统一使用有效 Ability；
4. 重写文档协作者聚合列表；
5. 清理 DocumentService 的旧枚举和查询；
6. 删除 Document/Knowledge/User 上的 collaborator relationship。

### 阶段 C：搜索、通知与杂项

1. 搜索“与我相关”改为 Grant 和成员身份；
2. 清理所有 `Knowledge.is_public`；
3. 通知 payload 不再依赖 collaborator_id；
4. `ResourceAccessSetting` 改用 `ResourceType`；
5. 清理旧 resource endpoint。

### 阶段 D：彻底删除 Collaborator

删除：

```text
Model
Schema
Service
Endpoint
relationship
旧枚举引用
旧表
```

完成后，后端应重新具备正常导入和启动条件。

### 阶段 E：数据库与交付

1. 编写 Alembic Expand 迁移；
2. 编写幂等历史数据回填脚本；
3. 编写数据核验脚本；
4. 建立核心权限矩阵测试；
5. 前端整体迁移；
6. 联调和回归；
7. 稳定后再执行 Contract 迁移删除旧结构。

## 9. 当前建议的阶段性停止点

为了避免长期陷在权限系统中，当前核心里程碑定义为：

```text
知识库 + 文档
    ↓
ResourceGrant
    ↓
PermissionGroup / Ability
    ↓
邀请 / 审批
    ↓
实际路由鉴权
    ↓
删除旧 Collaborator 活跃依赖
    ↓
后端能够启动并通过核心测试
```

达到该里程碑后，暂缓：

```text
完整空间权限管理
完整团队自定义权限
成员邀请审批
部门权限
离职回收
显式 DENY
```

随后将主要精力切回 Agent 和多模态 Agent 开发。

## 10. 数据库发布原则

当前开发分支允许完全重写，不要求代码兼容旧 `Collaborator`。

正式发布时仍建议：

```text
Expand
→ 新建表和新字段，不删除旧结构

Migrate
→ 幂等回填和数据核验

Switch
→ 切换到 V2 后端和前端

Contract
→ 稳定后再删除旧表和旧字段
```

第一版 V2 发布时建议保留旧表作为回滚保险，不在同一次发布中物理删除历史结构。

最低安全线：

- 发布前备份；
- 在生产数据副本演练；
- 回填脚本幂等；
- 有独立核验脚本；
- 准备明确回滚步骤；
- 权限矩阵覆盖创建者、团队角色、空间角色、直接协作者、游客和文档继承。

## 11. 继续开发时的审查清单

每次继续前：

1. 读取本文和 `permission-refactor-handoff.md`；
2. 读取磁盘当前代码，不能依赖聊天记忆；
3. 使用 `rg` 查找旧 Collaborator 和旧字段；
4. 检查 `app/core/deps.py` 与真实路由 Depends；
5. 检查单资源和批量权限结果是否一致；
6. 检查团队/空间 Grant 是否同时匹配 principal type、id、role；
7. 检查列表是否产生 N+1；
8. 检查 Service 是否错误地把邀请或审批当作最终权限；
9. 检查事务边界：Service flush，Endpoint commit/rollback；
10. 完成阶段后再删除旧代码，不在多个模块同时留下不同半成品方案。

## 12. 当前关键文件

权限内核：

```text
app/services/resource_grant_service.py
app/services/permission_service.py
app/services/permission_group_service.py
app/services/permission_ability_service.py
```

Repository：

```text
app/repositories/resource_grant_repository.py
app/repositories/permission_group_repository.py
app/repositories/knowledge_repository.py
app/repositories/document_repository.py
```

邀请与审批：

```text
app/models/resource_invitation.py
app/models/resource_access_request.py
app/services/resource_invitation_service.py
app/services/resource_access_request_service.py
app/api/v1/endpoints/resource_invitation.py
app/api/v1/endpoints/resource_access_request.py
```

下一阶段主要文件：

```text
app/schemas/knowledge.py
app/services/knowledge_service.py
app/api/v1/endpoints/knowledge.py
```

## 13. 已确认的设计边界

- 不把个人空间强行模拟为普通团队；
- 公共区知识库使用 `team_id=None` 表达，不创建伪团队；
- 空间管理员不天然拥有所有团队内容权限；
- 团队成员必须先是空间成员；
- 外部联系人只能通过明确的团队或资源授权访问；
- GrantSource 用于来源和审计，不作为权限判断条件；
- 数据库角色字段使用字符串，Python Service 使用 Enum 校验；
- 多授权路径目前取最高角色；
- Ability 合并目前使用 OR，不支持显式拒绝；
- 公开性是访问策略，但在有效角色解析中提供最低 `READ`；
- 页面聚合列表不等于一张数据库业务表；
- 邀请和审批不是最终授权；
- 批量列表不能循环调用单资源权限方法。

