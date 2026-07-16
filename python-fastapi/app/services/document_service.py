"""文档服务"""

from __future__ import annotations
from app.models.document import Document, DocumentContent
from fastapi import HTTPException, status
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentRouteContext,
)
from app.schemas.document_node import DocumentNodeCreate
from typing import List, Literal, Optional
from sqlalchemy.orm import Session, joinedload
from app.services.document_node_service import DocumentNodeService
from app.models.document_node import DocumentNode
from app.services.collaborator_service import CollaboratorService
from app.schemas.collaborator import CollaboratorCreate
from app.models.user import User
from app.models.collaborator import Collaborator
from app.core.config import settings
import secrets
import string
import httpx
import logging
from sqlalchemy import func, or_, and_
from app.services.base_service import BaseService
from app.common.enums import (
    CollaborateResourceType,
    DocumentType,
    DocumentNodeType,
    CollaboratorRole,
    CollaboratorStatus,
    DocumentImportFormat,
)
from app.services.permission_group_service import PermissionGroupService
from app.schemas.permission_group import PermissionGroupCreate
from app.common.enums import collaborator_role_name
from app.models.knowledge import Knowledge
from app.models.space import Space
from app.models.team import Team
import uuid

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
        """构建 document_content：调用 Node create-default（按 document_base.type 写 word/sheet）"""
        try:
            nodejs_service_url = settings.NODEJS_SERVICE_URL
            url = f"{nodejs_service_url}/document-content/create-default"
            payload = {
                "documentId": document_id,
            }
            headers = {
                "X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN,
                "Idempotency-Key": f"create-default:{document_id}",
                "X-Request-Id": str(uuid.uuid4()),
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload, headers=headers)
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

    def create(
        self, document_in: DocumentCreate, *, skip_default_content: bool = False
    ) -> DocumentNode:
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
        # 提取节点创建结构(这里提取为两类，如果是通用文档则设置为文档类型，否则为目录类型)
        node_type = (
            DocumentNodeType.DOC
            if document_in.type in DocumentType
            else DocumentNodeType.TITLE
        )
        document_node = document_node_service.create_node(
            DocumentNodeCreate(
                knowledge_id=document.knowledge_id,
                name=document.name,
                id=document.id,
                type=node_type,
                parent_id=document_in.parent_id,
            )
        )
        self.db.commit()
        # 这里追加判断是否导入默认内容（如果是走导入则跳过）
        if not skip_default_content:
            # 构建文档内容(这里调用nodejs服务构建一个默认的空的流和json， 注意：一定要先commit,确保事务完成，否则node连接会等待此事务完成)
            self.create_default_content(document.id)
        # 这里返回节点信息（不返回文档信息）
        return document_node

    def create_quick_document(
        self, document_in: DocumentCreate
    ) -> DocumentRouteContext | None:
        """创建快速文档"""
        target_document_node = self.create(document_in)
        if not target_document_node.document_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档创建失败"
            )
        return self.get_document_route_context(target_document_node.document_id)

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

    def _import_content_by_nodejs(
        self,
        document_id: str,
        file_bytes: bytes,
        file_name: str,
        content_type: str,
        format: DocumentImportFormat,
        titleHint: str,
        user_id: int,
    ) -> dict:
        """通过nodejs服务导入文档内容(会返回documentId和title)"""
        nodejs_service_url = settings.NODEJS_SERVICE_URL
        url = f"{nodejs_service_url}/document-io/import"
        headers = {
            "X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN,
            "X-Request-Id": str(uuid.uuid4())
        }
        files = {
            "file": (
                file_name,
                file_bytes,
                content_type or "application/octet-stream",
            ),
        }
        payload = {
            "documentId": document_id,
            "format": format.value,
            "titleHint": titleHint,
            # 追加用户id,用于生成附件名称
            "userId": user_id,
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, files=files, data=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Import document by nodejs success:documentId={document_id}")
            body = response.json()
            return body.get("data") or body

    def import_document(
        self,
        *,
        user_id: int,
        knowledge_id: str,
        parent_id: str | None = None,
        file_bytes: bytes,
        file_name: str,
        content_type: str,
        format: DocumentImportFormat,
    ) -> Optional[DocumentNode]:
        """导入文档（成功返回文档树节点）"""
        # 文件名作为文档标题（与正文 title 节点一致）
        placeholder_name = (file_name.rsplit(".", 1)[0] if file_name else "导入文档")[
            :50
        ] or "无标题文档"
        document_node = self.create(
            DocumentCreate(
                user_id=user_id,
                knowledge_id=knowledge_id,
                name=placeholder_name,
                # 后续会有更多类型
                type=DocumentType.WORD,
                parent_id=parent_id,
            ),
            skip_default_content=True,
        )
        document_id = document_node.document_id

        try:
            self._import_content_by_nodejs(
                document_id,
                file_bytes,
                file_name,
                content_type or "application/octet-stream",
                format,
                placeholder_name,
                user_id,
            )
            # 与新建文档一致，返回树节点便于前端挂载

            return document_node
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Import document by nodejs failed:documentId={document_id},error={e}"
            )
            try:
                # 回退删除已经加好的文档数据
                self.delete_by_id_or_slug(document_id, is_soft_delete=False)
            except Exception as e:
                logger.error(
                    f"Rollback delete document failed:documentId={document_id},error={e}"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="导入文档失败",
            )

    def get_list_by_user_id(self, user_id: int) -> List[Document]:
        """通过用户id获取文档列表"""
        return self.db.query(Document).filter(Document.user_id == user_id).all()

    def get_list_by_knowledge_id(self, knowledge_id: str) -> List[Document]:
        """通过知识库id获取文档列表"""
        return (
            self.db.query(Document).filter(Document.knowledge_id == knowledge_id).all()
        )

    def _sync_title_by_nodejs(self, document_id: str, new_title: str):
        """通过nodejs服务同步标题信息（标题同步不做幂等）"""
        try:
            nodejs_service_url = settings.NODEJS_SERVICE_URL
            url = f"{nodejs_service_url}/document-content/sync-title"
            headers = {
                "X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN,
                "X-Request-Id": str(uuid.uuid4()),
            }
            payload = {
                "documentId": document_id,
                "newTitle": new_title,
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info(f"Sync title by nodejs success:title={new_title}")
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Sync title by nodejs failed:title={new_title},error={e}",
                exc_info=True,
            )
        except Exception as e:
            logger.error(f"Sync title by nodejs failed:title={new_title},error={e}")

    def update_title(
        self,
        document_id: str,
        new_title: str,
        *,
        trigger: Literal["outer", "inner"] = "outer",
    ) -> None:
        """更新文档标题(普通文档更新和目录节点更新)"""
        document = self.get_by_id_or_slug(document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
            )
        # 更新文档节点标题
        from app.services.document_node_service import DocumentNodeService

        document_node_service = DocumentNodeService(self.db)
        document_node = document_node_service.get_node_by_document_id(document.id)
        if not document_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档节点不存在"
            )
        old_name = document.name
        # 同步node表的title
        document_node.title = new_title
        document.name = new_title
        self.db.commit()
        if new_title and old_name != new_title and trigger == "outer":
            self._sync_title_by_nodejs(document.id, new_title)

    def update_by_id_or_slug(
        self, identifier: str, updated_document: DocumentUpdate
    ) -> Document:
        """通过id或短链更新文档"""
        document = self.get_by_id_or_slug(identifier)
        if updated_document.name:
            self.update_title(
                document.id, updated_document.name, trigger=updated_document.trigger
            )
        self.db.refresh(document)
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
            # 物理删除(这里会同步删除权限组数据)
            permission_group_service = PermissionGroupService(self.db)
            permission_group_service.delete_permission_group_by_resource(
                CollaborateResourceType.DOCUMENT, document.id
            )
            self.db.delete(document)
        # 这里同步删除节点
        document_node_service.delete_by_document_id(document.id, auto_commit=False)
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
            .options(
                joinedload(Document.knowledge).joinedload(Document.knowledge.space),
                joinedload(Document.knowledge).joinedload(Document.knowledge.team),
            )
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
            document_id=document_full_info.id,
            document_name=document_full_info.name,
            document_slug=document_full_info.slug,
            knowledge_id=document_full_info.knowledge_id,
            knowledge_name=document_full_info.knowledge.name,
            knowledge_slug=document_full_info.knowledge.slug,
            team_id=document_full_info.knowledge.team_id,
            team_name=document_full_info.knowledge.team.name,
            team_slug=document_full_info.knowledge.team.slug,
            space_id=document_full_info.knowledge.space_id,
            space_domain=document_full_info.knowledge.space.domain,
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
            .options(
                joinedload(Document.knowledge).joinedload(Knowledge.space),
                joinedload(Document.knowledge).joinedload(Knowledge.team),
            )
            .all()
        )
        result: dict[str, DocumentRouteContext] = {}
        for info in document_full_infos:
            knowledge = info.knowledge
            team = knowledge.team if knowledge else None

            if not knowledge or not team:
                continue
            result[info.id] = DocumentRouteContext(
                document_id=info.id,
                document_name=info.name,
                document_slug=info.slug,
                knowledge_id=info.knowledge_id,
                knowledge_name=info.knowledge.name,
                knowledge_slug=info.knowledge.slug,
                team_id=info.knowledge.team_id,
                team_name=info.knowledge.team.name,
                team_slug=info.knowledge.team.slug,
                space_id=info.knowledge.space_id,
                space_domain=info.knowledge.space.domain,
            )
        return result

    def get_context_users(
        self, document_id: str, keyword: str | None = None
    ) -> List[User]:
        """查询当前文档下可访问的用户列表"""
        document = self.get_by_id_or_slug(document_id)
        rows = (
            self.db.query(User)
            .join(Collaborator, User.id == Collaborator.user_id)
            .filter(
                User.deleted_at.is_(None),
                Collaborator.status == CollaboratorStatus.ACCEPTED.value,
                or_(
                    and_(
                        Collaborator.document_id == document.id,
                        Collaborator.target_type == CollaborateResourceType.DOCUMENT,
                    ),
                    and_(
                        Collaborator.knowledge_id == document.knowledge_id,
                        Collaborator.target_type == CollaborateResourceType.KNOWLEDGE,
                    ),
                ),
            )
            .distinct(User.id)
        )

        if keyword:
            rows = rows.filter(
                or_(
                    User.username.ilike(f"%{keyword}%"),
                    User.nickname.ilike(f"%{keyword}%"),
                )
            )
        return rows.all()
