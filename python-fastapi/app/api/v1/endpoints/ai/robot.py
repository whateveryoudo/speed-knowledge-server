from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.ai.robot.speed_doc_robot import get_speed_doc_bot
from app.schemas.ai import RobotQuery
from app.schemas.chat_session import ChatSessionCreate, ChatSessionStatus
from app.schemas.chat_message import ChatMessageQuery, ChatMessageResponse
from app.schemas.response import PaginationResponse
from app.services.robot_chat_service import RobotChatService
from app.services.chat_session_service import ChatSessionService
from app.services.chat_message_service import ChatMessageService
from app.schemas.chat_session import (
    ChatSessionQuery,
    ChatSessionResponse,
    ChatSessionFullQuery,
)
from app.models.user import User
import json
import uuid

router = APIRouter()


@router.post("/chat/stream", response_class=StreamingResponse)
async def chat_stream(
    request: RobotQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    根据用户的问题，检索知识库，并返回流式响应（TODO:支持会话消息存储）。
    """

    chat_session_service = ChatSessionService(db)
    # 生成会话id
    session_id = request.session_id or str(uuid.uuid4())
    robot_chat_service = RobotChatService(db, session_id)

    # for event in agent.stream(
    #     {"messages": [{"role": "user", "content": request.content}]},
    #     stream_mode="values",
    # ):
    #     print(event)
    def generate():
        try:
            # 创建会话
            chat_session = chat_session_service.get_by_id(session_id)
            if not chat_session:
                chat_session_service.create(
                    ChatSessionCreate(
                        id=session_id,
                        user_id=current_user.id,
                        title=request.content[:30],
                        status=ChatSessionStatus.ACTIVE,
                    )
                )
            for event in robot_chat_service.stream_events(
                request.content,
                session_id,
                request.answer_group_id,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except HTTPException as e:
            yield f"data: {json.dumps({'event': 'error', 'data': e.detail})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/chat/history", response_model=PaginationResponse[ChatSessionResponse])
async def chat_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    sort: str = Query(default="updated_at:desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginationResponse[ChatSessionResponse]:
    """
    分页获取会话历史记录。
    """
    chat_session_service = ChatSessionService(db)
    # 追加一些其他参数
    return chat_session_service.get_list(
        ChatSessionFullQuery(
            page = page,
            page_size = page_size,
            user_id = current_user.id,
            sort = sort,
            status = ChatSessionStatus.ACTIVE,
        )
    )


@router.get("/chat/message/{session_id}", response_model=PaginationResponse[ChatMessageResponse])
async def chat_message(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    sort: str = Query(default="updated_at:desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginationResponse[ChatMessageResponse]:
    """
    分页获取此次对话会话消息记录。
    """
    chat_message_service = ChatMessageService(db)
    # 参数拼接
    return chat_message_service.get_list(
        ChatMessageQuery(
            page = page,
            page_size = page_size,
            sort = sort,
            session_id = session_id,
        )
    )
