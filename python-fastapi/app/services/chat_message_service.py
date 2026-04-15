from app.models.chat_message import ChatMessage
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
            suggestions=chat_message_in.suggestions,
        )
        self.db.add(chat_message)
        self.db.commit()
        self.db.refresh(chat_message)
        return chat_message

    def update(self, chat_message_in: ChatMessageUpdate):
        """更新聊天消息"""
        chat_message = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.id == chat_message_in.id)
            .first()
        )
        if not chat_message:
            raise HTTPException(status_code=404, detail="消息不存在")
        chat_message.content = chat_message_in.content
        chat_message.suggestions = chat_message_in.suggestions
        self.db.commit()
        self.db.refresh(chat_message)
        return chat_message

    def get_list(
        self, query_in: ChatMessageQuery
    ) -> PaginationResponse[ChatMessageResponse]:
        """获取聊天消息列表(带分页)"""
        query = self.db.query(ChatMessage)
        if query_in.session_id:
            query = query.filter(ChatMessage.session_id == query_in.session_id)

        spec = parse_sort_string(query_in.sort, default="updated_at:desc")
        query = apply_sort_by(
            query,
            ChatMessage,
            sort_spec=spec,
            allowed_fields=ALLOWED_SORT_FIELDS,
            default_order=None,
        )

        items, total, has_more = paginate_query(
            query,
            PaginationQuery(
                page=query_in.page,
                page_size=query_in.page_size,
            ),
        )

        return paginate_response(items, total, has_more, query_in)
