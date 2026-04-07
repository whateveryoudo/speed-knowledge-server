from app.models.chat_message import ChatMessage
from sqlalchemy import func, desc
from fastapi import HTTPException
from app.schemas.chat_message import (
    ChatMessageCreate,
    ChatMessageQuery,
    ChatMessageResponse,
    ChatMessageUpdate,
)
from app.services.base_service import BaseService
from app.common.pagination import paginate_query, paginate_response
from app.schemas.response import PaginationQuery, PaginationResponse
from app.common.sorting import parse_sort_string, apply_sort_by
from sqlalchemy.orm import Session
import uuid
from collections import defaultdict
ALLOWED_SORT_FIELDS = {"created_at", "updated_at"}


class ChatMessageService(BaseService[ChatMessage]):
    def __init__(self, db: Session):
        super().__init__(db, ChatMessage)

    def create(self, chat_message_in: ChatMessageCreate):
        """创建聊天消息"""
        chat_message = ChatMessage(
            content=chat_message_in.content,
            role=chat_message_in.role,
            type=chat_message_in.type,
            link_question=chat_message_in.link_question,
            session_id=chat_message_in.session_id,
            answer_group_id=(
                chat_message_in.answer_group_id
                if chat_message_in.answer_group_id
                else str(uuid.uuid4())
            ),
            version=chat_message_in.version if chat_message_in.version else 1,
        )
        self.db.add(chat_message)
        self.db.commit()
        self.db.refresh(chat_message)
        return chat_message

    def update(self, chat_message_in: ChatMessageUpdate):
        """更新聊天消息(注意这里不是直接覆盖，而是新增一个版本)"""
        chat_message = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.answer_group_id == chat_message_in.answer_group_id)
            .order_by(ChatMessage.version.desc())
            .first()
        )
        if not chat_message:
            raise HTTPException(status_code=404, detail="消息不存在")
        new_version_message = ChatMessage(
            content=chat_message_in.content,
            role=chat_message_in.role,
            type=chat_message_in.type,
            link_question=chat_message_in.link_question,
            session_id=chat_message_in.session_id,
            answer_group_id=chat_message_in.answer_group_id,
            version=chat_message.version + 1,
            context_json=chat_message_in.context_json,
        )
        self.db.add(new_version_message)
        self.db.commit()
        self.db.refresh(new_version_message)
        return new_version_message

    def get_list(
        self, query_in: ChatMessageQuery
    ) -> PaginationResponse[ChatMessageResponse]:
        """获取聊天消息列表(带分页)"""
        group_query_base = (
            self.db.query(
                ChatMessage.answer_group_id.label("answer_group_id"),
                func.max(ChatMessage.updated_at).label("latest_updated_at"),
            )
            .filter(ChatMessage.session_id == query_in.session_id)
            .group_by(ChatMessage.answer_group_id)
        )
        # 这里直接走默认排序，不需要结合多字段，前端也不用传入
        group_query_base = group_query_base.order_by(desc("latest_updated_at"))

        group_items, total, has_more = paginate_query(
            group_query_base,
            PaginationQuery(
                page=query_in.page,
                page_size=query_in.page_size,
            ),
        )

        group_ids = [g_item.answer_group_id for g_item in group_items]

        if not group_ids:
            return paginate_response([], total, has_more, query_in)

        rows = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.answer_group_id.in_(group_ids))
            .order_by(ChatMessage.version.asc())
            .all()
        )
        mp = defaultdict(list)
        for r in rows:
            mp[r.answer_group_id].append(r)
        items: list[ChatMessageResponse] = []
        for group_id in group_ids:
            items.append(ChatMessageResponse(
                answer_group_id=group_id,
                sub_messages=mp[group_id],
            ))

        return paginate_response(items, total, has_more, query_in)
