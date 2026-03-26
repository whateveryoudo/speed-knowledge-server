from app.models.chat_session import ChatSession
from app.schemas.chat_session import (
    ChatSessionCreate,
    ChatSessionFullQuery,
    ChatSessionResponse,
    ChatSessionUpdate,
)
from app.services.base_service import BaseService
from app.common.pagination import paginate_query, paginate_response
from app.schemas.response import PaginationQuery, PaginationResponse
from sqlalchemy.orm import Session


class ChatSessionService(BaseService[ChatSession]):
    """聊天会话服务"""

    def __init__(self, db: Session):
        super().__init__(db, ChatSession)

    def create(self, chat_session_in: ChatSessionCreate):
        """创建会话"""
        chat_session = ChatSession(
            id=chat_session_in.session_id,
            user_id=chat_session_in.user_id,
            title=chat_session_in.title,
            status=chat_session_in.status,
        )
        self.db.add(chat_session)
        self.db.commit()
        self.db.refresh(chat_session)
        return chat_session

    def get_by_id(self, session_id: str) -> ChatSession:
        """根据会话ID获取会话"""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_list(
        self, query_in: ChatSessionFullQuery
    ) -> PaginationResponse[ChatSessionResponse]:
        """获取聊天消息列表(带分页)"""
        query = self.get_active_query()
        if query_in.user_id:
            query = query.filter(ChatSession.user_id == query_in.user_id)
        if query_in.title:
            query = query.filter(ChatSession.title.like(f"%{query_in.title}%"))
        if query_in.status:
            query = query.filter(ChatSession.status == query_in.status.value)
        items, total = paginate_query(
            query,
            PaginationQuery(
                page=query_in.page,
                page_size=query_in.page_size,
            ),
        )

        return paginate_response(items, total, query_in)

    def update(self, session_id: str, update_in: ChatSessionUpdate):
        """更新会话(支持多属性更新)"""
        chat_session = self.get_by_id(session_id)
        if chat_session is None:
            raise ValueError(f"会话不存在: {session_id}")
        for key, value in update_in.model_dump().items():
            if value is not None:
                setattr(chat_session, key, value)
        self.db.commit()
        self.db.refresh(chat_session)
        return chat_session
