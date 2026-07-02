from fastapi import APIRouter, Depends
from app.schemas.search import SearchQuery, SearchResponse
from app.services.search_service import SearchService
from app.core.deps import get_current_user, get_db
from app.models.user import User
from sqlalchemy.orm.session import Session

router = APIRouter()


@router.post("/")
async def search(
    query_in: SearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """通用搜索功能"""
    search_service = SearchService(db)
    return search_service.search(current_user.id, query_in)
