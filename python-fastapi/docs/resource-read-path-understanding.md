# 资源读取链路：有效性、权限与分页

> 用途：记录本轮权限 V2 改造中已经确认的读取规则，解释为什么资源列表、搜索、收藏、历史等入口不能只查 `ResourceGrant`，以及当前阶段为何采用“全量有效候选后再做权限过滤”。
>
> 本文只讨论读取链路；创建、邀请、审批、修改 visibility、写入或删除 Grant 属于授权管理链路，不在这里展开。

## 1. 一个资源能展示，需要同时满足两件事

```text
资源有效
AND
当前用户可读
```

这两个问题相互独立，不能互相替代。

```text
资源有效：资源及其父级是否仍存在、仍处于有效状态
当前用户可读：当前用户是否拥有该资源的具体 READ Ability
```

例如：

```text
用户曾被授予文档 read
但该文档所在的 Space 已软删除
=> 有 Grant，但资源无效，不展示、不允许读取

知识库仍存在、父链也有效
但用户对应角色的 READ_BOOK 被关闭
=> 资源有效，但用户不可读，不展示、不允许读取
```

## 2. 有效资源的链式判断

### 2.1 知识库

知识库有效的条件：

```text
Knowledge.deleted_at IS NULL
AND Space.deleted_at IS NULL
AND (
    Knowledge.team_id IS NULL
    OR (
        Team 存在
        AND Team.deleted_at IS NULL
        AND Team.space_id == Knowledge.space_id
    )
)
```

### 2.2 文档

文档有效的条件：

```text
Document.deleted_at IS NULL
AND Knowledge 满足上述有效条件
```

展开后就是：

```text
Document 未删除
→ Knowledge 未删除
→ Space 未删除
→ Team 为空，或 Team 未删除且属于 Knowledge 的 Space
```

### 2.3 为什么不在删除父资源时级联软删除子资源

父资源软删除时，只修改父资源自己的 `deleted_at`：

```text
删除 Space      → 只删除 Space
删除 Team       → 只删除 Team
删除 Knowledge  → 只删除 Knowledge
删除 Document   → 只删除 Document
```

不级联修改子资源的原因是需要保留“是谁删除了谁”的语义：

```text
Knowledge 被删除后，Document 暂时不可见
Document 本身没有被删除
恢复 Knowledge 后，Document 自动重新可见

如果某篇 Document 本身也被单独删除
恢复 Knowledge 后，它仍应保持删除状态
```

因此，读取时必须检查完整父链，而不是只检查资源本身。

### 2.4 Repository 的职责

以下方法统一承载父链有效性过滤，并加载后续权限与响应组装需要的关系：

```python
KnowledgeRepository.active_scope_query()
DocumentRepository.active_scope_query()
```

它们使用 SQL `join / outerjoin` 进行过滤，并通过 `contains_eager` 把已 join 的关系填入 ORM：

```text
join / outerjoin：用于 SQL 过滤父链
contains_eager：复用这次 join 的结果加载 relationship
```

业务 Service 不应重新手写一套 `Knowledge.deleted_at`、`Space.deleted_at`、`Team.deleted_at` 条件。

## 3. 权限判断：Grant 不是最终权限

### 3.1 Grant 表达的是什么

`ResourceGrant` 记录的是授权事实，例如：

```text
某用户被直接授予 read
某团队 editor 角色被授予 edit
某空间 member 被授予 read
空间 owner/admin 被授予 admin
```

它回答的是：

```text
用户通过哪些主体，可能命中了哪个 ResourceRole
```

它不直接回答：

```text
用户是否拥有 READ_BOOK / DOC_READ
```

### 3.2 最终权限的完整过程

```text
ResourceGrant
→ 根据用户、团队成员、空间成员、角色继承解析最高 ResourceRole
→ 找到资源对应的 PermissionGroup
→ 读取 PermissionAbility
→ 判断 READ_BOOK / DOC_READ 等具体 Ability
```

文档还额外受 visibility 规则影响：

```text
inherit：可继承父知识库的普通可见范围
private：阻断父知识库的普通空间范围和公开入口
space：文档自身向空间内部成员开放
public：文档自身向游客开放
```

所以，下面这种代码只能作为“业务候选范围”判断，不能作为最终读取判断：

```python
resource_grant_service.list_user_accessible_knowledge_ids(user_id=user_id)
resource_grant_service.list_user_granted_document_ids(user_id=user_id)
```

### 3.3 只读 Grant 会出现的问题

| 情况 | 只查 Grant 的结论 | 正确结论 |
| --- | --- | --- |
| 角色对应的 `READ_BOOK` 被关闭 | 误认为可读 | 不可读 |
| 文档是 `private`，父知识库对空间开放 | 可能误认为可读 | 普通空间成员不可读 |
| Space / Team / Knowledge 已软删除 | 可能仍命中 Grant | 资源无效，不可读 |
| public 搜索，当前登录用户刚好有私有 Grant | 可能混入私有资源 | 只能返回游客可读资源 |

### 3.4 业务 Service 的固定入口

业务 Service 应使用 `PermissionService`：

```python
# 单个资源
permission_service.assert_knowledge_readable(user_id, identifier)
permission_service.assert_document_readable(user_id, identifier)

# 一批资源
permission_service.filter_readable_knowledges(
    user_id=user_id,
    knowledges=knowledges,
)
permission_service.filter_readable_documents(
    user_id=user_id,
    documents=documents,
)
```

层次关系：

```text
搜索 / 收藏 / 历史 / 文档树 / Pin / 分组等业务 Service
    ↓
PermissionService（最终 Ability 判断）
    ↓
ResourceGrantService（解析授权事实与资源角色）
    ↓
Repository
```

例外：授权管理业务本身可以直接使用 `ResourceGrantService`，例如创建默认 Grant、批准访问申请、同步 visibility Policy Grant、删除直接协作者授权。

## 4. 搜索与列表：改造前后对比

### 4.1 改造前

以文档搜索为例，旧实现的思路是：

```text
Document + Knowledge 自身未删除
→ 按 Grant 预先找候选文档 / 知识库
→ SQL LIMIT 或 LIMIT * 5
→ 部分场景再逐条最终权限过滤
```

问题：

```text
1. 搜索自己重复拼接软删除条件，遗漏 Space / Team 父链。
2. 知识库搜索只按 Grant 过滤，没有最终 READ_BOOK 判断。
3. 文档搜索先 LIMIT * 5 再过滤；若前面的候选多数不可读，后面可读资源会被遗漏。
4. public 搜索、related 搜索各自维护一套条件，规则容易漂移。
```

### 4.2 当前阶段的调整方案

```text
Repository：按标题查询全部“标题命中 + 父链有效”的候选
    ↓
PermissionService：批量过滤最终可读资源
    ↓
Search / List Service：按排序后的结果截取 limit 或做内存分页
```

搜索伪代码：

```python
rows = document_repository.list_active_by_title(keyword=keyword)

readable_rows = permission_service.filter_readable_documents(
    user_id=user_id,
    documents=rows,
)

return readable_rows[:limit]
```

`public` 搜索不应该因为当前请求携带登录态就返回私有资源。它使用游客权限规则：

```python
readable_rows = permission_service.filter_readable_documents(
    user_id=None,
    documents=rows,
)
```

这代表“只保留游客可读资源”，而不是“用户未登录”。

## 5. 分页方案：为什么当前先全量过滤

### 5.1 不能先 SQL 分页、后权限过滤

错误顺序：

```text
SQL ORDER BY + LIMIT / OFFSET
→ 当前页做权限过滤
```

例如一页需要 20 条，但 SQL 取出的前 20 条里 15 条不可读：

```text
前端只得到 5 条
但后面的资源可能有可读文档
total 与 has_more 也不准确
```

### 5.2 当前阶段采用的方案

```text
全部“查询条件命中 + 父链有效”的候选
→ 最终权限过滤
→ 再做 [:limit] 或内存分页
```

对于分页列表：

```python
candidate_rows = query.all()
readable_rows = permission_service.filter_readable_knowledges(
    user_id=user_id,
    knowledges=candidate_rows,
)

page_rows = readable_rows[skip : skip + limit]
total = len(readable_rows)
has_more = total > skip + limit
```

优点：

```text
结果完整
分页 total / has_more 正确
规则最直观，方便权限 V2 矩阵验证
```

代价：关键词非常宽、资源数量非常大时，会加载较多 ORM 对象。

### 5.3 `limit * 5` 为什么不作为最终方案

它只是临时猜测：

```text
想返回 20 条
→ 先取 100 条候选
→ 权限过滤
→ 希望还能留下 20 条
```

它既不能保证结果完整，也和知识库搜索直接 `limit` 的逻辑不一致，因此本轮已确定不采用。

### 5.4 数据量变大后的演进方向

当全量候选确实造成性能问题，再替换为：

```text
游标分批取“父链有效”的候选
→ 每批批量权限过滤
→ 可读资源不够一页时继续取下一批
→ 直到凑满 limit 或候选耗尽
```

游标以稳定排序字段表示位置，例如：

```text
updated_at DESC, id DESC
```

这只是候选获取的性能优化；`PermissionService` 的调用方式、资源有效链规则、最终返回语义都不变。

更后续才考虑把复杂的角色与 Ability 判断完全下沉为一条 SQL。当前优先级是先保证权限语义一致、可测试。

## 6. 当前改造检查清单

资源读取或展示入口都应自问：

```text
1. 是否通过 KnowledgeRepository / DocumentRepository 的 active scope 获取资源？
2. 是否通过 PermissionService 做最终可读 / Ability 判断？
3. 是否在最终过滤之后才做 limit、分页、统计、Top N？
4. 如果只是用户个人关系（收藏、Pin、分组），资源失效或失权时是否隐藏关系而不删除记录？
```

当前已按此方向收口：

```text
文档搜索
知识库搜索
知识库内文档搜索
收藏列表
文档历史
知识库文档列表
文档树（文档节点部分）
```

待继续收口：

```text
我的 / 协作知识库分页列表
常用知识库 Pin
知识库分组中的资源与文档摘要
文档 context-users（需要按用户批量解析 DOC_READ）
```
