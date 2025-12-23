"""文档服务"""

from app.models.document import Document, DocumentContent
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from typing import List
from sqlalchemy.orm import Session
from app.services.document_node_service import DocumentNodeService
import secrets
import string

alphabet = string.ascii_letters + string.digits


class DocumentService:
    """文档服务"""
    def _generate_slug(self) -> str:
        """生成文档短链"""
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def __init__(self, db: Session):
        self.db = db

    def create(self, document_in: DocumentCreate) -> Document:
        """创建文档"""
        temp_slug = self._generate_slug()
        while self.db.query(Document).filter(Document.slug == temp_slug).first():
            temp_slug = self._generate_slug()
        document = Document(
            user_id=document_in.user_id,
            knowledge_id=document_in.knowledge_id,
            name=document_in.name,
            slug=temp_slug,
            type=document_in.type,
        )
        self.db.add(document)
        self.db.flush()
        # 构建文档内容
        document_content = DocumentContent(
            document_id=document.id,
            content=b"",
        )
        self.db.add(document_content)
        self.db.commit()
        self.db.refresh(document)
        self.db.refresh(document_content)
        # 调用节点更新
        document_node_service = DocumentNodeService(self.db)
        # 追加文档id
        temp_document_in = document_in.model_copy(update={"id": document.id}) 
        document_node_service.create_node(temp_document_in, document_in.parent_id)
        return document    

    def get_by_id_or_slug(self, identifier: str, user_id: int) -> Document:
        """通过id或短链获取文档"""
        document = (
            self.db.query(Document)
            .filter(
                (Document.id == identifier) | (Document.slug == identifier),
                Document.user_id == user_id,
            )
            .first()
        )
        return document

    def get_list_by_user_id(self, user_id: int) -> List[Document]:
        """通过用户id获取文档列表"""
        return self.db.query(Document).filter(Document.user_id == user_id).all()

    def get_list_by_knowledge_id(self, knowledge_id: str) -> List[Document]:
        """通过知识库id获取文档列表"""
        return (
            self.db.query(Document).filter(Document.knowledge_id == knowledge_id).all()
        )

    def update_by_id_or_slug(self, updated_document: Document) -> Document:
        """通过id或短链更新文档"""
         # 调用节点更新
        document_node_service = DocumentNodeService(self.db)
        document_node=document_node_service.get_node_by_document_id(updated_document.id)
        document_node.title = updated_document.name
        self.db.commit()
        self.db.refresh(updated_document)
        self.db.refresh(document_node)
        return updated_document
        