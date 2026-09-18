"""资源访问申请服务"""

from datetime import datetime
from app.models.resource_access_request import ResourceAccessRequest
from sqlalchemy.orm import Session
from app.common.utils import is_duplicate_on
from app.services.resource_grant_service import ResourceGrantService
from fastapi import HTTPException
from app.common.enums import (
    GrantSource,
    PrincipalType,
    ResourceType,
    AccessRequestStatus,
    ResourceRole,
    PrincipalRole,
)
from typing import Optional
from sqlalchemy.exc import IntegrityError
from app.models.knowledge import Knowledge
from app.models.document import Document
from app.schemas.resource_access_request import (
    ResourceAccessRequestListItem,
    ResourceAccessRequestQuery,
)
from app.common.pagination import paginate_response
from app.schemas.response import PaginationResponse

from app.repositories.resource_access_request_repository import (
    ResourceAccessRequestRepository,
)
from app.repositories.document_repository import DocumentRepository
from app.repositories.knowledge_repository import KnowledgeRepository


class ResourceAccessRequestService:
    """资源访问申请服务(知识库，文档)"""

    PENDING_KEY_CONSTRAINT = "uq_resource_access_request_pending_key"

    def __init__(self, db: Session):
        self.db = db

        self.request_repository = ResourceAccessRequestRepository(db)
        self.document_repository = DocumentRepository(db)
        self.knowledge_repository = KnowledgeRepository(db)

        self.resource_grant_service = ResourceGrantService(db)

    @staticmethod
    def _build_pending_key(
        *, resource_type: ResourceType, resource_id: str, applicant_user_id: int
    ) -> str:
        """生成待审批幂等键"""
        return f"{resource_type.value}:{resource_id}:{applicant_user_id}"

    def get_by_id(
        self, request_id: str, *, for_update: bool = False
    ) -> ResourceAccessRequest | None:
        """根据ID获取资源访问申请（审批单）"""
        return self.request_repository.get_by_id(request_id, for_update=for_update)

    def get_by_id_or_404(
        self, request_id: str, *, for_update: bool = False
    ) -> ResourceAccessRequest:
        """根据ID获取资源访问申请（审批单），不存在则抛出404异常"""
        request = self.get_by_id(request_id, for_update=for_update)
        if request is None:
            raise HTTPException(
                status_code=404, detail="Resource access request not found"
            )
        return request

    def get_pending_request(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        applicant_user_id: int,
        for_update: bool = False,
    ) -> ResourceAccessRequest | None:
        """获取用户对指定资源正在进行的审批单"""
        pending_key = self._build_pending_key(
            resource_type=resource_type,
            resource_id=resource_id,
            applicant_user_id=applicant_user_id,
        )
        return self.request_repository.get_pending(
            pending_key=pending_key,
            for_update=for_update,
        )

    def get_requests_by_resource(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        query_in: ResourceAccessRequestQuery,
    ) -> PaginationResponse[ResourceAccessRequestListItem]:
        """获取指定资源的访问申请列表"""
        items, total, has_more = self.request_repository.paginate_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
            status=query_in.status,
            page=query_in.page,
            page_size=query_in.page_size,
        )
        items = [ResourceAccessRequestListItem.model_validate(item) for item in items]
        return paginate_response(
            items=items,
            total=total,
            has_more=has_more,
            pagination_query=query_in,
        )

    def get_requests_by_applicant(
        self,
        *,
        applicant_user_id: int,
        query_in: ResourceAccessRequestQuery,
    ) -> PaginationResponse[ResourceAccessRequestListItem]:
        """获取用户自己发起的访问申请列表"""
        items, total, has_more = self.request_repository.paginate_by_applicant(
            applicant_user_id=applicant_user_id,
            status=query_in.status,
            page=query_in.page,
            page_size=query_in.page_size,
        )
        items = [ResourceAccessRequestListItem.model_validate(item) for item in items]
        return paginate_response(
            items=items,
            total=total,
            has_more=has_more,
            pagination_query=query_in,
        )

    def ensure_pending_request(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        applicant_user_id: int,
        requested_role: ResourceRole,
        invitation_id: Optional[str] = None,
        apply_message: Optional[str] = None,
    ) -> ResourceAccessRequest:
        """确保用户对指定资源有一条待审批的审批单，如果之前的申请已经结束，则会创建新的审批单"""
        self.resource_grant_service.assert_assignable_role(
            resource_type=resource_type,
            resource_role=requested_role,
        )
        pending_request = self.get_pending_request(
            resource_type=resource_type,
            resource_id=resource_id,
            applicant_user_id=applicant_user_id,
        )
        if pending_request is not None:
            return pending_request
        pending_key = self._build_pending_key(
            resource_type=resource_type,
            resource_id=resource_id,
            applicant_user_id=applicant_user_id,
        )
        access_request = ResourceAccessRequest(
            resource_type=resource_type.value,
            resource_id=resource_id,
            applicant_user_id=applicant_user_id,
            requested_role=requested_role.value,
            invitation_id=invitation_id,
            apply_message=apply_message,
            pending_key=pending_key,
        )
        try:
            with self.db.begin_nested():
                self.request_repository.add(access_request)
                self.request_repository.flush()
            return access_request
        except IntegrityError as exc:
            if not is_duplicate_on(exc, self.PENDING_KEY_CONSTRAINT):
                raise
            # 并发请求插入了相同的pending_key，需要重新查询
            pending_request = self.get_pending_request(
                resource_type=resource_type,
                resource_id=resource_id,
                applicant_user_id=applicant_user_id,
                for_update=True,
            )
            if pending_request is None:
                # 非pending_key唯一性冲突
                raise
            return pending_request

    def _get_resource(
        self, *, resource_type: ResourceType, resource_id: str
    ) -> Knowledge | Document:
        """获取资源"""
        if resource_type == ResourceType.KNOWLEDGE:
            resource = self.knowledge_repository.get_active_by_id(resource_id)
        elif resource_type == ResourceType.DOCUMENT:
            resource = self.document_repository.get_active_by_id(resource_id)
        else:
            raise HTTPException(status_code=422, detail="不支持的申请资源类型")
        if resource is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        return resource

    def _resolve_existing_role(
        self,
        *,
        user_id: int,
        resource_type: ResourceType,
        resource: Knowledge | Document,
    ) -> ResourceRole | None:
        """解析用户对该资源的最终角色"""
        if resource_type == ResourceType.KNOWLEDGE:
            return self.resource_grant_service.resolve_granted_knowledge_role(
                user_id=user_id,
                knowledge=resource,
            )
        # 文档最终角色依赖知识库，需要取最高级
        knowledge_role = self.resource_grant_service.resolve_granted_knowledge_role(
            user_id=user_id,
            knowledge=resource.knowledge,
        )

        document_role = self.resource_grant_service.resolve_granted_document_role(
            user_id=user_id,
            document=resource,
        )

        roles = [role for role in (knowledge_role, document_role) if role is not None]
        return self.resource_grant_service.get_highest_role(roles)

    def approve_request(
        self,
        *,
        request_id: str,
        reviewer_id: int,
    ) -> ResourceAccessRequest:
        """审批通过访问申请，调用方负责校验审批权限和提交事务"""
        # 开启锁防止并发审批
        access_request = self.get_by_id_or_404(request_id, for_update=True)
        if access_request.status == AccessRequestStatus.APPROVED.value:
            return access_request
        if access_request.status != AccessRequestStatus.PENDING.value:
            raise HTTPException(status_code=409, detail="申请状态不正确，不能通过")
        resource_type = ResourceType(access_request.resource_type)
        requested_role = ResourceRole(access_request.requested_role)
        self.resource_grant_service.assert_assignable_role(
            resource_type=resource_type,
            resource_role=requested_role,
        )
        resource = self._get_resource(
            resource_type=resource_type, resource_id=access_request.resource_id
        )
        existing_role = self._resolve_existing_role(
            user_id=access_request.applicant_user_id,
            resource_type=resource_type,
            resource=resource,
        )

        # 审批期间，如果用户被拉到了团队/空间/或者直接授权（获得了更高级的权限，则不重复写入低的grant）
        if not self.resource_grant_service.role_covers(existing_role, requested_role):
            # 插入新的grant
            grant = self.resource_grant_service.upsert_grant(
                resource_type=resource_type,
                resource_id=access_request.resource_id,
                principal_id=access_request.applicant_user_id,
                principal_type=PrincipalType.USER,
                # 授权主体是具体用户
                principal_role=PrincipalRole.NONE,
                resource_role=requested_role,
                source=GrantSource.ACCESS_REQUEST,
                created_by=reviewer_id,
            )
            if grant is None:
                raise RuntimeError("审批授权失败")
        # 更新审批单状态
        access_request.status = AccessRequestStatus.APPROVED.value
        access_request.reviewed_by = reviewer_id
        access_request.reviewed_at = datetime.now()
        # 释放pending唯一键
        access_request.pending_key = None
        self.request_repository.flush()
        return access_request

    def reject_request(
        self, *, request_id: str, reviewer_id: int
    ) -> ResourceAccessRequest:
        """拒绝申请(直接改状态就行，不用考虑授权)"""
        access_request = self.get_by_id_or_404(request_id, for_update=True)
        if access_request.status == AccessRequestStatus.REJECTED.value:
            return access_request
        if access_request.status != AccessRequestStatus.PENDING.value:
            raise HTTPException(status_code=409, detail="申请状态不正确，不能拒绝")
        access_request.status = AccessRequestStatus.REJECTED.value
        access_request.reviewed_by = reviewer_id
        access_request.reviewed_at = datetime.now()

        access_request.pending_key = None
        self.request_repository.flush()
        return access_request

    def cancel_request(self, *, request_id: str, applicant_user_id: int):
        """申请人主动取消"""
        access_request = self.get_by_id_or_404(request_id, for_update=True)
        if access_request.applicant_user_id != applicant_user_id:
            raise HTTPException(status_code=403, detail="无权限其他用户的申请")
        if access_request.status == AccessRequestStatus.CANCELLED.value:
            return access_request
        if access_request.status != AccessRequestStatus.PENDING.value:
            raise HTTPException(status_code=409, detail="当前申请状态不允许取消")

        access_request.status = AccessRequestStatus.CANCELLED.value
        access_request.reviewed_by = None
        access_request.reviewed_at = None
        access_request.pending_key = None
        self.request_repository.flush()
        return access_request

    def cancel_pending_if_exists(
        self, *, resource_type: ResourceType, resource_id: str, applicant_user_id: int
    ) -> ResourceAccessRequest | None:
        """关闭失去业务意义的待审批的申请"""
        pending_request = self.get_pending_request(
            resource_type=resource_type,
            resource_id=resource_id,
            applicant_user_id=applicant_user_id,
            for_update=True,
        )
        if pending_request is None:
            return None
        pending_request.status = AccessRequestStatus.CANCELLED.value
        pending_request.reviewed_by = None
        pending_request.reviewed_at = None
        pending_request.pending_key = None
        self.request_repository.flush()
        return pending_request
