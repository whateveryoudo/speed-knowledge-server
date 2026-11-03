from app.common.enums import SpaceMemberRole, OrgInvitationUserStatus
from sqlalchemy.orm import Session
from typing import Optional
from app.repositories.space_department_repository import SpaceDepartmentRepository
from app.repositories.space_member_repository import SpaceMemberRepository
from app.repositories.org_invitation_repository import OrgInvitationRepository
from app.models.org_invitation import OrgInvitation
from app.models.space import Space
from app.models.space_member import SpaceMember
from app.models.team import Team
from app.schemas.org_invitation import (
    OrgInvitationAcceptResponse,
    OrgInvitationUpdateSettings,
    OrgInvitationPublicInfo,
)
from app.common.enums import OrgType, InvitationStatus
from app.services.space_member_service import SpaceMemberService
from app.services.org_join_request_service import OrgJoinRequestService
from app.repositories.org_join_request_repository import OrgJoinRequestRepository
from app.schemas.space_member import SpaceMemberAdd
from app.common.utils import to_enum
from fastapi import HTTPException, status
import secrets
import string

alphabet = string.ascii_letters + string.digits


class OrgInvitationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrgInvitationRepository(db)
        self.space_dept_repo = SpaceDepartmentRepository(db)
        self.join_request_repo = OrgJoinRequestRepository(db)
        self.space_member_repo = SpaceMemberRepository(db)
        self.space_member_service = SpaceMemberService(db)
        self.join_request_service = OrgJoinRequestService(db)

    @staticmethod
    def _generate_token() -> str:
        """生成邀请token"""
        return "".join(secrets.choice(alphabet) for _ in range(16))

    def _ensure_org_admin(
        self, *, org_type: OrgType | str, org_id: str, operator_id: int
    ):
        """校验用户是否有权限审批"""
        # 枚举判断
        org_type_enum = to_enum(OrgType, org_type)
        # 2. 细粒度多态鉴权
        if org_type_enum == OrgType.SPACE:
            self.space_member_service.ensure_member_role(
                space_id=org_id,
                user_id=operator_id,
                allow_roles=[SpaceMemberRole.ADMIN, SpaceMemberRole.OWNER],
                detail_message="您不是该空间的管理员或所有者，无权审批加入申请",
            )
        elif org_type_enum == OrgType.TEAM:
            # 后续接入团队时，直接在这里调 team_member_service 校验团队管理员
            pass


    def get_my_invitation(
        self,
        *,
        org_type: OrgType,
        org_id: str,
        data: OrgInvitationUpdateSettings,
        operator_id: int,
    ) -> OrgInvitation:
        """点开弹出显示个人的邀请链接"""
        # 权限校验
        self._ensure_org_admin(
            org_id=org_id,
            org_type=org_type,
            operator_id=operator_id
        )
        invitation = self.repo.get_by_user(
            org_type=org_type, org_id=org_id, inviter_id=operator_id
        )
       
        if not invitation:
            invitation = OrgInvitation(
                org_id=org_id,
                org_type=org_type.value,
                inviter_id=operator_id,
                token=self._generate_token(),
                default_dept_id=data.default_dept_id,
                need_approval=data.need_approval if data.need_approval is not None else False,
                default_role=data.default_role or 'member'
            )
            self.repo.add(invitation)
            self.db.commit()
        return invitation

    def save_and_get_invitation(
        self,
        *,
        token: str,
        data: OrgInvitationUpdateSettings,
        operator_id: int
    ):
        invitation = self.repo.get_by_token(token)
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="邀请链接不存在")
        # 权限校验
        self._ensure_org_admin(
                org_id=invitation.org_id,
                org_type=invitation.org_type,
                operator_id=operator_id,
            )
        # 更新一些配置(这样写支持重置None)
        update_data = data.model_dump(exclude_unset=True)
        for field,value in update_data.items():
            setattr(invitation, field,value)
        # if data.default_dept_id is not None:
        #     invitation.default_dept_id = data.default_dept_id
        # if data.need_approval is not None:
        #     invitation.need_approval = data.need_approval
        # if data.default_role is not None:
        #     invitation.default_role = data.default_role
        self.db.commit()
        return invitation

    def reset_token(
        self,
        *,
        token: str,
        operator_id: int
    ) -> OrgInvitation:
        invitation = self.repo.get_by_token(token)
        if invitation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="邀请链接不存在")
        self._ensure_org_admin(
            org_id=invitation.org_id,
            org_type=invitation.org_type,
            operator_id=operator_id,
        )
        # 更新token
        invitation.token = self._generate_token()
        invitation.status = InvitationStatus.ACTIVE.value
        self.db.commit()
        return invitation

    def _get_active_invitation_or_404(self, token: str) -> OrgInvitation:
        """前置查询邀请信息"""
        invitation = self.repo.get_by_token(token)
        if invitation is None or invitation.status != InvitationStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="邀请链接不存在或已失效"
            )
        return invitation

    def _resolve_org_display_info(
        self, invitation: OrgInvitation
    ) -> tuple[str, Optional[str], Optional[str], Optional[str]]:
        """解析邀请组织的一些信息"""
        org_name = ""
        org_icon = None
        org_slug = None
        default_dept_name = None
        if invitation.org_type == OrgType.SPACE.value:
            space = self.db.query(Space).filter(Space.id == invitation.org_id, Space.deleted_at.is_(None)).first()
            if not space:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="目标空间不存在")
            org_icon = space.icon
            org_name = space.name
            org_slug = space.domain  # 这里返回空间域名
            if invitation.default_dept_id:
                dept = self.space_dept_repo.get_by_id(invitation.default_dept_id)
                default_dept_name = dept.name if dept else None
        elif invitation.org_type == OrgType.TEAM.value:
            team = (
                self.db.query(Team)
                .filter(Team.id == invitation.org_id,Team.deleted_at.is_(None))
                .first()
            )
            org_icon = team.icon
            org_name = team.name
            org_slug = team.slug  # 这里返回团队的短链
        return org_name, org_icon, org_slug, default_dept_name

    def _resolve_user_identity(
        self, *, invitation: OrgInvitation, user_id: int
    ) -> OrgInvitationUserStatus:
        """用户信息前置校验"""
        user_status = OrgInvitationUserStatus.NOT_JOINED
        if invitation.org_type == OrgType.SPACE.value:
            member = self.space_member_repo.get_any_by_space_and_user(
                space_id=invitation.org_id, user_id=user_id
            )
            if member and member.deleted_at is None:
                if member.role == SpaceMemberRole.EXTERNAL:
                    user_status = OrgInvitationUserStatus.EXTERNAL
                else:
                    user_status = OrgInvitationUserStatus.JOINED
            else:
                pending_row = self.join_request_repo.get_pending(
                    pending_key=f"{invitation.org_type}:{invitation.org_id}:{user_id}"
                )
                if pending_row:
                    user_status = OrgInvitationUserStatus.PENDING
        elif invitation.org_type == OrgType.TEAM.value:
            # 预留团队校验
            pass

        return user_status

    def get_public_info(
        self, *, token: str, current_user_id: int
    ) -> OrgInvitationPublicInfo:
        """通过token拿取相关信息"""
        invitation = self._get_active_invitation_or_404(token)
        # 查出邀请组织的一些信息
        (org_name, org_icon, org_slug, default_dept_name) = self._resolve_org_display_info(
            invitation
        )
        # 计算登录人身份
        user_status = self._resolve_user_identity(
            invitation=invitation, user_id=current_user_id
        )
        inviter_name = (
            invitation.inviter.nickname or invitation.inviter.username
            if invitation.inviter
            else "管理员"
        )

        return OrgInvitationPublicInfo(
            org_id=invitation.org_id,
            org_type=OrgType(invitation.org_type),
            org_name=org_name,
            org_icon=org_icon,
            org_slug=org_slug,
            inviter_name=inviter_name,
            need_approval=invitation.need_approval,
            default_dept_id=invitation.default_dept_id,
            default_dept_name=default_dept_name,
            user_status=user_status,
        )

    def accept_invitation(self, *, token: str, user_id: int):
        """点击加入"""
        invitation = self._get_active_invitation_or_404(token)

        _, _, org_slug, _ = self._resolve_org_display_info(invitation)

        user_status = self._resolve_user_identity(
            invitation=invitation, user_id=user_id
        )

        if (
            user_status == OrgInvitationUserStatus.JOINED
            or user_status == OrgInvitationUserStatus.PENDING
        ):
            # 正在审核或者用户已经加入了，则直接进入
            return OrgInvitationAcceptResponse(
                user_status=user_status,
                org_id=invitation.org_id,
                org_slug=org_slug or "",
            )
        if not invitation.need_approval:
            # 不需要审批，直接加入
            if invitation.org_type == OrgType.SPACE.value:
                target_role = (
                    SpaceMemberRole(invitation.default_role)
                    if invitation.default_role in SpaceMemberRole.__members__.values()
                    else SpaceMemberRole.MEMBER
                )
                dept_id = invitation.default_dept_id
                if dept_id and not self.space_dept_repo.get_by_id(dept_id):
                    # 如果加入前部门被删除了， 会挂载到根部门下
                    dept_id = None
                self.space_member_service.add_or_restore_member(
                    space_id=invitation.org_id,
                    data=SpaceMemberAdd(
                        user_id=user_id,
                        role=target_role,
                        department_ids=[dept_id]
                        if dept_id
                        else [],
                    ),
                )
            elif invitation.org_type == OrgType.TEAM.value:
                pass
            return OrgInvitationAcceptResponse(
                user_status=OrgInvitationUserStatus.JOINED,
                org_id=invitation.org_id,
                org_slug=org_slug or "",
            )

        # 走审批流程
        self.join_request_service.ensure_pending_request(
            org_type=OrgType(invitation.org_type),
            org_id=invitation.org_id,
            applicant_user_id=user_id,
            target_role=invitation.default_role,
            department_id=invitation.default_dept_id,
            # 这里目前没有同意/拒绝信息
            apply_message=None,
        )
        self.db.commit()
        return OrgInvitationAcceptResponse(
            user_status=OrgInvitationUserStatus.PENDING,
            org_id=invitation.org_id,
            org_slug=org_slug or "",
        )
