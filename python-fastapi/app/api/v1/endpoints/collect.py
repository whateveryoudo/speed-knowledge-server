from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm.session import Session
from typing import List
from app.schemas.collect import CollectCreate, CollectResponse, CollectSearch
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.collect_service import CollectService
from app.models.collect import Collect


router = APIRouter()

@router.post("/", response_model=CollectResponse, status_code=status.HTTP_201_CREATED)
async def add_collect(
    collect_in: CollectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Collect:
    """添加资源收藏"""
    collect_service = CollectService(db)
    collect = collect_service.add_collect(current_user.id, collect_in.identifier, collect_in.resource_type)
    return collect

@router.delete("/", status_code=status.HTTP_200_OK)
async def remove_collect(
    collect_in: CollectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """取消资源收藏"""
    collect_service = CollectService(db)
    collect_service.remove_collect(current_user.id, collect_in.identifier, collect_in.resource_type)
    return None

@router.get("/list", response_model=List[CollectResponse], status_code=status.HTTP_200_OK)
async def get_collects(
    search_collect: CollectSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[CollectResponse]:
    """获取资源收藏列表"""
    collect_service = CollectService(db)
    collects = collect_service.get_collects(current_user.id, search_collect)
    return collects