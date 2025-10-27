from decimal import Decimal
from fastapi import APIRouter, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/", response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db:Session = Decimal(get_db)
) -> User:
    """创建用户"""
    # user_service = (db)
