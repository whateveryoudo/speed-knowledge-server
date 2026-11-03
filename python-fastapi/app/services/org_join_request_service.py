"""资源访问申请服务"""


from app.repositories.org_join_request_repository import OrgJoinRequestRepository
from datetime import datetime
from app.models.resource_access_request import ResourceAccessRequest

from sqlalchemy.orm import Session
from app.common.utils import is_duplicate_on
from fastapi import HTTPException, status
from app.common.enums import OrgType, ApprovalStatus, SpaceMemberRole
from typing import Optional
from sqlalchemy.exc import IntegrityError
from app.models.org_join_request import OrgJoinRequest
from app.schemas.org_join_request import OrgJoinRequestAudit
from app.schemas.space_member import SpaceMemberAdd

from app.models.org_join_request import OrgJoinRequest
from app.repositories.org_join_request_repository import OrgJoinRequestRepository
from app.repositories.space_department_repository import SpaceDepartmentRepository
from app.services.space_member_service import SpaceMemberService
from app.common.utils import to_enum

class OrgJoinRequestService:
    """组织加入审批服务"""

    PENDING_KEY_CONSTRAINT = "uq_org_join_request_pending_key"

    def __init__(self, db: Session):
        self.db = db

        self.repo = OrgJoinRequestRepository(db)
        self.space_dept_repo = SpaceDepartmentRepository(db)
        self.space_member_service = SpaceMemberService(db)

    @staticmethod
    def _build_pending_key(
        *, org_type: OrgType, org_id: str, applicant_user_id: int
    ) -> str:
        """生成待审批幂等键"""
        return f"{org_type.value}:{org_id}:{applicant_user_id}"

    def get_by_id_or_404(
        self, request_id: str, *, for_update: bool = False
    ) -> OrgJoinRequest:
        """根据ID获取（审批单），不存在则抛出404异常"""
        request = self.repo.get_by_id(id=request_id, for_update=for_update)
        if request is None:
            raise HTTPException(status_code=404, detail="审批记录不存在")
        return request

    def _ensure_org_admin(
        self, *, org_type: OrgType | str, org_id: str, reviewer_id: int
    ):
        """校验用户是否有权限审批"""
        # 枚举判断
        org_type_enum = to_enum(OrgType, org_type)
        # 2. 细粒度多态鉴权
        if org_type_enum == OrgType.SPACE:
            self.space_member_service.ensure_member_role(
                space_id=org_id,
                user_id=reviewer_id,
                allow_roles=[SpaceMemberRole.ADMIN, SpaceMemberRole.OWNER],
                detail_message="您不是该空间的管理员或所有者，无权审批加入申请",
            )
        elif org_type_enum == OrgType.TEAM:
            # 后续接入团队时，直接在这里调 team_member_service 校验团队管理员
            pass

    def ensure_pending_request(
        self,
        *,
        org_type: OrgType,
        org_id: str,
        applicant_user_id: int,
        target_role: str = "member",
        department_id: Optional[str] = None,
        apply_message: Optional[str] = None,
    ) -> OrgJoinRequest:
        """确保用户对指定资源有一条待审批的审批单，如果之前的申请已经结束，则会创建新的审批单"""

        pending_key = self._build_pending_key(
            org_type=org_type,
            org_id=org_id,
            applicant_user_id=applicant_user_id,
        )
        existing = self.repo.get_pending(pending_key=pending_key, for_update=True)
        if existing:
            return existing
        join_req = OrgJoinRequest(
            org_type=org_type.value,
            org_id=org_id,
            applicant_user_id=applicant_user_id,
            department_id=department_id,
            target_role=target_role,
            status=ApprovalStatus.PENDING.value,
            apply_message=apply_message,
            pending_key=pending_key,
        )
        try:
            with self.db.begin_nested():
                self.repo.add(request=join_req)
            return join_req
        except IntegrityError as exc:
            if not is_duplicate_on(exc, self.PENDING_KEY_CONSTRAINT):
                raise
            # 并发请求插入了相同的pending_key，需要重新查询
            pending_request = self.repo.get_pending(
                pending_key=pending_key,
                for_update=True,
            )
            if pending_request is None:
                # 非pending_key唯一性冲突
                raise
            return pending_request

    def audit_request(
        self, *, request_id: str, reviewer_id: int, audit_in: OrgJoinRequestAudit
    ) -> Optional[bool]:
        """审批单据（包含拒绝/同意）"""
        # 开启锁防止并发审批
        access_request = self.get_by_id_or_404(request_id, for_update=True)
        # 权限校验
        self._ensure_org_admin(
            org_id=access_request.org_id,
            org_type=access_request.org_type,
            reviewer_id=reviewer_id
        )
        if access_request.status != ApprovalStatus.PENDING.value:
            raise HTTPException(status_code=409, detail="该申请已被处理，无法重复操作")

        if audit_in.status == ApprovalStatus.APPROVED:
            # 加入到组织
            if access_request.org_type == OrgType.SPACE.value:
                # 空间成员，
                dept_id = access_request.department_id
                if dept_id and not self.space_dept_repo.get_by_id(dept_id):
                    dept_id = None
                self.space_member_service.add_or_restore_member(
                    space_id=access_request.org_id,
                    data=SpaceMemberAdd(
                        user_id=access_request.applicant_user_id,
                        role=access_request.target_role,
                        department_ids=[dept_id]
                        if dept_id
                        else [],
                    ),
                    ignore_if_exists=True,
                )
            elif access_request.org_type == OrgType.TEAM.value:
                # 预留团队成员加入
                pass
        # 更新审批单状态
        access_request.status = audit_in.status.value
        access_request.reviewed_by = reviewer_id
        access_request.reviewed_at = datetime.now()
        # 释放pending唯一键
        access_request.pending_key = None
        self.db.commit()
        return True

    def cancel_request(
        self, *, request_id: str, applicant_user_id: int
    ) -> Optional[bool]:
        """申请人主动取消"""
        access_request = self.get_by_id_or_404(request_id, for_update=True)
        if access_request.applicant_user_id != applicant_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权限取消其他用户的申请"
            )
        if access_request.status == ApprovalStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="当前申请已取消，请勿重复操作"
            )
        if access_request.status != ApprovalStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="当前申请状态不允许取消"
            )

        access_request.status = ApprovalStatus.CANCELLED.value
        access_request.reviewed_by = None
        access_request.reviewed_at = None
        access_request.pending_key = None
        self.db.commit()
        return True
