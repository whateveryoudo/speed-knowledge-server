from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.ai.robot.speed_doc_robot import get_speed_doc_bot
from app.schemas.ai import RobotQuery
from app.schemas.chat_session import ChatSessionCreate, ChatSessionStatus
from app.services.robot_chat_service import RobotChatService
from app.services.chat_session_service import ChatSessionService
from app.models.user import User
import json
import uuid

router = APIRouter()


@router.post("/chat")
async def chat(
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
                yield f"data: {json.dumps({'session_id': session_id}, ensure_ascii=False)}\n\n"
            for event in robot_chat_service.stream_events(
                request.content,
                session_id,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except HTTPException as e:
            yield f"data: {json.dumps({'error': e.detail})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
