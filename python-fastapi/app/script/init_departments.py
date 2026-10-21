from app.models import SpaceMember
from app.models import SpaceDepartment, Space, SpaceDepartmentMember
from app.db.session import SessionLocal
from app.common.enums import SpaceType
from datetime import datetime
import uuid


def init_existing_space_departments():
    db = SessionLocal()
    try:
        spaces = db.query(Space).filter(
            Space.type == SpaceType.ORGANIZATION.value
        ).all()
        now = datetime.now()
        count = 0

        for space in spaces:
            root_dept = (
                db.query(SpaceDepartment)
                .filter(
                    SpaceDepartment.space_id == space.id,
                    SpaceDepartment.parent_id.is_(None),
                )
                .first()
            )
            if not root_dept:
                # 追加默认部门
                root_dept = SpaceDepartment(
                    id=str(uuid.uuid4()),
                    space_id=space.id,
                    parent_id=None,
                    sort_order=0,
                    name=space.name,
                    created_at=now,
                    updated_at=now,
                )
                db.add(root_dept)
                db.flush()
                print(f"空间：{space.name}，追加了根部门：{root_dept.name}")
            members = (
                db.query(SpaceMember)
                .filter(
                    SpaceMember.space_id == space.id,
                    SpaceMember.deleted_at.is_(None),
                )
                .all()
            )
            for member in members:
                exsits = (
                    db.query(SpaceDepartmentMember)
                    .filter(
                        SpaceDepartmentMember.space_member_id == member.id,
                        SpaceDepartmentMember.department_id == root_dept.id,
                    )
                    .first()
                )
                if not exsits:
                    db.add(
                        SpaceDepartmentMember(
                            id=str(uuid.uuid4()),
                            department_id=root_dept.id,
                            space_member_id=member.id,
                            created_at=now,
                            updated_at=now,
                        )
                    )
                    count += 1
        db.commit()
        print(f"追加根部门成功，共追加了{count}个成员到根部门")
    except Exception as e:
        db.rollback()
        print(f"初始化失败：{e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_existing_space_departments()
