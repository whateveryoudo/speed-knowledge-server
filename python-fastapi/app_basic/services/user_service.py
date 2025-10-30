"""用户服务"""
from optparse import Option
from sqlalchemy.orm import Session
from types import Optional, List
from app.models.user import User
from app.schemas.user import CreateUser
from app.core.security import get_password_hash
class UserService:
    """用户服务类"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """通过Id查找用户"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """通过Email查找用户"""
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self,skip = 0, limit = 100) -> List[User]:
        """查询所有用户""" 
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create(self,user_in = CreateUser) -> User:
        """创建用户"""
        hased_password = get_password_hash(user_in.password)
        user = User(
            email=user_in.email, 
            password=hased_password,
            name=user_in.name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user



