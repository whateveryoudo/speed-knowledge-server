"""知识库邀请链接服务"""

from fastapi import HTTPException
from app.models.invitation import Invitation
from app.models.knowledge import Knowledge
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.document import Document
from app.models.knowledge import Knowledge
from app.models.resource_access_request import ResourceAccessRequest
from app.common.enums import (
    InvitationStatus,
    ResourceRole,
    CollaborateResourceType,
    ResourceType,
    AccessRequestStatus,
    PrincipalType,
    PrincipalRole,
    GrantSource,
)
from app.services.resource_grant_service import ResourceGrantService

from app.schemas.invitation import (
    InvitationValidInfo,
    InvitationResponse,
    InvitationBase,
    InvitationJoinResponse,
    InvitationJoinState,
)
from typing import Optional
from app.common.utils import isUUID
import secrets
import string

alphabet = string.ascii_letters + string.digits


class InvitationService:
    """知识库邀请链接服务"""

    def __init__(self, db: Session):
        self.db = db
        self.resource_grant_service = ResourceGrantService(db)

    def _get_invited_resource(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
    ) -> Knowledge | Document:
        """获取邀请的资源"""
        if resource_type == ResourceType.KNOWLEDGE:
            resource = (
                self.db.query(Knowledge)
                .filter(Knowledge.id == resource_id, Knowledge.deleted_at.is_(None))
                .first()
            )
        else:
            resource = (
                self.db.query(Document)
                .options(
                    joinedload(Document.knowledge).joinedload(Knowledge.team),
                    joinedload(Document.knowledge).joinedload(Knowledge.space),
                )
                .filter(Document.id == resource_id, Document.deleted_at.is_(None))
                .first()
            )
        if resource is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        return resource

    def _get_resource_name(self, resource: Knowledge | Document) -> str:
        """获取资源名称"""
        return resource.name

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
            user_id=user_id, knowledge=resource
        )
        document_role = self.resource_grant_service.resolve_granted_document_role(
            user_id=user_id, document=resource
        )
        roles = [role for role in (knowledge_role, document_role) if role is not None]

        return self.resource_grant_service.get_highest_role(roles)

    def _get_pending_request(
        self,
        *,
        resource_type: ResourceType,
        resource_id: str,
        applicant_user_id: int,
    ) -> ResourceAccessRequest | None:
        """获取待处理的请求"""
        return (
            self.db.query(ResourceAccessRequest)
            .filter(
                ResourceAccessRequest.resource_type == resource_type,
                ResourceAccessRequest.resource_id == resource_id,
                ResourceAccessRequest.applicant_user_id == applicant_user_id,
                ResourceAccessRequest.status == AccessRequestStatus.PENDING.value,
            )
            .first()
        )

    def join_invitation(
        self,
        *,
        token: str,
        applicant_user_id: int,
        apply_message: Optional[str],
        submit_request: bool,
        user_id: int,
    ) -> ResourceAccessRequest:
        """加入邀请"""
        invitation = (
            self.db.query(Invitation)
            .filter(
                Invitation.token == token,
                Invitation.status == InvitationStatus.ACTIVE.value,
            )
            .with_for_update()
            .first()
        )
        if invitation is None:
            raise HTTPException(status_code=404, detail="邀请不存在或已失效")
        resource = self._get_invited_resource(
            resource_type=ResourceType(invitation.resource_type),
            resource_id=invitation.resource_id,
        )
        resource_name = self._get_resource_name(resource)
        resource_type = ResourceType(invitation.resource_type)
        offered_role = ResourceRole(invitation.role)
        existing_role = self._resolve_existing_role(
            user_id=user_id,
            resource_type=resource_type,
            resource=resource,
        )
        if self.resource_grant_service.role_covers(existing_role, offered_role):
            # 已经通过授权(直接授权/空间/团队继承获得同等或者更高级的角色)
            return InvitationJoinResponse(
                state=InvitationJoinState.EFFECTIVE,
                invitation_id=invitation.id,
                resource_type=resource_type,
                resource_id=invitation.resource_id,
                resource_name=resource_name,
                offered_role=offered_role,
                effective_role=existing_role,
                need_approval=invitation.need_approval,
                request_id=None,
            )
        pending_request = self._get_pending_request(
            resource_type=resource_type,
            resource_id=invitation.resource_id,
            applicant_user_id=applicant_user_id,
        )
        if pending_request is not None:
            return InvitationJoinResponse(
                state=InvitationJoinState.PENDING,
                invitation_id=invitation.id,
                resource_type=resource_type,
                resource_id=invitation.resource_id,
                resource_name=resource_name,
                offered_role=offered_role,
                effective_role=existing_role,
                need_approval=invitation.need_approval,
                request_id=pending_request.id,
            )
        if invitation.need_approval:
            if not submit_request:
                # 首次进入，直接返回邀请信息
                return InvitationJoinResponse(
                    state=InvitationJoinState.APPROVAL_REQUIRED,
                    invitation_id=invitation.id,
                    resource_type=resource_type,
                    resource_id=invitation.resource_id,
                    resource_name=resource_name,
                    offered_role=offered_role,
                    effective_role=existing_role,
                    need_approval=invitation.need_approval,
                    request_id=None,
                )
            # 点击提交申请
            access_request = ResourceAccessRequest(
                resource_type=resource_type.value,
                resource_id=invitation.resource_id,
                applicant_user_id=applicant_user_id,
                message=apply_message,
                invitation_id=invitation.id,
                # 复制邀请角色
                requested_role=offered_role.value,
                apply_message=apply_message,
                status=AccessRequestStatus.PENDING.value,
            )
            self.db.add(access_request)
            self.db.commit()
            self.db.refresh(access_request)
            return InvitationJoinResponse(
                state=InvitationJoinState.PENDING,
                invitation_id=invitation.id,
                resource_type=resource_type,
                resource_id=invitation.resource_id,
                resource_name=resource_name,
                offered_role=offered_role,
                need_approval=True,
                request_id=access_request.id,
            )
        # 不需要审批，直接创建 grant
        grant = self.resource_grant_service.update_grant(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=invitation.resource_id,
            role=offered_role,
            principal_type=PrincipalType.USER,
            principal_id=applicant_user_id,
            prinical_role=PrincipalRole.NONE,
            resource_role=offered_role,
            source=GrantSource.INVITATION,
            created_by=invitation.invitate_id,
        )
        if grant is None:
            raise RuntimeError("创建授权失败")
        self.db.commit()
        self.db.refresh(grant)

        return InvitationJoinResponse(
            state=InvitationJoinState.EFFECTIVE,
            invitation_id=invitation.id,
            resource_type=resource_type,
            resource_id=invitation.resource_id,
            resource_name=resource_name,
            offered_role=offered_role,
            effective_role=offered_role,
            need_approval=False,
            request_id=None,
            grant_id=grant.id,
        )

    def _generate_token(self) -> str:
        """生成邀请token"""
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def update_invitation_token(
        self, invitation_id: str, invitation_update: InvitationBase
    ) -> InvitationResponse:
        """更新邀请链接token信息"""
        has_active_record = (
            self.db.query(Invitation).filter(Invitation.id == invitation_id).first()
        )
        if has_active_record is None:
            raise HTTPException(status_code=404, detail="邀请链接不存在")
        update_data = invitation_update.model_dump(exclude_unset=True, exclude={"id"})
        for field_name, field_value in update_data.items():
            if field_value is not None:
                setattr(
                    has_active_record,
                    field_name,
                    field_value.value if hasattr(field_value, "value") else field_value,
                )
        self.db.commit()
        self.db.refresh(has_active_record)
        return has_active_record

    def reset_invitation_token(self, invitation_id: str) -> InvitationResponse:
        """重置知识库邀请链接token信息"""
        has_active_record = (
            self.db.query(Invitation).filter(Invitation.id == invitation_id).first()
        )
        if has_active_record is None:
            return None
        # 复制一份已有的记录
        record_dict = {
            k: v
            for k, v in has_active_record.__dict__.items()
            if not k.startswith("_") and k not in ["id", "created_at", "updated_at"]
        }
        record_dict["token"] = self._generate_token()
        record_dict["status"] = InvitationStatus.ACTIVE.value
        # 历史改为已撤销
        has_active_record.status = InvitationStatus.REVOKED.value
        new_record = Invitation(**record_dict)
        self.db.add(new_record)
        self.db.commit()
        self.db.refresh(new_record)
        return new_record

    def get_invitation_token(
        self, resource_type: str, resource_identifier: str, invitate_user_id: int
    ) -> InvitationResponse:
        """获取邀请链接token信息(知识库/文档)"""
        if resource_type == CollaborateResourceType.KNOWLEDGE.value:
            target_model = Knowledge
        else:
            target_model = Document
        # 通过slug/id查询资源
        resource_row = (
            self.db.query(target_model)
            .filter(
                (target_model.slug == resource_identifier)
                | (target_model.id == resource_identifier)
            )
            .first()
        )
        if resource_row is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        resource_id = resource_row.id
        if resource_id is None:
            raise HTTPException(status_code=404, detail="资源不存在")
        print(f"resource_id: {resource_id}")
        # 逻辑：先查找active记录，没有的话则初始化一条记录
        has_active_record = (
            self.db.query(Invitation)
            .filter(
                Invitation.status == InvitationStatus.ACTIVE.value,
                or_(
                    Invitation.document_id == resource_id,
                    Invitation.knowledge_id == resource_id,
                ),
            )
            .first()
        )

        # 只有没有 active 记录时才生成 token
        if has_active_record is None:
            temp_token = self._generate_token()
            while (
                self.db.query(Invitation).filter(Invitation.token == temp_token).first()
            ):
                temp_token = self._generate_token()
            if resource_type == CollaborateResourceType.KNOWLEDGE.value:
                has_active_record = Invitation(
                    knowledge_id=resource_id,
                    invitate_user_id=invitate_user_id,
                    invitate_type=resource_type,
                    token=temp_token,
                )
            else:
                has_active_record = Invitation(
                    document_id=resource_id,
                    knowledge_id=resource_row.knowledge_id,  # 同时存入所属知识库id
                    invitate_user_id=invitate_user_id,
                    invitate_type=resource_type,
                    token=temp_token,
                )
            self.db.add(has_active_record)
            self.db.commit()
            self.db.refresh(has_active_record)

        return has_active_record

    def get_invitation_valid_info(self, token: str) -> InvitationValidInfo:
        """获取邀请链接token信息(这里会进行一些封装)"""
        print(f"token: {token}")
        has_active_record = (
            self.db.query(
                Invitation,
                Knowledge.name.label("knowledge_name"),
                Document.name.label("document_name"),
            )
            .outerjoin(Knowledge, Invitation.knowledge_id == Knowledge.id)
            .outerjoin(Document, Invitation.document_id == Document.id)
            .filter(
                Invitation.token == token,
                Invitation.status == InvitationStatus.ACTIVE.value,
            )
            .first()
        )
        if has_active_record is None:
            return None
        invitation, knowledge_name, document_name = has_active_record
        return InvitationValidInfo(
            status=invitation.status,
            role=invitation.role,
            knowledge_id=invitation.knowledge_id,
            document_id=invitation.document_id,
            knowledge_name=knowledge_name,
            invitate_type=invitation.invitate_type,
            document_name=document_name,
            need_approval=invitation.need_approval,
        )

    def get_invitation_by_token(self, token: str) -> InvitationResponse:
        """获取知识库邀请链接token信息"""
        has_active_record = (
            self.db.query(Invitation)
            .filter(
                Invitation.token == token,
                Invitation.status == InvitationStatus.ACTIVE.value,
            )
            .first()
        )

        return has_active_record
