from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from app.ai.robot.speed_doc_robot import get_speed_doc_bot
from app.schemas.ai import RobotQuery
from langchain_core.messages import AIMessage
import json

router = APIRouter()


@router.post("/chat")
async def chat(request: RobotQuery):
    """
    根据用户的问题，检索知识库，并返回流式响应（TODO:支持会话消息存储）。
    """
    agent = get_speed_doc_bot()
    # for event in agent.stream(
    #     {"messages": [{"role": "user", "content": request.content}]},
    #     stream_mode="values",
    # ):
    #     print(event)
    def generate():
        last_send = ""
        try:
            for event in agent.stream(
                {"messages": [{"role": "user", "content": request.content}]},
                stream_mode="values",
            ):
                messages = [message for message in event.get("messages", []) if isinstance(message, AIMessage)]
                if not messages:
                    continue
                print(messages)
                content = messages[-1].content
                if not content:
                    continue
                if content.startswith(last_send):
                    delta = content[len(last_send) :]
                else:
                    delta = content
                last_send = content
                yield f"data: {json.dumps({'content': delta})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
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
