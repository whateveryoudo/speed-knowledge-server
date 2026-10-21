# 树形组织架构设计与遍历算法工程实践指南

本文档全面总结了在开发**空间组织架构（Space Department）**体系时沉淀的底层算法原理、排序模型选择、以及工程落地最佳实践。

---

## 目录
- [一、业务背景与问题定义](#一业务背景与问题定义)
- [二、树形排序模型方案选型（为什么部门不用链表）](#二树形排序模型方案选型为什么部门不用链表)
- [三、树遍历三大算法深度解构](#三树遍历三大算法深度解构)
  - [1. 递归深度优先（DFS - Recursive）](#1-递归深度优先dfs---recursive)
  - [2. 循环队列广度优先（BFS - Queue）](#2-循环队列广度优先bfs---queue)
  - [3. 循环栈深度优先（DFS - Stack）](#3-循环栈深度优先dfs---stack)
  - [4. 为什么 `pop()` 比 `pop(0)` 会突变为由深到浅？](#4-为什么-pop-比-pop0-会突变为由深到浅)
- [四、三大算法优劣势与场景选型矩阵](#四三大算法优劣势与场景选型矩阵)
- [五、部门架构树的工程安全防线](#五部门架构树的工程安全防线)
  - [1. 闭环死锁防范（Cycle Detection）](#1-闭环死锁防范cycle-detection)
  - [2. 原生 SQL EXISTS 短路懒加载优化](#2-原生-sql-exists-短路懒加载优化)
  - [3. 多租户数据越权防护（BOLA 防护）](#3-多租户数据越权防护bola-防护)

---

## 一、业务背景与问题定义

在空间管理模块中，部门呈现为典型的无限级多叉树结构：
- **空间（Space）**：拥有一个唯一的根部门（Root Department，通常为空间公司同名节点，`parent_id IS NULL`）；
- **部门（SpaceDepartment）**：支持无限级子部门（`parent_id` 指向父部门）；
- **成员（SpaceMember）与部门（SpaceDepartment）**：为**多对多（N:N）**关系，通过中间表 `SpaceDepartmentMember` 关联。

在针对部门树进行移动、排序、删除、以及人数统计时，需要高效的算法支撑。

---

## 二、树形排序模型方案选型（为什么部门不用链表）

在系统中，存在两种截然不同的树节点排序业务场景：

| 对比维度 | 知识库文档目录树（Document Tree） | 空间部门组织树（Department Tree） |
| :--- | :--- | :--- |
| **操作频次** | **极高频**（每天上千次编辑、协同拖拽排序） | **极低频**（一个月难得调整一次） |
| **并发冲突** | 高频多人协同编辑，易行锁冲突和死锁 | 通常只有 1~2 名系统管理员单点维护 |
| **所选方案** | **双向链表（Prev/Next ID）** | **整数同级排序（Dense Integer `sort_order`）** |
| **选型原因** | 拖拽时永远只更新相邻 3 个节点的指针，锁粒度极小 | 查询只需单句 `ORDER BY sort_order ASC, created_at ASC`，极速出结果，无需内存穿糖葫芦拼指针 |

### 稳定排序（Stable Ordering）原则
当出现兄弟节点 `sort_order` 相同（例如都为默认值 `0`）时，SQL 使用多重权重规则保障排序稳定性：
```sql
ORDER BY sort_order ASC, created_at ASC;
```
- **第一权重**：`sort_order` 升序；
- **第二权重**：创建时间 `created_at` 升序（先建的在先）。
确保页面刷新 100 次渲染顺序绝对一致，不产生视觉跳动。

---

## 三、树遍历三大算法深度解构

假设组织关系如下：
```text
技术部 (root)
 ├── 前端组 (child_1)
 │     ├── Vue小组 (grandchild_1)
 │     └── React小组 (grandchild_2)
 └── 后端组 (child_2)
```

### 1. 递归深度优先（DFS - Recursive）
人类直觉友好型，符合分治法思想。

```python
def get_all_sub_dept_ids_recursive(tree_map: dict, current_id: str, result: list):
    for child_id in tree_map.get(current_id, []):
        result.append(child_id)
        get_all_sub_dept_ids_recursive(tree_map, child_id, result)  # 钻到底
```
- **遍历顺序**：前端组 ➔ Vue小组 ➔ React小组 ➔ 后端组。

---

### 2. 循环队列广度优先（BFS - Queue）
水波扩散型，一层一层横向推进。

```python
queue = [root_dept_id]
result = []
while queue:
    cur = queue.pop(0)  # 👈 核心：从队头拿出（先入先出 FIFO）
    for child_id in tree_map.get(cur, []):
        result.append(child_id)
        queue.append(child_id)  # 排到队伍最末尾，等当前辈分全部处理完
```
- **遍历顺序**：前端组 ➔ 后端组 ➔ Vue小组 ➔ React小组。

---

### 3. 循环栈深度优先（DFS - Stack）
系统调用栈的堆内存模拟版，防爆栈利器。

```python
stack = [root_dept_id]
result = []
while stack:
    cur = stack.pop()  # 👈 核心：从末尾弹出（后入先出 LIFO）
    result.append(cur)
    # 若希望遍历顺序与递归严格一致，需将子节点倒序入栈
    for child_id in reversed(tree_map.get(cur, [])):
        stack.append(child_id)
```
- **遍历顺序**：前端组 ➔ Vue小组 ➔ React小组 ➔ 后端组。

---

### 4. 为什么 `pop()` 比 `pop(0)` 会突变为由深到浅？

- **`pop(0)`（队列，排队逻辑）**：
  新发现的子孙节点被 `append` 到队尾，**必须老老实实排队**，直到排在它前面的“长辈”全部被 `pop(0)` 处理完毕。因此呈现**按层级横向推进（广度优先）**。
- **`pop()`（栈，就近深入逻辑）**：
  刚被 `append` 进去的新一代子代，处在列表的最末尾，**在下一次循环的一瞬间立刻就被 `pop()` 抓出来继续深挖**！因此呈现**纵向深挖到底，撞墙才回退（深度优先）**。

---

## 四、三大算法优劣势与场景选型矩阵

```
                ┌── 递归 DFS ─────── 业务树小(深度<1000)、组装前端路由/嵌套菜单、可读性第一
                │
树遍历选型路径 ──┼── 队列 BFS ─────── 求最短路径、二度人脉、水波层级展开、依赖环检测
                │
                └── 循环栈 DFS ───── 超深树(深度>10000)、操作系统文件扫描、编译器AST
```

| 维度 | 递归 (DFS) | While 队列 (BFS) | While 栈 (循环 DFS) |
| :--- | :--- | :--- | :--- |
| **底层结构** | 系统函数调用栈（Call Stack） | 堆内存列表 `pop(0)` | 堆内存列表 `pop()` |
| **空间复杂度** | $O(H)$，$H$ 为树最大深度 | $O(W)$，$W$ 为树最大宽度 | $O(H)$，$H$ 为树最大深度 |
| **爆栈风险** | **有**（Python 默认深度超 1000 会异常） | **无**（受限于机器物理内存） | **无**（受限于机器物理内存） |
| **代码可读性** | ★★★★★（人类直觉最佳） | ★★★★☆（清晰明了） | ★★★☆☆（需考虑逆序入栈） |

---

## 五、部门架构树的工程安全防线

### 1. 闭环死锁防范（Cycle Detection）
在编辑部门时，若允许将【上级部门（`parent_id`）】修改为【自己】或【自己的任何下级子孙】：
```text
爷爷 (技术部) ➔ 爸爸 (前端组) ➔ 孙子 (Vue组)
若将技术部的 parent 改为 Vue组：
Vue组 ➔ 前端组 ➔ 技术部 ➔ Vue组 (无限闭环死锁！)
```
**安全防御实现（在 Service 层拦截）**：
```python
if data.parent_id is not None and data.parent_id != dept.parent_id:
    # 1. 不能设置为自己
    if data.parent_id == dept.id:
        raise HTTPException(400, "不能将上级部门设置为自己")
    # 2. 不能设置为自己的任意子孙节点（通过 BFS/DFS 提前探明）
    sub_ids = self.repo.get_all_sub_dept_ids(space_id=space_id, root_dept_id=dept.id)
    if data.parent_id in sub_ids:
        raise HTTPException(400, "不能将上级部门调整为自己的子孙部门")
    dept.parent_id = data.parent_id
```

### 2. 原生 SQL EXISTS 短路懒加载优化
树组件懒加载如果使用 `COUNT(*)` 会导致全表扫描子节点，改用原生短路 `EXISTS`：
```python
sub_dept = aliased(SpaceDepartment)
has_children_expr = exists(
    select(1).where(sub_dept.parent_id == SpaceDepartment.id)
).label("has_children")

# 只要 MySQL 索引探到第 1 条满足条件的子记录，立即返回 1，耗时趋近 O(1)
```

### 3. 多租户数据越权防护（BOLA 防护）
在所有通过 ID 查询和操作部门的 SQL 中，**永远强制绑定 `space_id`**：
```python
db.query(SpaceDepartment).filter(
    SpaceDepartment.id == dept_id,
    SpaceDepartment.space_id == space_id  # 隔离防线，杜绝跨租户越权修改
)
```
哪怕攻击者伪造或枚举其他租户的 `dept_id`，查询也会精确返回 `404 Not Found`，彻底锁死多租户安全。
