"""文档服务"""

from app.models.document import Document, DocumentContent
from fastapi import HTTPException, status
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from typing import List
from sqlalchemy.orm import Session
from app.services.document_node_service import DocumentNodeService
from app.core.config import settings
import secrets
import string
import httpx
import logging
from sqlalchemy import func


alphabet = string.ascii_letters + string.digits

logger = logging.getLogger(__name__)


class DocumentService:
    """文档服务"""

    def _generate_slug(self) -> str:
        """生成文档短链"""
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def __init__(self, db: Session):
        self.db = db

    def create_default_content(self, document_id: str):
        """构建文档内容(这里调用nodejs服务构建一个默认的空的流和json)"""
        try:
            nodejs_service_url = settings.NODEJS_SERVICE_URL
            url = f"{nodejs_service_url}/document-content/create-default"
            payload = {
                "documentId": document_id,
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                logger.info(
                    f"Create default content by nodejs success:documentId={document_id}"
                )
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Create default content by nodejs failed:documentId={document_id},error={e}",
                exc_info=True,
            )
        except Exception as e:
            logger.error(
                f"Create default content by nodejs failed:documentId={document_id},error={e}"
            )

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
            content_updated_at=func.now(),
        )
        self.db.add(document)
        self.db.flush()
        # 调用节点更新
        document_node_service = DocumentNodeService(self.db)
        # 追加文档id
        temp_document_in = document_in.model_copy(update={"id": document.id})
        document_node_service.create_node(temp_document_in, document_in.parent_id)
        self.db.commit()
        # 构建文档内容(这里调用nodejs服务构建一个默认的空的流和json， 注意：一定要先commit,确保事务完成，否则node连接会等待此事务完成)
        self.create_default_content(document.id)
        return document

    def get_by_id_or_slug(self, identifier: str) -> Document:
        """通过id或短链获取文档"""
        document = (
            self.db.query(Document)
            .filter(
                (Document.id == identifier) | (Document.slug == identifier),
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

    def _sync_title_by_nodejs(self, document_id: str, new_title: str):
        """通过nodejs服务同步标题信息（目前未加鉴权）"""
        try:
            nodejs_service_url = settings.NODEJS_SERVICE_URL
            url = f"{nodejs_service_url}/document-content/sync-title"
            payload = {
                "documentId": document_id,
                "newTitle": new_title,
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                logger.info(f"Sync title by nodejs success:title={new_title}")
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Sync title by nodejs failed:title={new_title},error={e}",
                exc_info=True,
            )
        except Exception as e:
            logger.error(f"Sync title by nodejs failed:title={new_title},error={e}")

    def update_by_id_or_slug(
        self, identifier: str, updated_document: DocumentUpdate
    ) -> Document:
        """通过id或短链更新文档"""
        # 调用节点更新
        document_service = DocumentService(self.db)
        document = document_service.get_by_id_or_slug(identifier)
        document_node_service = DocumentNodeService(self.db)
        document_node = document_node_service.get_node_by_document_id(document.id)
        old_name = document.name
        # 同步node表的title
        document_node.title = updated_document.name
        document.name = updated_document.name
        # 如果更新了名称（外层触发,内层会触发协作），则调用node服务更新标题
        print("updated_document.trigger", updated_document.trigger)
        self.db.commit()
        self.db.refresh(document)
        if (
            updated_document.name
            and old_name != updated_document.name
            and updated_document.trigger == "outer"
        ):
            self._sync_title_by_nodejs(document.id, updated_document.name)

        return document

    def get_content(self, document_id: str) -> str:
        """获取文档内容"""
        document_content = (
            self.db.query(DocumentContent)
            .filter(DocumentContent.document_id == document_id)
            .first()
        )
        return document_content.node_json

    def delete_by_id_or_slug(self, identifier: str) -> None:
        """通过id或短链删除文档(这里会同步删除node节点和内容)"""
        document = self.get_by_id_or_slug(identifier)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
            )
        self.db.delete(document)
        self.db.commit()
        return None
