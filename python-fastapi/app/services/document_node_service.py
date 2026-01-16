"""知识库的文档树服务"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload, contains_eager, with_loader_criteria
from sqlalchemy import and_
from app.models.document import Document
from app.models.document_node import DocumentNode
from app.schemas.document_node import DocumentNodeResponse
from typing import List, Optional
from app.schemas.document import DocumentCreate, DragDocumentNodeParams
from app.common.enums import DocumentType, DocumentNodeType, DocumentNodeDragAction
from app.services.base_service import BaseService


class DocumentNodeService(BaseService[DocumentNode]):
    """知识库的文档树服务"""

    def __init__(self, db: Session):
        super().__init__(db, DocumentNode)

    def create_node(
        self, document_in: DocumentCreate, parent_id: Optional[str] = None
    ) -> DocumentNode:
        """创建文档树节点"""
        first_child = (
            self.get_active_query()
            .filter(
                DocumentNode.knowledge_id == document_in.knowledge_id,
                DocumentNode.parent_id == parent_id,
                DocumentNode.prev_id.is_(None),
            )
            .first()
        )
        node_type = (
            DocumentNodeType.DOC
            if document_in.type in DocumentType
            else DocumentNodeType.TITLE
        )
        # 构建新节点
        new_node = DocumentNode(
            document_id=document_in.id,
            knowledge_id=document_in.knowledge_id,
            type=node_type,
            title=document_in.name,
            parent_id=parent_id,
        )

        if first_child:
            new_node.next_id = first_child.id
            first_child.prev_id = new_node.id

        if parent_id:
            parent = (
                self.db.query(DocumentNode).filter(DocumentNode.id == parent_id).first()
            )
            if parent and (
                parent.first_child_id is None or parent.first_child_id == first_child.id
            ):
                parent.first_child_id = new_node.id
        self.db.add(new_node)
        self.db.commit()
        self.db.refresh(new_node)
        return new_node

    def get_document_tree_nodes(self, knowledge_id: str) -> List[DocumentNodeResponse]:
        """获取知识库的文档树"""
        return (
            self.get_active_query()
            .filter(DocumentNode.knowledge_id == knowledge_id)
            .options(
                joinedload(DocumentNode.document),
                with_loader_criteria(DocumentNode, Document.deleted_at.is_(None)),
            )
            .all()
        )

    def get_node_by_document_id(self, document_id: str) -> DocumentNode:
        """通过文档id获取节点"""
        return (
            self.get_active_query()
            .filter(DocumentNode.document_id == document_id)
            .first()
        )

    def get_node_by_id(self, node_id: str) -> DocumentNode:
        """通过节点id获取节点"""
        return self.get_active_query().filter(DocumentNode.id == node_id).first()

    def delete_by_document_id(
        self, document_id: str, is_soft_delete: bool = True
    ) -> None:
        """通过文档id软删除节点"""
        document_node = (
            self.get_active_query()
            .filter(DocumentNode.document_id == document_id)
            .first()
        )
        if not document_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档节点不存在"
            )
        if is_soft_delete:
            self.soft_delete(document_node)
        else:
            self.get_active_query().filter(
                DocumentNode.document_id == document_id
            ).delete()
        self.db.commit()
        return None

    def drag_document(self, drag_document_in: DragDocumentNodeParams) -> None:
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
        if not drag_node or not target_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="拖拽节点不存在"
            )
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
