from sqlalchemy.orm import Session
from app.models.knowledge_common_pin import KnowledgeCommonPin
from app.models.knowledge import Knowledge
from app.schemas.knowledge_common_pin import KnowledgeCommonPinResponse
from typing import List
from app.common.utils import next_order_index, is_duplicate_entry
from sqlalchemy.exc import IntegrityError
from app.services.permission_service import PermissionService
from app.schemas.knowledge import KnowledgeResponse


class KnowledgeCommonPinService:
    def __init__(self, db: Session):
        self.db = db
        self.permission_service = PermissionService(db)

    def _build_response(
        self,
        *,
        pin: KnowledgeCommonPin,
        knowledge: Knowledge,
        ability_map: dict[str, dict],
    ) -> KnowledgeCommonPinResponse:
        """构建响应对象"""
        knowledge_response = KnowledgeResponse.model_validate(knowledge).model_copy(
            update={"ability": ability_map.get(knowledge.id, {})}
        )
        return KnowledgeCommonPinResponse(
            id=pin.id,
            knowledge_id=pin.knowledge_id,
            user_id=pin.user_id,
            order_index=pin.order_index,
            created_at=pin.created_at,
            updated_at=pin.updated_at,
            knowledge=knowledge_response,
        )

    def get_by_knowledge_id_and_user_id(
        self, knowledge_id: str, user_id: int
    ) -> KnowledgeCommonPin:
        """获取一条常用知识库记录"""
        return (
            self.db.query(KnowledgeCommonPin)
            .filter(
                KnowledgeCommonPin.knowledge_id == knowledge_id,
                KnowledgeCommonPin.user_id == user_id,
            )
            .first()
        )

    def create(
        self, *, knowledge_id: str, creator_id: int, commit: bool = True
    ) -> KnowledgeCommonPinResponse:
        """创建一条常用知识库记录"""
        knowledge = self.permission_service.assert_knowledge_readable(
            user_id=creator_id, identifier=knowledge_id
        )
        ability_map = (
            self.permission_service.get_multiple_effective_knowledge_abilities(
                user_id=creator_id,
                knowledge_ids=[knowledge_id],
            )
        )
        existing_record = self.get_by_knowledge_id_and_user_id(knowledge_id, creator_id)
        if existing_record is not None:
            return self._build_response(
                pin=existing_record,
                knowledge=knowledge,
                ability_map=ability_map,
            )

        new_record = KnowledgeCommonPin(
            knowledge_id=knowledge_id,
            order_index=next_order_index(self.db, KnowledgeCommonPin, user_id=creator_id),
            user_id=creator_id,
        )
        self.db.add(new_record)
        if not commit:
            self.db.flush()
            return self._build_response(
                pin=new_record,
                knowledge=knowledge,
                ability_map=ability_map,
            )
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            if not is_duplicate_entry(e):
                raise
            existing_record = self.get_by_knowledge_id_and_user_id(
                knowledge.id, creator_id
            )
            if existing_record is None:
                raise
            return self._build_response(
                pin=existing_record,
                knowledge=knowledge,
                ability_map=ability_map,
            )

        self.db.refresh(new_record)
        return self._build_response(
            pin=new_record,
            knowledge=knowledge,
            ability_map=ability_map,
        )

    def get_list_by_user_id(self, user_id: int) -> List[KnowledgeCommonPinResponse]:
        """获取用户常用知识库记录列表（含知识库信息）"""
        pins = (
            self.db.query(KnowledgeCommonPin)
            .filter(KnowledgeCommonPin.user_id == user_id)
            .order_by(KnowledgeCommonPin.order_index.asc())
            .all()
        )
        if not pins:
            return []
        readable_knowledge_by_id = {
            knowledge.id: knowledge
            for knowledge in self.permission_service.list_readable_knowledges_by_ids(
                user_id=user_id, knowledge_ids=[pin.knowledge_id for pin in pins]
            )
        }
        ability_map = (
            self.permission_service.get_multiple_effective_knowledge_abilities(
                user_id=user_id,
                knowledge_ids=[
                    knowledge.id for knowledge in readable_knowledge_by_id.values()
                ],
            )
        )
        return [
            self._build_response(
                pin=pin,
                knowledge=readable_knowledge_by_id[pin.knowledge_id],
                ability_map=ability_map,
            )
            for pin in pins
            if pin.knowledge_id in readable_knowledge_by_id
        ]

    def change_order_index(
        self, knowledge_id: str, user_id: int, order_index: int
    ) -> bool:
        """修改常用知识库记录的排序索引（拖拽排序）"""
        move_record = self.get_by_knowledge_id_and_user_id(knowledge_id, user_id)
        if not move_record:
            return False
        old_index = move_record.order_index
        if old_index == order_index:
            return True
        if old_index < order_index:
            # 后移，后续范围内的记录，order_index减1
            self.db.query(KnowledgeCommonPin).filter(
                KnowledgeCommonPin.user_id == user_id,
                KnowledgeCommonPin.order_index > old_index,
                KnowledgeCommonPin.order_index <= order_index,
            ).update(
                {KnowledgeCommonPin.order_index: KnowledgeCommonPin.order_index - 1}
            )
        else:
            # 前移，后续范围内的记录，order_index加1
            self.db.query(KnowledgeCommonPin).filter(
                KnowledgeCommonPin.user_id == user_id,
                KnowledgeCommonPin.order_index < old_index,
                KnowledgeCommonPin.order_index >= order_index,
            ).update(
                {KnowledgeCommonPin.order_index: KnowledgeCommonPin.order_index + 1}
            )
        move_record.order_index = order_index
        self.db.commit()
        return True

    def delete_by_knowledge_id_and_user_id(
        self, knowledge_id: str, user_id: int
    ) -> bool:
        """取消常用（硬删 pin 记录）"""
        record = self.get_by_knowledge_id_and_user_id(knowledge_id, user_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True
