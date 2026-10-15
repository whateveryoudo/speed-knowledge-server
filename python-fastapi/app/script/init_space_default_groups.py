"""
存量组织空间补齐公共区域的默认分组
"""

from app.common.enums.knowledge import KnowledgeGroupType
from app.db.session import SessionLocal
from app.models.space import Space
from app.models.knowledge_group import KnowledgeGroup
from app.schemas.knowledge_group import DEFAULT_DISPLAY_CONFIG
from app.common.enums import SpaceType, KnowledgeScopeType


def main():
    db = SessionLocal()
    try:
        org_spaces = db.query(Space).filter(Space.type == SpaceType.ORGANIZATION).all()
        created_count = 0
        for space in org_spaces:
            exists = (
                db.query(KnowledgeGroup)
                .filter(
                    KnowledgeGroup.scope_id == space.id,
                    KnowledgeGroup.scope_type == KnowledgeScopeType.SPACE.value,
                    KnowledgeGroup.is_default.isnot(None),
                )
                .first()
            )
            if not exists:
                default_group = KnowledgeGroup(
                    group_name="默认分组",
                    scope_id=space.id,
                    scope_type=KnowledgeScopeType.SPACE.value,
                    created_by=space.owner_id,
                    is_default=True,
                    order_index=0,
                    display_config=DEFAULT_DISPLAY_CONFIG.model_dump(),
                )
                db.add(default_group)
                created_count += 1
                print(f"[+] 为空间 '{space.name}' ({space.id}) 创建公共区默认分组")
        db.commit()
        print(f"成功为 {created_count} 个组织空间创建公共区默认分组")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
        print("Done.")


if __name__ == "__main__":
    main()
