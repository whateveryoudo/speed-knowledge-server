"""知识库的文档树服务"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload, contains_eager, with_loader_criteria
from sqlalchemy import and_
from app.models.document import Document
from app.models.document_node import DocumentNode
from app.schemas.document_node import DocumentNodeResponse
from typing import List, Optional
from app.schemas.document import DocumentCreate
from app.common.enums import DocumentType, DocumentNodeType
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
                with_loader_criteria(DocumentNode, Document.deleted_at.is_(None))
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
