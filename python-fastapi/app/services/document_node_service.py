"""知识库的文档树服务"""

from sqlalchemy.orm import Session
from app.models.document_node import DocumentNode
from app.schemas.document_node import DocumentNodeResponse
from typing import List, Optional
from sqlalchemy.orm import joinedload
from app.schemas.document import DocumentCreate
from app.common.enums import DocumentType, DocumentNodeType

class DocumentNodeService:
    """知识库的文档树服务"""
    def __init__(self, db: Session):
        self.db = db

    def create_node(self, document_in: DocumentCreate, parent_id: Optional[str] = None) -> DocumentNode:
        """创建文档树节点"""
        first_child = (
            self.db.query(DocumentNode)
            .filter(
                DocumentNode.knowledge_id == document_in.knowledge_id,
                DocumentNode.parent_id == parent_id,
                DocumentNode.prev_id.is_(None),
            )
            .first()
        )
        node_type = DocumentNodeType.DOC if document_in.type in DocumentType else DocumentNodeType.TITLE
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
            parent = self.db.query(DocumentNode).get(parent_id)
            if parent and (parent.first_child_id is None or parent.first_child_id == first_child.id):
                parent.first_child_id = new_node.id
        self.db.add(new_node)
        self.db.commit()
        self.db.refresh(new_node)
        return new_node

    def get_document_tree_nodes(self, knowledge_id: str) -> List[DocumentNodeResponse]:
        """获取知识库的文档树"""
        
        return (
            self.db.query(DocumentNode)
            .options(joinedload(DocumentNode.document))
            .filter(DocumentNode.knowledge_id == knowledge_id)
            .all()
        )

    def get_node_by_document_id(self, document_id: str) -> DocumentNode:
        """通过文档id获取节点"""
        return (
            self.db.query(DocumentNode)
            .filter(DocumentNode.document_id == document_id)
            .first()
        )
