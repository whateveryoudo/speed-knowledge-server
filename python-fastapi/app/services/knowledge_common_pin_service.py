from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.knowledge_common_pin import KnowledgeCommonPin
from app.models.knowledge import Knowledge
from app.schemas.knowledge_common_pin import KnowledgeCommonPinResponse
from app.services.knowledge_service import KnowledgeService
from typing import List
from app.common.utils import next_order_index, is_duplicate_entry
from sqlalchemy.exc import IntegrityError


class KnowledgeCommonPinService:
    def __init__(self, db: Session):
        self.db = db

    def _to_response(
        self, pin: KnowledgeCommonPin, user_id: int
    ) -> KnowledgeCommonPinResponse | None:
        knowledge_service = KnowledgeService(self.db)
        knowledge = (
            knowledge_service.get_active_query()
            .filter(Knowledge.id == pin.knowledge_id)
            .options(joinedload(Knowledge.team))
            .first()
        )
        if not knowledge:
            return None
        return KnowledgeCommonPinResponse(
            id=pin.id,
            knowledge_id=pin.knowledge_id,
            user_id=pin.user_id,
            order_index=pin.order_index,
            created_at=pin.created_at,
            updated_at=pin.updated_at,
            knowledge=knowledge_service.to_wrap_knowledge_response(knowledge, user_id),
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

    def create(self, knowledge_id: str, user_id: int) -> KnowledgeCommonPinResponse:
        """创建一条常用知识库记录"""
        existing_record = self.get_by_knowledge_id_and_user_id(knowledge_id, user_id)
        if existing_record:
            response = self._to_response(existing_record, user_id)
            if not response:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="知识库不存在或已删除",
                )
            return response

        new_record = KnowledgeCommonPin(
            knowledge_id=knowledge_id,
            order_index=next_order_index(self.db, KnowledgeCommonPin, user_id=user_id),
            user_id=user_id,
        )
        self.db.add(new_record)
        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            if is_duplicate_entry(e):
                existing_record = self.get_by_knowledge_id_and_user_id(
                    knowledge_id, user_id
                )
                if existing_record:
                    response = self._to_response(existing_record, user_id)
                    if response:
                        return response
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="已在常用列中",
                )
            raise e
        self.db.refresh(new_record)
        response = self._to_response(new_record, user_id)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在或已删除",
            )
        return response

    def get_list_by_user_id(self, user_id: int) -> List[KnowledgeCommonPinResponse]:
        """获取用户常用知识库记录列表（含知识库信息）"""
        pins = (
            self.db.query(KnowledgeCommonPin)
            .filter(KnowledgeCommonPin.user_id == user_id)
            .order_by(KnowledgeCommonPin.order_index.asc())
            .all()
        )
        result: List[KnowledgeCommonPinResponse] = []
        for pin in pins:
            item = self._to_response(pin, user_id)
            if item:
                result.append(item)
        return result

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
