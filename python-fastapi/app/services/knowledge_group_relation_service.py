from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.utils import is_duplicate_entry, next_order_index
from app.models.knowledge_group_relation import KnowledgeGroupRelation
from app.schemas.knowledge_group_relation import (
    KnowledgeGroupRelationCreate,
    KnowledgeGroupRelationMoveBody,
)


class KnowledgeGroupRelationService:
    """知识库分组关联信息服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id_and_knowledge_id(
        self, user_id: int, knowledge_id: str
    ) -> KnowledgeGroupRelation | None:
        return (
            self.db.query(KnowledgeGroupRelation)
            .filter(
                KnowledgeGroupRelation.user_id == user_id,
                KnowledgeGroupRelation.knowledge_id == knowledge_id,
            )
            .first()
        )

    def create(
        self,
        knowledge_group_relation_in: KnowledgeGroupRelationCreate,
        *,
        commit: bool = True,
    ) -> KnowledgeGroupRelation:
        """创建知识库分组关联信息"""
        user_id = knowledge_group_relation_in.user_id
        knowledge_id = knowledge_group_relation_in.knowledge_id
        group_id = knowledge_group_relation_in.group_id

        existing_record = self.get_by_user_id_and_knowledge_id(user_id, knowledge_id)
        if existing_record:
            return existing_record

        knowledge_group_relation = KnowledgeGroupRelation(
            knowledge_id=knowledge_id,
            user_id=user_id,
            group_id=group_id,
            order_index=next_order_index(
                self.db, KnowledgeGroupRelation, user_id=user_id, group_id=group_id
            ),
        )
        self.db.add(knowledge_group_relation)
        if commit:
            try:
                self.db.commit()
            except IntegrityError as exc:
                self.db.rollback()
                if is_duplicate_entry(exc):
                    existing = self.get_by_user_id_and_knowledge_id(
                        user_id, knowledge_id
                    )
                    if existing:
                        return existing
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="该知识库已在分组中",
                    ) from exc
                raise
            self.db.refresh(knowledge_group_relation)
        else:
            self.db.flush()
        return knowledge_group_relation

    def move_relation(
        self,
        user_id: int,
        knowledge_id: str,
        move_in: KnowledgeGroupRelationMoveBody,
    ) -> bool:
        """组内排序 / 跨组拖入"""
        relation = self.get_by_user_id_and_knowledge_id(user_id, knowledge_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库分组关联不存在",
            )

        target_group_id = move_in.group_id
        target_index = move_in.order_index
        old_group_id = relation.group_id
        old_index = relation.order_index

        if old_group_id == target_group_id:
            if old_index == target_index:
                return True
            if old_index < target_index:
                self.db.query(KnowledgeGroupRelation).filter(
                    KnowledgeGroupRelation.user_id == user_id,
                    KnowledgeGroupRelation.group_id == target_group_id,
                    KnowledgeGroupRelation.order_index > old_index,
                    KnowledgeGroupRelation.order_index <= target_index,
                ).update(
                    {
                        KnowledgeGroupRelation.order_index: KnowledgeGroupRelation.order_index
                        - 1
                    },
                    synchronize_session=False,
                )
            else:
                self.db.query(KnowledgeGroupRelation).filter(
                    KnowledgeGroupRelation.user_id == user_id,
                    KnowledgeGroupRelation.group_id == target_group_id,
                    KnowledgeGroupRelation.order_index < old_index,
                    KnowledgeGroupRelation.order_index >= target_index,
                ).update(
                    {
                        KnowledgeGroupRelation.order_index: KnowledgeGroupRelation.order_index
                        + 1
                    },
                    synchronize_session=False,
                )
            relation.order_index = target_index
        else:
            self.db.query(KnowledgeGroupRelation).filter(
                KnowledgeGroupRelation.user_id == user_id,
                KnowledgeGroupRelation.group_id == target_group_id,
                KnowledgeGroupRelation.order_index >= target_index,
            ).update(
                {
                    KnowledgeGroupRelation.order_index: KnowledgeGroupRelation.order_index
                    + 1
                },
                synchronize_session=False,
            )
            relation.group_id = target_group_id
            relation.order_index = target_index

        self.db.commit()
        return True
