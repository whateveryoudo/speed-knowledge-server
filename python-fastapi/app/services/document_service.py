"""文档服务"""

from __future__ import annotations
from app.models.document import Document, DocumentContent
from fastapi import HTTPException, status
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DragDocumentNodeParams,
    DocumentRouteContext,
)
from typing import List
from sqlalchemy.orm import Session, joinedload
from app.services.document_node_service import DocumentNodeService
from app.services.collaborator_service import CollaboratorService
from app.schemas.collaborator import CollaboratorCreate
from app.core.config import settings
import secrets
import string
import httpx
import logging
from sqlalchemy import func
from app.services.base_service import BaseService
from app.common.enums import CollaborateResourceType
from app.common.enums import CollaboratorRole
from app.services.permission_group_service import PermissionGroupService
from app.schemas.permission_group import PermissionGroupCreate
from app.common.enums import collaborator_role_name
from app.models.knowledge import Knowledge
from app.models.space import Space
from app.models.team import Team

alphabet = string.ascii_letters + string.digits

logger = logging.getLogger(__name__)


class DocumentService(BaseService[Document]):
    """文档服务"""

    def _generate_slug(self) -> str:
        """生成文档短链"""
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def __init__(self, db: Session):
        super().__init__(db, Document)

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
        while self.get_active_query().filter(Document.slug == temp_slug).first():
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
        # 追加默认协作者
        collaborator_service = CollaboratorService(self.db)
        collaborator_service.join_default_collaborator(
            CollaboratorCreate(
                user_id=document_in.user_id,
                document_id=document.id,
                target_type=CollaborateResourceType.DOCUMENT,
            )
        )

        # 创建默认权限组(追加3个角色权限)
        for role in CollaboratorRole:
            permission_group_service = PermissionGroupService(self.db)
            permission_group_service.create_permission_group(
                # 权限组名称: 文档名称(文档短链)-角色名称
                PermissionGroupCreate(
                    name=f"{document.name}({document.slug})-{collaborator_role_name[role.value]}",
                    role=role,
                    target_type=CollaborateResourceType.DOCUMENT,
                    target_id=document.id,
                )
            )
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
            self.get_active_query()
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
        """获取文档信息"""
        document_content = (
            self.db.query(DocumentContent)
            .filter(DocumentContent.document_id == document_id)
            .first()
        )
        return document_content.node_json

    def delete_by_id_or_slug(
        self, identifier: str, is_soft_delete: bool = True
    ) -> None:
        """通过id或短链删除文档(这里会同步删除node节点和内容（物理删除下）)"""
        document = self.get_by_id_or_slug(identifier)
        document_node_service = DocumentNodeService(self.db)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
            )
        # 修改为软删除
        if is_soft_delete:
            document.soft_delete()
        else:
            self.db.delete(document)
        # 这里同步删除节点
        document_node_service.delete_by_document_id(document.id, is_soft_delete)
        self.db.commit()
        return None

    def resolve_document_links_batch(self, document_ids: list[str]) -> dict[str, str]:
        """批量获取文档相关链接(一次join)"""
        print("document_ids", document_ids)
        rows = (
            self.db.query(
                Document.id.label("document_id"),
                Document.slug.label("document_slug"),
                Knowledge.slug.label("knowledge_slug"),
                Team.slug.label("team_slug"),
                Space.domain.label("space_domain"),
            )
            .join(Knowledge, Document.knowledge_id == Knowledge.id)
            .join(Space, Knowledge.space_id == Space.id)
            .join(Team, Knowledge.team_id == Team.id)
            .filter(Document.deleted_at.is_(None))
            .filter(Document.id.in_(document_ids))
            .all()
        )
        result: dict[str, str] = {}
        for r in rows:
            # 构建文档相关链接(个人空间不存在domin)
            result[r.document_id] = (
                f"http://{r.space_domain or settings.DOMAIN}/{r.team_slug or ''}/knowledge/{r.knowledge_slug or ''}/document/{r.document_slug or ''}"
            )
        return result

    def get_document_route_context(self, document_id: str) -> DocumentRouteContext:
        """获取文档路由上下文(主要是和当前文档访问相关)"""
        document_full_info = (
            self.get_active_query()
            .filter(Document.id == document_id)
            .options(joinedload(Document.knowledge).joinedload(Knowledge.team))
            .first()
        )
        if not document_full_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
            )
        knowledge = document_full_info.knowledge
        team = knowledge.team if knowledge else None
        if not knowledge or not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库或团队不存在"
            )
        return DocumentRouteContext(
            doc_id=document_full_info.id,
            doc_name=document_full_info.name,
            doc_slug=document_full_info.slug,
            knowledge_id=document_full_info.knowledge_id,
            knowledge_name=document_full_info.knowledge.name,
            knowledge_slug=document_full_info.knowledge.slug,
            team_id=document_full_info.knowledge.team_id,
            team_name=document_full_info.knowledge.team.name,
            team_slug=document_full_info.knowledge.team.slug,
            space_id=document_full_info.knowledge.space_id,
        )

    def get_document_route_context_multiple(
        self, document_ids: list[str]
    ) -> dict[str, DocumentRouteContext]:
        """批量获取文档路由上下文"""
        if not document_ids:
            return {}
        document_full_infos = (
            self.get_active_query()
            .filter(Document.id.in_(document_ids))
            .options(joinedload(Document.knowledge).joinedload(Knowledge.team))
            .all()
        )
        result: dict[str, DocumentRouteContext] = {}
        for info in document_full_infos:
            knowledge = info.knowledge
            team = knowledge.team if knowledge else None

            if not knowledge or not team:
                continue
            result[info.id] = DocumentRouteContext(
                doc_id=info.id,
                doc_name=info.name,
                doc_slug=info.slug,
                knowledge_id=info.knowledge_id,
                knowledge_name=info.knowledge.name,
                knowledge_slug=info.knowledge.slug,
                team_id=info.knowledge.team_id,
                team_name=info.knowledge.team.name,
                team_slug=info.knowledge.team.slug,
                space_id=info.knowledge.space_id,
            )
        return result
