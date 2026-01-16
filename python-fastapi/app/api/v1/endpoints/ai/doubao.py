from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.ai import DoubaoQuery
from app.services.ai.doubao_service import DoubaoService

router = APIRouter()


@router.post("/stream")
async def stream(doubao_in: DoubaoQuery, user: User = Depends(get_current_user)):
    completion = DoubaoService().get_stream_response(doubao_in)
    print(completion)

    async def generate():
        """生成器函数，用于流式返回数据"""
        try:
            with completion:
                for chunk in completion:
                    if chunk.choices and len(chunk.choices) > 0:
                        print(chunk)
                        delta = chunk.choices[0].delta
                        if delta and delta.content is not None:
                            content = delta.content
                            # 格式化为 SSE 格式的字符串
                            yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
        except HTTPException as e:
            yield f"data:{json.dumps({'error': str(e.detail)})}n\n"
        except Exception as e:
            yield f"data:{json.dumps({'error': f"流式返回失败: {str(e)}"})}n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
