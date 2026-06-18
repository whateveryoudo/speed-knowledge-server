"""添加知识库分组关系(单独脚本)"""

from app.db.session import SessionLocal  # 名字看你项目，通常叫 SessionLocal
from app.services.permission_ability_service import PermissionAbilityService
from app.models.knowledge_group_relation import KnowledgeGroupRelation
from app.models.knowledge import Knowledge
from app.models.knowledge_group import KnowledgeGroup
from app.models.user import User
from app.services.knowledge_group_service import KnowledgeGroupService


def main():
    db = SessionLocal()
    knowledge_group_service = KnowledgeGroupService(db)
    for kb in db.query(Knowledge).filter(Knowledge.deleted_at.is_(None)).all():
        exists = (
            db.query(KnowledgeGroupRelation)
            .filter_by(
                knowledge_id=kb.id,
                user_id=kb.user_id,
            )
            .first()
        )
        if exists:
            continue

        group = db.query(KnowledgeGroup).filter_by(id=kb.group_id).first()
        if not group:
            group = knowledge_group_service.get_default_group(kb.user_id)
        order_index = (
            db.query(KnowledgeGroupRelation).filter_by(group_id=group.id).count() + 1
        )

        relation = KnowledgeGroupRelation(
            knowledge_id=kb.id,
            user_id=kb.user_id,
            group_id=group.id,
            order_index=order_index,
        )
        db.add(relation)
        db.flush()
        print(
            f"Added knowledge group relation for knowledge {kb.id} in group {group.id}"
        )
    db.commit()
    db.close()


if __name__ == "__main__":
    main()
