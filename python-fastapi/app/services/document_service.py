"""文档服务"""

from __future__ import annotations
from app.models.document import Document, DocumentContent
from fastapi import HTTPException, status
from fastapi.responses import Response
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentRouteContext,
)
from typing import List, Literal, Optional
from sqlalchemy.orm import Session, joinedload
from app.services.document_node_service import DocumentNodeService
from app.services.resource_grant_service import ResourceGrantService
from app.models.document_node import DocumentNode
from app.models.user import User
from app.core.config import settings
import secrets
import string
import httpx
import logging
from sqlalchemy import func, or_
from app.services.base_service import BaseService
from app.services.permission_service import PermissionService
from app.common.enums import (
    DocumentType,
    DocumentImportFormat,
    DocumentExportFormat,
    SpaceType,
    PermissionScopeType,
    ResourceRole,
    ResourceType,
    DocumentVisibility,
    resource_role_name,
    KnowledgeAbility,
)
from app.services.permission_group_service import PermissionGroupService
from app.schemas.permission_group import PermissionGroupCreate
from app.repositories.document_repository import DocumentRepository
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
        self.resource_grant_service = ResourceGrantService(db)
        self.permission_service = PermissionService(db)
        self.document_repository = DocumentRepository(db)

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
        # 创建文档创建者授权
        if document_in.user_id is None:
            raise ValueError("文档创建者用户id不能为空")
        self.permission_service.assert_knowledge_ability(
            user_id=document_in.user_id,
            identifier=document_in.knowledge_id,
            ability=KnowledgeAbility.CREATE_DOCUMENT,
        )
        temp_slug = self._generate_slug()
        while self.document_repository.exists_slug(
            knowledge_id=document_in.knowledge_id, slug=temp_slug
        ):
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
        # 文档创建者不产生永久授权，权限由知识库继承或文档直接授权决定
        # 创建默认权限组(追加2个角色权限)
        for role in (
            ResourceRole.EDIT,
            ResourceRole.READ,
        ):
            permission_group_service = PermissionGroupService(self.db)
            permission_group_service.create_permission_group(
                # 权限组名称: 文档名称(文档短链)-角色名称
                PermissionGroupCreate(
                    name=f"{document.name}({document.slug})-{resource_role_name[role.value]}",
                    role_key=role.value,
                    scope_type=PermissionScopeType.DOCUMENT,
                    scope_id=document.id,
                )
            )
        # 调用节点更新
        document_node_service = DocumentNodeService(self.db)
        document_node = document_node_service.create_document_node(
            document=document,
            parent_id=document_in.parent_id,
            commit=False,
        )
        self.db.commit()
        self.db.refresh(document_node)
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
            "X-Request-Id": str(uuid.uuid4()),
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

    def _export_content_by_nodejs(
        self, document_id: str, format: DocumentExportFormat, fileName: str
    ) -> dict:
        """通过nodejs服务导出文档内容(会返回文件流)"""
        nodejs_service_url = settings.NODEJS_SERVICE_URL
        url = f"{nodejs_service_url}/document-io/export"
        headers = {
            "X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN,
            "X-Request-Id": str(uuid.uuid4()),
        }
        payload = {
            "documentId": document_id,
            "format": format.value,
            "fileName": fileName,
        }
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()

        out_headers = {}
        if cd := response.headers.get("Content-Disposition"):
            out_headers["Content-Disposition"] = cd
        media_type = response.headers.get("Content-Type") or "application/octet-stream"

        return Response(
            content=response.content, headers=out_headers, media_type=media_type
        )

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
    ) -> DocumentNode:
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

    def export_document(
        self, document_id: str, format: DocumentExportFormat
    ) -> Response:
        """导出文档"""
        document = self.get_by_id_or_slug(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
            )
        # 文档名作为导出的文件名
        fileName = f"{document.name}"

        return self._export_content_by_nodejs(document_id, format, fileName)

    def get_list_by_knowledge_id(
        self, *, knowledge_id: str, user_id: int
    ) -> List[Document]:
        """通过知识库id获取文档列表"""
        documents = self.document_repository.list_active_by_knowledge(
            knowledge_id=knowledge_id
        )
        return self.permission_service.filter_readable_documents(
            user_id=user_id, documents=documents
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
            permission_group_service.delete_permission_group_by_scope(
                scope_type=PermissionScopeType.DOCUMENT,
                scope_id=document.id,
            )
            self.resource_grant_service.delete_resource_grants(
                resource_type=ResourceType.DOCUMENT,
                resource_id=document.id,
            )
            self.db.delete(document)
        # 这里同步删除节点
        document_node_service.delete_by_document_id(document.id, auto_commit=False)
        self.db.commit()
        return None

    def _build_document_path(
        self, *, scope_slug: str, knowledge_slug: str, document_slug: str
    ) -> str:
        """构建文档路径"""
        return (
            f"/{scope_slug}" f"/knowledge/{knowledge_slug}" f"/document/{document_slug}"
        )

    def _build_space_origin(self, *, space_domain: Optional[str]) -> str:
        if space_domain:
            return f"{settings.PUBLIC_SCHEME}://{space_domain}.{settings.PUBLIC_ROOT_DOMAIN}"
        return f"{settings.PUBLIC_SCHEME}://{settings.PUBLIC_ROOT_DOMAIN}"

    def _resolve_document_scope_slug(self, *, knowledge: Knowledge) -> str:
        """获取文档短链"""
        if knowledge.team_id is not None:
            if not knowledge.team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="团队不存在"
                )
            return knowledge.team.slug
        elif knowledge.space.type == SpaceType.PERSONAL:
            if not knowledge.creator:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="无创建者用户名"
                )
            return knowledge.creator.username
        else:
            if not knowledge.space.public_area_slug:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="空间公共区域短链不存在",
                )
            return knowledge.space.public_area_slug

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
                Space.type.label("space_type"),
                Space.public_area_slug.label("public_area_slug"),
                User.username.label("creator_username"),
            )
            .join(Knowledge, Document.knowledge_id == Knowledge.id)
            .join(Space, Knowledge.space_id == Space.id)
            .outerjoin(Team, Knowledge.team_id == Team.id)
            .filter(Document.deleted_at.is_(None))
            .join(User, Knowledge.creator_id == User.id)
            .filter(Document.id.in_(document_ids))
            .all()
        )
        result: dict[str, str] = {}
        for row in rows:
            if row.team_slug:
                scope_slug = row.team_slug
            elif row.space_type == SpaceType.PERSONAL.value:
                scope_slug = row.creator_username
            else:
                scope_slug = row.public_area_slug
            path = self._build_document_path(
                scope_slug=scope_slug,
                knowledge_slug=row.knowledge_slug,
                document_slug=row.document_slug,
            )
            origin = self._build_space_origin(space_domain=row.space_domain)
            # 构建文档相关链接
            result[row.document_id] = f"{origin}{path}"
        return result

    def get_document_route_context(self, document_id: str) -> DocumentRouteContext:
        """获取文档路由上下文(主要是和当前文档访问相关)"""

        document_full_info = (
            self.get_active_query()
            .filter(Document.id == document_id)
            .options(
                joinedload(Document.knowledge).joinedload(Document.knowledge.creator),
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
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )
        team = knowledge.team

        return DocumentRouteContext(
            document_id=document_full_info.id,
            document_name=document_full_info.name,
            document_slug=document_full_info.slug,
            knowledge_id=knowledge.id,
            knowledge_name=knowledge.name,
            knowledge_slug=knowledge.slug,
            team_id=team.id if team else None,
            team_name=team.name if team else None,
            team_slug=team.slug if team else None,
            space_id=knowledge.space_id,
            space_domain=knowledge.space.domain,
            scope_slug=self._resolve_document_scope_slug(knowledge=knowledge),
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
                joinedload(Document.knowledge).joinedload(Knowledge.creator),
                joinedload(Document.knowledge).joinedload(Knowledge.space),
                joinedload(Document.knowledge).joinedload(Knowledge.team),
            )
            .all()
        )
        result: dict[str, DocumentRouteContext] = {}
        for info in document_full_infos:
            knowledge = info.knowledge
            team = knowledge.team if knowledge else None

            if not knowledge:
                continue
            result[info.id] = DocumentRouteContext(
                document_id=info.id,
                document_name=info.name,
                document_slug=info.slug,
                knowledge_id=info.knowledge_id,
                knowledge_name=knowledge.name,
                knowledge_slug=knowledge.slug,
                team_id=team.id if team else None,
                team_name=team.name if team else None,
                team_slug=team.slug if team else None,
                space_id=knowledge.space_id,
                space_domain=knowledge.space.domain,
                scope_slug=self._resolve_document_scope_slug(knowledge=knowledge),
            )
        return result

    def update_visibility(
        self,
        document: Document,
        visibility: DocumentVisibility,
        operator_id: int,
    ) -> bool:
        """更新文档可见范围"""
        knowledge = document.knowledge
        if knowledge is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档所属知识库不存在"
            )
        if (
            visibility == DocumentVisibility.SPACE
            and knowledge.space.type != SpaceType.ORGANIZATION
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="个人空间不能设置为空间成员可见",
            )
        old_visibility = DocumentVisibility(document.visibility)
        if old_visibility == visibility:
            return True
        document.visibility = visibility.value
        self.resource_grant_service.sync_document_visibility_policy_grants(
            document=document,
            old_visibility=old_visibility,
            new_visibility=visibility,
            operator_id=operator_id,
        )
        self.db.commit()
        return True

    def get_context_users(
        self, *, document_id: str, keyword: str | None = None
    ) -> List[User]:
        """查询当前文档最终具有读取能力的上下文用户"""
        document = self.document_repository.get_active_by_id_or_slug(document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
            )
        # 收窄用户范围
        candidate_user_ids = self.resource_grant_service.list_document_context_user_ids(
            document=document
        )
        if not candidate_user_ids:
            return []
        # 进一步进行权限过滤（查找可读的权限）
        readable_user_ids = self.permission_service.filter_document_readable_user_ids(
            document=document, user_ids=candidate_user_ids
        )
        if not readable_user_ids:
            return []
        # 查询用户
        query = self.db.query(User).filter(
            User.id.in_(readable_user_ids), User.deleted_at.is_(None)
        )

        normalized_keyword = (keyword or "").lower().strip()
        if normalized_keyword:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{normalized_keyword}%"),
                    User.nickname.ilike(f"%{normalized_keyword}%"),
                )
            )
        return query.order_by(User.id.asc()).all()
