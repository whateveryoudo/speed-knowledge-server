"""知识库的文档树服务"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, contains_eager
from app.models.document import Document
from app.models.document_node import DocumentNode
from typing import List
from app.schemas.document_node import (
    DragDocumentNodeParams,
    DocumentNodeUpdate,
)
from app.common.enums import DocumentNodeType, DocumentNodeDragAction, DocumentAbility, KnowledgeAbility
from app.models.knowledge import Knowledge
from app.services.permission_service import PermissionService


class DocumentNodeService:
    """知识库的文档树服务"""

    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)

    def _insert_node(
        self,
        *,
        knowledge_id: str,
        name: str,
        node_type: DocumentNodeType,
        document_id: str | None,
        parent_id: str | None,
    ) -> DocumentNode:
        """创建文档树节点(通用)"""
        parent: DocumentNode | None = None
        if parent_id is not None:
            parent = self.get_node_by_id(parent_id)
            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="父节点不存在"
                )
            if parent.knowledge_id != knowledge_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="父节点不属于当前知识库",
                )
        first_child = (
            self.db.query(DocumentNode)
            .filter(
                DocumentNode.knowledge_id == knowledge_id,
                DocumentNode.parent_id == parent_id,
                DocumentNode.prev_id.is_(None),
            )
            .first()
        )

        # 构建新节点
        new_node = DocumentNode(
            document_id=document_id,
            knowledge_id=knowledge_id,
            type=node_type,
            title=name,
            parent_id=parent_id,
        )
        self.db.add(new_node)
        self.db.flush()

        if first_child is not None:
            new_node.next_id = first_child.id
            first_child.prev_id = new_node.id

        if parent is not None:
            parent.first_child_id = new_node.id
        return new_node

    def create_catalog_node(
        self,
        *,
        operator_id: int,
        knowledge_id: str,
        name: str,
        parent_id: str | None,
        commit: bool = True,
    ) -> DocumentNode:
        """创建目录节点"""
        self.permission_service.assert_knowledge_ability(
            user_id=operator_id,
            identifier=knowledge_id,
            ability=KnowledgeAbility.CREATE_DOCUMENT,
        )
        node = self._insert_node(
            knowledge_id=knowledge_id,
            name=name,
            node_type=DocumentNodeType.TITLE,
            document_id=None,
            parent_id=parent_id,
        )
        if commit:
            self.db.commit()
            self.db.refresh(node)
        return node

    def create_document_node(
        self,
        *,
        document: Document,
        parent_id: str | None,
        commit: bool = True,
    ) -> DocumentNode:
        """创建文档节点"""

        node = self._insert_node(
            knowledge_id=document.knowledge_id,
            name=document.name,
            node_type=DocumentNodeType.DOC,
            document_id=document.id,
            parent_id=parent_id,
        )
        if commit:
            self.db.commit()
            self.db.refresh(node)
        return node

    def delete_by_document_id(
        self, document_id: str, *, auto_commit: bool = True
    ) -> None:
        """通过文档id删除节点"""
        node = self.get_node_by_document_id(document_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="节点不存在"
            )
        self._delete_subtree(node)
        if auto_commit:
            self.db.commit()

    def get_document_tree_nodes(
        self, *, knowledge_id: str, user_id: int | None
    ) -> List[DocumentNode]:
        """获取知识库的文档树（追加权限过滤）"""
        nodes = (
            self.db.query(DocumentNode)
            .outerjoin(Document, DocumentNode.document_id == Document.id)
            .filter(DocumentNode.knowledge_id == knowledge_id)
            .filter(
                (DocumentNode.document_id.is_(None)) | (Document.deleted_at.is_(None))
            )
            .options(
                contains_eager(DocumentNode.document)
                .joinedload(Document.knowledge)
                .joinedload(Knowledge.team),
                contains_eager(DocumentNode.document)
                .joinedload(Document.knowledge)
                .joinedload(Knowledge.space),
            )
            .all()
        )
        documents = [node.document for node in nodes if node.document is not None]
        readability_by_id = (
            self.permission_service.resolve_multiple_document_readabilities(
                user_id=user_id, documents=documents
            )
        )
        # 批量入口当前内部仍逐条鉴权，后续优化为批量查询
        visible_nodes: List[DocumentNode] = []
        for node in nodes:
            if node.document_id is None:
                # 目录节点
                visible_nodes.append(node)
                continue
            if readability_by_id.get(node.document_id, False):
                visible_nodes.append(node)
        return visible_nodes

    def get_node_by_document_id(self, document_id: str) -> DocumentNode:
        """通过文档id获取节点"""
        return (
            self.db.query(DocumentNode)
            .filter(DocumentNode.document_id == document_id)
            .first()
        )

    def get_node_by_id(self, node_id: str) -> DocumentNode | None:
        """通过节点id获取节点"""
        return self.db.query(DocumentNode).filter(DocumentNode.id == node_id).first()

    def _delete_self(self, node: DocumentNode) -> None:
        """删除节点本身(不再递归)"""
        if node.type == DocumentNodeType.DOC:
            # 如果是文档节点，则软删文档
            if not node.document_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="文档节点缺少关联 document_id",
                )
            from app.services.document_service import DocumentService

            document_service = DocumentService(self.db)
            document = document_service.get_by_id_or_slug(node.document_id)
            if document:
                document.soft_delete()
        self.db.delete(node)

    def _unlink_node(self, node: DocumentNode) -> None:
        """从双向链表里面去掉node节点"""
        prev_id = node.prev_id
        next_id = node.next_id
        parent_id = node.parent_id
        if prev_id:
            prev_node = self.get_node_by_id(prev_id)
            if prev_node:
                prev_node.next_id = next_id
        if next_id:
            next_node = self.get_node_by_id(next_id)
            if next_node:
                next_node.prev_id = prev_id
        if parent_id:
            parent = self.get_node_by_id(parent_id)
            if parent and parent.first_child_id == node.id:
                parent.first_child_id = next_id
        node.prev_id = None
        node.next_id = None
        node.parent_id = None

    def _delete_subtree(self, node: DocumentNode) -> None:
        """递归删除子节点"""
        while node.first_child_id:
            child = self.get_node_by_id(node.first_child_id)
            if not child:
                node.first_child_id = None
                break
            self._delete_subtree(child)
        self._unlink_node(node)
        self._delete_self(node)

    def delete_node(self, *, operator_id: int, node_id: str) -> None:
        """通过node-id节点(需要同步软删除文档)"""
        node = self.get_node_by_id(node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="节点不存在"
            )
        # 文档树权限校验（需要有知识库的文档编辑能力）
        self.permission_service.assert_knowledge_ability(
            user_id=operator_id,
            identifier=node.knowledge_id,
            ability=DocumentAbility.DOC_DELETE,
        )
        # 递归删除子节点
        self._delete_subtree(node)
        self.db.commit()
        return None

    def update_node(
        self, *, operator_id: int, node_id: str, update_in: DocumentNodeUpdate
    ) -> None:
        """更新文档节点"""
        node = self.get_node_by_id(node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="节点不存在"
            )
        # 文档树权限校验（需要有知识库的文档编辑能力）
        if node.type == DocumentNodeType.DOC:
            if node.document_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="文档节点缺少关联 document_id",
                )
            # 这里校验的具体文档的权限(后续会有更新标题的逻辑)
            self.permission_service.assert_document_ability(
                user_id=operator_id,
                identifier=node.document_id,
                ability=DocumentAbility.DOC_EDIT,
            )
        else:
            self.permission_service.assert_knowledge_ability(
                user_id=operator_id,
                identifier=node.knowledge_id,
                ability=DocumentAbility.DOC_EDIT,
            )

        if node.type == DocumentNodeType.DOC:
            from app.services.document_service import DocumentService

            document_service = DocumentService(self.db)
            document_service.update_title(
                node.document_id, update_in.title, trigger="outer"
            )
        else:
            node.title = update_in.title
            self.db.commit()
        self.db.refresh(node)
        return node

    def _assert_valid_new_parent(
        self, *, drag_node: DocumentNode, new_parent_id: str | None
    ) -> None:
        """禁止将节点移动到自身或者自己的子树中"""
        current_id = new_parent_id
        visited_ids: set[str] = set()
        while current_id is not None:
            if current_id == drag_node.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能将节点移动到自身或者自己的子树中",
                )
            if current_id in visited_ids:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="目录树存在循环引用",
                )
            visited_ids.add(current_id)
            current_node = self.get_node_by_id(current_id)
            if current_node is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="目录树父链不完整"
                )
            current_id = current_node.parent_id

    def drag_document(
        self, *, operator_id: int, drag_document_in: DragDocumentNodeParams
    ) -> None:
        """拖拽文档"""
        # 查找拖拽节点和目标节点
        if (
            not drag_document_in.node_id.strip()
            or not drag_document_in.target_id.strip()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="节点ID或目标节点ID不能为空",
            )
        drag_node = self.get_node_by_id(drag_document_in.node_id)
        target_node = self.get_node_by_id(drag_document_in.target_id)
        if drag_node is None or target_node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="拖拽节点不存在"
            )
        if drag_node.id == target_node.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能将节点拖拽到自身",
            )
        if drag_node.knowledge_id != target_node.knowledge_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能跨知识库拖拽节点",
            )
        self.permission_service.assert_knowledge_ability(
            user_id=operator_id,
            identifier=drag_node.knowledge_id,
            ability=DocumentAbility.DOC_EDIT,
        )

        # 计算移动完成的后的父节点（用于环检测）
        if drag_document_in.action in (
            DocumentNodeDragAction.MOVE_AFTER,
            DocumentNodeDragAction.MOVE_BEFORE,
        ):
            new_parent_id = target_node.parent_id
        elif drag_document_in.action == DocumentNodeDragAction.PREPEND_CHILD:
            new_parent_id = target_node.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="操作类型不支持"
            )

        self._assert_valid_new_parent(drag_node=drag_node, new_parent_id=new_parent_id)

        # 保存拖拽节点的元素信息
        old_prev_id = drag_node.prev_id
        old_next_id = drag_node.next_id
        old_parent_id = drag_node.parent_id
        # 断链操作
        if old_prev_id:
            # 断开与前一个节点的连接
            old_prev = self.get_node_by_id(old_prev_id)
            if old_prev:
                old_prev.next_id = old_next_id
        if old_next_id:
            # 断开与后一个节点的连接
            old_next = self.get_node_by_id(old_next_id)
            if old_next:
                old_next.prev_id = old_prev_id
        if old_parent_id:
            # 断开与父节点的连接
            old_parent = self.get_node_by_id(old_parent_id)
            if old_parent:
                # 只有当 drag_node 是父节点的第一个子节点时，才需要更新
                if old_parent.first_child_id == drag_node.id:
                    # 更新为 drag_node 的下一个兄弟节点（如果存在）
                    old_parent.first_child_id = old_next_id if old_next_id else None
                    # 如果 drag_node 不是第一个子节点，first_child_id 不需要改变

        # 根据操作类型更新连接
        if drag_document_in.action == DocumentNodeDragAction.MOVE_AFTER:
            # 移动到目标节点之后
            drag_node.prev_id = target_node.id
            drag_node.next_id = target_node.next_id
            drag_node.parent_id = target_node.parent_id

            # 更新 target_node 的下一个节点
            target_node.next_id = drag_node.id
            if drag_node.next_id:
                next_node = self.get_node_by_id(drag_node.next_id)
                if next_node:
                    next_node.prev_id = drag_node.id

        elif drag_document_in.action == DocumentNodeDragAction.MOVE_BEFORE:
            # 移动到目标节点之前
            drag_node.prev_id = target_node.prev_id
            drag_node.next_id = target_node.id
            drag_node.parent_id = target_node.parent_id

            # 更新 target_node 的上一个节点
            target_node.prev_id = drag_node.id
            if drag_node.prev_id:
                prev_node = self.get_node_by_id(drag_node.prev_id)
                if prev_node:
                    prev_node.next_id = drag_node.id

            # 如果 target_node 是父节点的第一个子节点，需要更新父节点
            if target_node.parent_id:
                parent = self.get_node_by_id(target_node.parent_id)
                if parent and parent.first_child_id == target_node.id:
                    parent.first_child_id = drag_node.id

        elif drag_document_in.action == DocumentNodeDragAction.PREPEND_CHILD:
            # 作为目标节点的第一个子节点
            drag_node.parent_id = target_node.id
            drag_node.prev_id = None
            drag_node.next_id = target_node.first_child_id

            # 更新 target_node 原来的第一个子节点
            if target_node.first_child_id:
                first_child = self.get_node_by_id(target_node.first_child_id)
                if first_child:
                    first_child.prev_id = drag_node.id

            # 更新 target_node 的 first_child_id
            target_node.first_child_id = drag_node.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="操作类型不支持"
            )
        self.db.commit()
        return None
