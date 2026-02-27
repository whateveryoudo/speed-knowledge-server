from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ai import CheckDocumentRequest, CheckDocumentResponse
from app.core.deps import get_db
from sqlalchemy.orm import Session
from app.agent.document.detection import call_llm_for_suggestions

router = APIRouter()


@router.post("/check", response_model=CheckDocumentResponse)
async def check_document(
    payload: CheckDocumentRequest, db: Session = Depends(get_db)
) -> CheckDocumentResponse:
    """检查文档

    Args:
        payload (CheckDocumentRequest): tiptap 文档结构(json)
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        CheckDocumentResponse: LLM返回建议
    """
    try:
        suggestions = call_llm_for_suggestions(payload.doc, payload.rules)
        return CheckDocumentResponse(suggestions=suggestions)
    except Exception as e:
        print(f"AI检测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
