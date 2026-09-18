"""知识库、文档邀请链接服务"""

from fastapi import HTTPException
from app.models.resource_invitation import ResourceInvitation
from app.models.knowledge import Knowledge
from sqlalchemy.orm import Session
from app.models.document import Document
from app.common.enums import (
    InvitationStatus,
    ResourceRole,
    ResourceType,
    PrincipalType,
    PrincipalRole,
    GrantSource,
)
from app.services.resource_grant_service import ResourceGrantService
from app.services.resource_access_request_service import ResourceAccessRequestService
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.document_repository import DocumentRepository

from app.schemas.resource_invitation import (
    ResourceInvitationJoinResponse,
    ResourceInvitationJoinState,
    ResourceInvitationCreate,
    ResourceInvitationUpdate,
)
from typing import Optional
import secrets
import string

alphabet = string.ascii_letters + string.digits


class ResourceInvitationService:
    """知识库、文档资源邀请链接服务"""

    def __init__(self, db: Session):
        self.db = db
        # 这里暂时不会去接入repository

        self.knowledge_repository = KnowledgeRepository(db)
        self.document_repository = DocumentRepository(db)

        self.resource_grant_service = ResourceGrantService(db)
        self.access_request_service = ResourceAccessRequestService(db)

    def _generate_token(self) -> str:
        """生成邀请token"""
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def _generate_unique_token(self) -> str:
        """生成唯一的邀请token"""
        while True:
            token = self._generate_token()
            exists = (
                self.db.query(ResourceInvitation)
                .filter(ResourceInvitation.token == token)
                .first()
            )
            if exists is None:
                return token

    def get_by_id_or_404(self, invitation_id: str) -> ResourceInvitation:
        """获取邀请，不存在则抛出404异常"""
        invitation = (
            self.db.query(ResourceInvitation)
            .filter(ResourceInvitation.id == invitation_id)
            .first()
        )
        if invitation is None:
            raise HTTPException(status_code=404, detail="邀请链接不存在")
        return invitation

    def get_by_token(self, token: str) -> ResourceInvitation:
        """根据token获取邀请链接"""
        invitation = (
            self.db.query(ResourceInvitation)
            .filter(
                ResourceInvitation.token == token,
                ResourceInvitation.status == InvitationStatus.ACTIVE.value,
            )
            .first()
        )
        if invitation is None:
            raise HTTPException(status_code=404, detail="邀请链接不存在或已失效")
        return invitation

    def get_by_resource(
        self, *, resource_type: ResourceType, resource_id: str
    ) -> ResourceInvitation | None:
        """根据资源查询邀请配置"""
        return (
            self.db.query(ResourceInvitation)
            .filter(
                ResourceInvitation.resource_type == resource_type.value,
                ResourceInvitation.resource_id == resource_id,
            )
            .first()
        )

    def _get_invited_resource(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
    ) -> Knowledge | Document:
        """获取邀请的资源"""
        if resource_type == ResourceType.KNOWLEDGE:
            resource = self.knowledge_repository.get_active_by_id(resource_id)
        elif resource_type == ResourceType.DOCUMENT:
            resource = self.document_repository.get_active_by_id(resource_id)
        else:
            # 这里编辑区会变灰，但是实际运行做防御性拦截
            raise HTTPException(
                status_code=422, detail=f"不支持的资源类型: {resource_type}"
            )
        if resource is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        return resource

    def create_or_update(
        self, *, invitation_in: ResourceInvitationCreate, inviter_id: int
    ) -> ResourceInvitation:
        """创建或更新邀请配置"""
        # 校验邀请角色是否可授权
        self.resource_grant_service.assert_assignable_role(
            resource_type=invitation_in.resource_type,
            resource_role=invitation_in.offered_role,
        )
        self._get_invited_resource(
            resource_type=invitation_in.resource_type,
            resource_id=invitation_in.resource_id,
        )
        invitation = self.get_by_resource(
            resource_type=invitation_in.resource_type,
            resource_id=invitation_in.resource_id,
        )
        if invitation is None:
            invitation = ResourceInvitation(
                inviter_id=inviter_id,
                resource_type=invitation_in.resource_type.value,
                resource_id=invitation_in.resource_id,
                token=self._generate_unique_token(),
                offered_role=invitation_in.offered_role.value,
                need_approval=invitation_in.need_approval,
                status=InvitationStatus.ACTIVE.value,
            )
            self.db.add(invitation)
        else:
            invitation.inviter_id = inviter_id
            invitation.offered_role = invitation_in.offered_role.value
            invitation.need_approval = invitation_in.need_approval
            invitation.status = InvitationStatus.ACTIVE.value
        self.db.flush()
        return invitation

    def update(
        self,
        *,
        invitation_id: str,
        invitation_update: ResourceInvitationUpdate,
        operator_id: int,
    ) -> ResourceInvitation:
        """更新邀请配置"""
        invitation = self.get_by_id_or_404(invitation_id)
        update_data = invitation_update.model_dump(exclude_unset=True)
        offered_role = update_data.get("offered_role")

        if offered_role is not None:
            self.resource_grant_service.assert_assignable_role(
                resource_type=ResourceType(invitation.resource_type),
                resource_role=ResourceRole(offered_role),
            )
            invitation.offered_role = offered_role.value
        if "need_approval" in update_data:
            invitation.need_approval = update_data["need_approval"]
        invitation_status = update_data.get("status")
        if invitation_status is not None:
            invitation.status = invitation_status.value
        invitation.inviter_id = operator_id
        self.db.flush()
        return invitation

    def reset_token(
        self, *, invitation_id: str, operator_id: int
    ) -> ResourceInvitation:
        """重置token"""
        invitation = self.get_by_id_or_404(invitation_id)
        invitation.token = self._generate_unique_token()
        invitation.status = InvitationStatus.ACTIVE.value
        invitation.inviter_id = operator_id
        self.db.flush()
        return invitation

    def revoke(self, *, invitation_id: str, operator_id: int) -> ResourceInvitation:
        """撤销邀请配置"""
        invitation = self.get_by_id_or_404(invitation_id)
        invitation.status = InvitationStatus.REVOKED.value
        invitation.inviter_id = operator_id
        self.db.flush()
        return invitation

    def _resolve_existing_role(
        self,
        *,
        user_id: int,
        resource_type: ResourceType,
        resource: Knowledge | Document,
    ) -> ResourceRole | None:
        if resource_type == ResourceType.KNOWLEDGE:
            return self.resource_grant_service.resolve_granted_knowledge_role(
                user_id=user_id, knowledge=resource
            )
        # 文档需要考虑知识库继承，和文档本身的授权
        knowledge_role = self.resource_grant_service.resolve_granted_knowledge_role(
            user_id=user_id, knowledge=resource.knowledge
        )
        document_role = self.resource_grant_service.resolve_granted_document_role(
            user_id=user_id, document=resource
        )
        roles = [role for role in (knowledge_role, document_role) if role is not None]

        return self.resource_grant_service.get_highest_role(roles)

    def _build_join_response(
        self,
        *,
        state: ResourceInvitationJoinState,
        invitation: ResourceInvitation,
        resource_name: str,
        effective_role: ResourceRole | None = None,
        request_id: Optional[str] = None,
        grant_id: Optional[str] = None,
    ) -> ResourceInvitationJoinResponse:
        """构建加入邀请响应"""
        return ResourceInvitationJoinResponse(
            state=state,
            invitation_id=invitation.id,
            resource_type=ResourceType(invitation.resource_type),
            resource_id=invitation.resource_id,
            resource_name=resource_name,
            offered_role=ResourceRole(invitation.offered_role),
            effective_role=effective_role,
            need_approval=invitation.need_approval,
            request_id=request_id,
            grant_id=grant_id,
        )

    def join_by_invitation(
        self,
        *,
        token: str,
        applicant_user_id: int,
        apply_message: Optional[str],
        submit_request: bool,
    ) -> ResourceInvitationJoinResponse:
        """加入邀请"""
        # 这里去掉了最开始的锁
        invitation = self.get_by_token(token)
        resource = self._get_invited_resource(
            resource_type=ResourceType(invitation.resource_type),
            resource_id=invitation.resource_id,
        )
        resource_name = resource.name
        resource_type = ResourceType(invitation.resource_type)
        offered_role = ResourceRole(invitation.offered_role)
        self.resource_grant_service.assert_assignable_role(
            resource_type=resource_type,
            resource_role=offered_role,
        )
        existing_role = self._resolve_existing_role(
            user_id=applicant_user_id,
            resource_type=resource_type,
            resource=resource,
        )
        if self.resource_grant_service.role_covers(existing_role, offered_role):
            # 已经通过授权(直接授权/空间/团队继承获得同等或者更高级的角色)
            self.access_request_service.cancel_pending_if_exists(
                resource_type=resource_type,
                resource_id=invitation.resource_id,
                applicant_user_id=applicant_user_id,
            )

            return self._build_join_response(
                state=ResourceInvitationJoinState.EFFECTIVE,
                invitation=invitation,
                resource_name=resource_name,
                effective_role=existing_role,
            )
        if invitation.need_approval:
            pending_request = self.access_request_service.get_pending_request(
                resource_type=resource_type,
                resource_id=invitation.resource_id,
                applicant_user_id=applicant_user_id,
            )
            if pending_request is not None:
                return self._build_join_response(
                    state=ResourceInvitationJoinState.PENDING,
                    invitation=invitation,
                    resource_name=resource_name,
                    request_id=pending_request.id,
                    effective_role=existing_role,
                )
            if not submit_request:
                # 首次进入，直接返回邀请信息
                return self._build_join_response(
                    state=ResourceInvitationJoinState.APPROVAL_REQUIRED,
                    invitation=invitation,
                    resource_name=resource.name,
                    effective_role=existing_role,
                )
            pending_request = self.access_request_service.ensure_pending_request(
                resource_type=resource_type,
                resource_id=invitation.resource_id,
                applicant_user_id=applicant_user_id,
                requested_role=offered_role,
                apply_message=apply_message,
                invitation_id=invitation.id,
            )
            return self._build_join_response(
                state=ResourceInvitationJoinState.PENDING,
                invitation=invitation,
                resource_name=resource_name,
                request_id=pending_request.id,
                effective_role=existing_role,
            )
        # 不需要审批，直接创建 grant
        grant = self.resource_grant_service.upsert_grant(
            resource_type=resource_type,
            resource_id=invitation.resource_id,
            principal_type=PrincipalType.USER,
            principal_id=applicant_user_id,
            principal_role=PrincipalRole.NONE,
            resource_role=offered_role,
            source=GrantSource.INVITATION,
            created_by=invitation.inviter_id,
        )
        if grant is None:
            raise RuntimeError("创建授权失败")

        self.access_request_service.cancel_pending_if_exists(
            resource_type=resource_type,
            resource_id=invitation.resource_id,
            applicant_user_id=applicant_user_id,
        )
        effective_role = self._resolve_existing_role(
            user_id=applicant_user_id,
            resource_type=resource_type,
            resource=resource,
        )
        return self._build_join_response(
            state=ResourceInvitationJoinState.EFFECTIVE,
            invitation=invitation,
            resource_name=resource_name,
            effective_role=effective_role,
            grant_id=grant.id,
        )
