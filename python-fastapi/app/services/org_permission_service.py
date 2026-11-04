"""组织统一权限校验前置服务"""
from sqlalchemy.orm import Session
from app.common.enums import OrgType, SpaceMemberRole, TeamMemberRole
from app.common.utils import to_enum
from app.services.space_member_service import SpaceMemberService
from app.services.team_member_service import TeamMemberService


class OrgPermissionService:
    """团队/空间的前置权限校验"""

    def __init__(self, db: Session):
        self.db = db
        self.space_member_service = SpaceMemberService(db)
        self.team_member_service = TeamMemberService(db)

    def ensure_org_admin(
        self, *, org_type: OrgType | str, org_id: str, user_id: int,detail_message:str|None=None
    ):
        """校验用户是否是管理员及以上"""
        # 枚举判断
        org_type_enum = to_enum(OrgType, org_type)
        # 2. 细粒度多态鉴权
        if org_type_enum == OrgType.SPACE:
            self.space_member_service.ensure_member_role(
                space_id=org_id,
                user_id=user_id,
                allow_roles=[SpaceMemberRole.ADMIN, SpaceMemberRole.OWNER],
                detail_message= detail_message or "您不是该空间的管理员或所有者，无权审批加入申请",
            )
        elif org_type_enum == OrgType.TEAM:
            # 后续接入团队时，直接在这里调 team_member_service 校验团队管理员
            pass
