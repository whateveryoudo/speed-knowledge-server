from app.models.permission_group import PermissionGroup
from app.models.permission_ability import PermissionAbility
from app.db.session import SessionLocal
from app.common.enums import DocumentAbility, ResourceRole


def main():
    ENABLE_BY_ROLE = {
        ResourceRole.ADMIN.value: True,
        ResourceRole.EDIT.value: True,
        ResourceRole.READ.value: False,
    }
    db = SessionLocal()
    groups = db.query(PermissionGroup).all()
    try:
        for group in groups:
            exists = (
                db.query(PermissionAbility)
                .filter(
                    PermissionAbility.permission_group_id == group.id,
                    PermissionAbility.ability_key == DocumentAbility.DOC_EXPORT.value,
                )
                .first()
            )
            if exists:
                continue
            # 获取校色的能力值
            enabled = ENABLE_BY_ROLE[group.role_key]
            ability = PermissionAbility(
                permission_group_id=group.id,
                ability_key=DocumentAbility.DOC_EXPORT.value,
                enabled=enabled,
            )
            db.add(ability)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
