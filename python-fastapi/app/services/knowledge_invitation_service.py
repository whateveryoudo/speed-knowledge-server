"""知识库邀请链接服务"""

from fastapi import HTTPException
from app.models.knowledge_invitation import KnowledgeInvitation
from app.models.knowledge import Knowledge
from sqlalchemy.orm import Session
from app.common.enums import KnowledgeInvitationStatus
from app.schemas.knowledge_invitation import (
    KnowledgeInvitationValidInfo,
    KnowledgeInvitationResponse,
    KnowledgeInvitationBase,
)
from app.common.utils import isUUID
import secrets
import string

alphabet = string.ascii_letters + string.digits


class KnowledgeInvitationService:
    """知识库邀请链接服务"""

    def __init__(self, db: Session):
        self.db = db

    def _generate_token(self) -> str:
        """生成邀请token"""
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def update_invitation_token(
        self, invitation_id: str, invitation_update: KnowledgeInvitationBase
    ) -> KnowledgeInvitationResponse:
        """更新知识库邀请链接token信息"""
        has_active_record = (
            self.db.query(KnowledgeInvitation)
            .filter(KnowledgeInvitation.id == invitation_id)
            .first()
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

    def reset_invitation_token(self, invitation_id: str) -> KnowledgeInvitationResponse:
        """重置知识库邀请链接token信息"""
        has_active_record = (
            self.db.query(KnowledgeInvitation)
            .filter(KnowledgeInvitation.id == invitation_id)
            .first()
        )
        if has_active_record is None:
            return None
        # 复制一份已有的记录
        new_record = has_active_record.copy()
        new_record.token = self._generate_token()
        new_record.status = KnowledgeInvitationStatus.ACTIVE.value
        # 历史改为已撤销
        has_active_record.status = KnowledgeInvitationStatus.REVOKED.value
        self.db.add(new_record)
        self.db.commit()
        self.db.refresh(has_active_record)
        self.db.refresh(new_record)
        return new_record

    def get_invitation_token(
        self, knowledge_identifier: str
    ) -> KnowledgeInvitationResponse:
        """获取知识库邀请链接token信息"""
        if isUUID(knowledge_identifier):
            knowledge_id = knowledge_identifier
        else:
            # 通过slug查询知识库id
            knowledge = (
                self.db.query(Knowledge)
                .filter(Knowledge.slug == knowledge_identifier)
                .first()
            )
            if knowledge is None:
                return None
            knowledge_id = knowledge.id

        print(f"knowledge_id: {knowledge_id}")
        # 逻辑：先查找active记录，没有的话则初始化一条记录
        has_active_record = (
            self.db.query(KnowledgeInvitation)
            .filter(
                KnowledgeInvitation.knowledge_id == knowledge_id,
                KnowledgeInvitation.status == KnowledgeInvitationStatus.ACTIVE.value,
            )
            .first()
        )

        # 只有没有 active 记录时才生成 token
        if has_active_record is None:
            temp_token = self._generate_token()
            while (
                self.db.query(KnowledgeInvitation)
                .filter(KnowledgeInvitation.token == temp_token)
                .first()
            ):
                temp_token = self._generate_token()

            has_active_record = KnowledgeInvitation(
                knowledge_id=knowledge_id, token=temp_token
            )
            self.db.add(has_active_record)
            self.db.commit()
            self.db.refresh(has_active_record)

        return has_active_record

    def get_invitation_valid_info(self, token: str) -> KnowledgeInvitationValidInfo:
        """获取知识库邀请链接token信息(这里会进行一些封装)"""
        has_active_record = (
            self.db.query(KnowledgeInvitation, Knowledge.name.label("knowledge_name"))
            .join(Knowledge, KnowledgeInvitation.knowledge_id == Knowledge.id)
            .filter(
                KnowledgeInvitation.token == token,
                KnowledgeInvitation.status == KnowledgeInvitationStatus.ACTIVE.value,
            )
            .first()
        )
        if has_active_record is None:
            return None
        invitation, knowledge_name = has_active_record
        return KnowledgeInvitationValidInfo(
            knowledge_id=invitation.knowledge_id,
            status=invitation.status,
            knowledge_name=knowledge_name,
        )

    def get_invitation_by_token(self, token: str) -> KnowledgeInvitationResponse:
        """获取知识库邀请链接token信息"""
        has_active_record = (
            self.db.query(KnowledgeInvitation)
            .filter(
                KnowledgeInvitation.token == token,
                KnowledgeInvitation.status == KnowledgeInvitationStatus.ACTIVE.value,
            )
            .first()
        )

        return has_active_record
