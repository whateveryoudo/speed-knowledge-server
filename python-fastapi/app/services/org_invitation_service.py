from app.common.enums import SpaceMemberRole, OrgInvitationUserStatus
from sqlalchemy.orm import Session
from typing import Optional
from app.repositories.space_department_repository import SpaceDepartmentRepository
from app.repositories.space_member_repository import SpaceMemberRepository
from app.repositories.org_invitation_repository import OrgInvitationRepository
from app.models.org_invitation import OrgInvitation
from app.models.space import Space
from app.models.space_member import SpaceMember
from app.schemas.org_invitation import OrgInvitationUpdateSettings,OrginvitationPublicInfo
from app.common.enums import OrgType, InvitationStatus, ResourceType
from fastapi import HTTPException, status
import secrets
import string

alphabet = string.ascii_letters + string.digits


class OrgInvitationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrgInvitationRepository(db)
        self.space_dept_repo = SpaceDepartmentRepository(db)
        self.space_member_repo = SpaceMemberRepository(db)

    @staticmethod
    def _generate_token() -> str:
        """生成邀请token"""
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def get_my_invitation(
        self,
        *,
        org_type: OrgType,
        org_id: str,
        data: OrgInvitationUpdateSettings,
        operator_id: int,
    ) -> OrgInvitation:
        """点开弹出显示个人的邀请链接"""
        invitation = self.repo.get_by_user(
            org_type=org_type, org_id=org_id, inviter_id=operator_id
        )
        if not invitation:
            invitation = OrgInvitation(
                org_id=org_id,
                org_type=org_type,
                inviter_id=operator_id,
                default_dept_id=data.default_dept_id,
            )
            self.repo.add(invitation)
        return invitation

    def save_and_get_invitation(
        self,
        *,
        invitation_id: str,
        data: OrgInvitationUpdateSettings,
    ):
        invitation = self.repo.get_by_token(invitation_id)
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="邀请链接不存在")

        # 更新一些配置
        if data.default_dept_id is not None:
            invitation.default_dept_id = data.default_dept_id
        if data.need_approval is not None:
            invitation.need_approval = data.need_approval
        if data.default_role is not None:
            invitation.default_role = data.default_role
        self.db.flush()
        return invitation

    def reset_token(
        self,
        *,
        org_type: OrgType,
        org_id: str,
        data: OrgInvitationUpdateSettings,
        operator_id: int,
    ) -> Optional[bool]:
        invitation = self.get_my_invitation(
            org_type=org_type, org_id=org_id, data=data, operator_id=operator_id
        )
        # 更新token
        invitation.token = self._generate_token()
        invitation.status = InvitationStatus.ACTIVE.value
        self.db.flush()
        return True

    def _get_active_invitation_or_404(self, token:str) -> OrgInvitation:
        """前置查询邀请信息"""
        invitation = self.repo.get_by_token(token)
        if invitation is None or invitation.status != InvitationStatus.ACTIVE.value:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="邀请链接不存在或已失效")
        return invitation

    def _resolve_org_display_info(self,invitation:OrgInvitation) -> tuple[str, Optional[str], Optional[str]]:
        """解析邀请组织的一些信息"""
        org_name = ""
        org_icon = None
        default_dept_name = None
        if invitation.org_type == OrgType.SPACE.value:
            space = self.query(Space).query(Space.id == invitation.org_id).first()
            if not space:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="目标空间不存在")
            org_icon = space.icon    
            org_name = space.name
            if invitation.default_dept_id:
                dept = self.space_dept_repo.get_by_id(invitation.default_dept_id)
                default_dept_name = dept.name if dept else None
        elif invitation.org_type == OrgType.TEAM.value:
            # TODO  团队信息获取
            pass
        return org_name, org_icon, default_dept_name

    def _resolve_user_identity(self, *, invitation: OrgInvitation, user_id: int) -> OrgInvitationUserStatus:
        """用户信息前置校验"""
        user_status = OrgInvitationUserStatus.NOT_JOINED
        if invitation.org_type == OrgType.SPACE.value:
            member = self.space_member_repo.get_any_by_space_and_user(
                space_id=invitation.org_id,
                user_id=user_id
            )
            if member and member.deleted_at is None:
                if member.role == SpaceMemberRole.EXTERNAL:
                    user_status = OrgInvitationUserStatus.EXTERNAL
                else:
                    user_status = OrgInvitationUserStatus.JOINED
            else:
                # TODO
                # pending = self.join_request_service.get_pending(
                #     pending_key=f"{invitation.org_type}:{invitation.org_id}:{current_user_id}"
                # )
        elif invitation.org_type == OrgType.TEAM.value:
            # 预留团队校验
            pass

        return user_status
             

    def get_public_info(self, *, token:str, current_user_id: int) -> OrginvitationPublicInfo:

        """通过token拿取相关信息"""
        invitation = self._get_active_invitation_or_404(token)
        # 查出邀请组织的一些信息
        (org_name, org_icon, default_dept_name) = self._resolve_org_display_info(invitation)
        # 计算登录人身份
        user_status = self._resolve_user_identity(invitation=invitation, user_id=current_user_id)
        inviter_name = invitation.inviter.nickname or invitation.inviter.username if invitation.inviter else "管理员"
        
        return OrginvitationPublicInfo(
            org_id=invitation.org_id,
            org_type=OrgType(invitation.org_type),
            org_name=org_name,
            org_icon=org_icon,
            inviter_name=inviter_name,
            need_approval=invitation.need_approval,
            default_dept_id=invitation.default_dept_id,
            default_dept_name=default_dept_name,
            user_status=user_status
        )

    def accept_invitation(
        self,*,token:str,user_id:int
    ):
        """点击加入"""
        invitation = self._get_active_invitation_or_404(token)

        user_status = self._resolve_user_identity(invitation=invitation,user_id=user_id=)

        if user_status == OrgInvitationUserStatus.JOINED:
            return OrgInvitationAcceptResponse(
                joined=True,
                message="您已经是该空间正式成员，正在前往空间..."
            )