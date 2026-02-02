"""知识库邀请链接服务"""

from fastapi import HTTPException
from app.models.invitation import Invitation
from app.models.knowledge import Knowledge
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.document import Document
from app.models.knowledge import Knowledge
from app.common.enums import InvitationStatus, CollaborateResourceType
from app.schemas.invitation import (
    InvitationValidInfo,
    InvitationResponse,
    InvitationBase,
)
from app.common.utils import isUUID
import secrets
import string

alphabet = string.ascii_letters + string.digits


class InvitationService:
    """知识库邀请链接服务"""

    def __init__(self, db: Session):
        self.db = db

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
        self, resource_type: str, resource_identifier: str
    ) -> InvitationResponse:
        """获取邀请链接token信息(知识库/文档)"""
        if resource_type == CollaborateResourceType.KNOWLEDGE.value:
            target_model = Knowledge
        else:
            target_model = Document
        if isUUID(resource_identifier):
            resource_id = resource_identifier
        else:
            # 通过slug查询资源id
            resource_row = (
                self.db.query(target_model)
                .filter(target_model.slug == resource_identifier)
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
                    invitate_type=resource_type,
                    token=temp_token,
                )
            else:
                has_active_record = Invitation(
                    document_id=resource_id,
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
            knowledge_id=invitation.knowledge_id,
            status=invitation.status,
            knowledge_name=knowledge_name,
            document_id=invitation.document_id,
            invitate_type=invitation.invitate_type,
            document_name=document_name,
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
