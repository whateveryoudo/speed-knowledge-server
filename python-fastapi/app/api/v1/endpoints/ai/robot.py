from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from app.ai.robot.speed_doc_robot import get_speed_doc_bot
from app.schemas.ai import RobotQuery
from app.services.robot_chat_service import RobotChatService
import json
import uuid

router = APIRouter()


@router.post("/chat")
async def chat(request: RobotQuery):
    """
    根据用户的问题，检索知识库，并返回流式响应（TODO:支持会话消息存储）。
    """
    robot_chat_service = RobotChatService(session_id=request.session_id)
    # 生成会话id
    session_id = request.session_id or str(uuid.uuid4())

    # for event in agent.stream(
    #     {"messages": [{"role": "user", "content": request.content}]},
    #     stream_mode="values",
    # ):
    #     print(event)
    def generate():
        try:
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
