"""用户端点"""
from re import A
from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas.user import UserResponse, UserCreate
from sqlalchemy.orm.session import Session
from app.core.deps import get_db
from app.models.user import User
from app.services.user_service import UserService

router = APIRouter()

@router.post('/', response_model=UserResponse,status_code = status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate,db: Session = Depends(get_db)) -> User:
    """创建用户

    Args:
        user_in (UserCreate): 入参
        db (Session, optional): _description_. Defaults to Depends(get_db).

    Returns:
        User: 用户对象
    """
    
    user_service = UserService(db)
    existing_user = user_service.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail = "该邮箱已注册")

    return user_service.create(user_in)

