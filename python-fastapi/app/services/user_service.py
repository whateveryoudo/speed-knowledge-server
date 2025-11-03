"""用户服务"""
import email
from typing import Optional
from sqlalchemy.orm.session import Session
from app.models.user import User
from app.core.security import verify_password, get_password_hash
from app.schemas.user import UserCreate

class UserService:
    """用户服务类
    """

    def __init__(self, db:Session) -> None:
        self.db = db


    def create(self, user_in: UserCreate) -> User:
        """创建用户

        Args:
            user_in (UserCreate): 入参

        Returns:
            User: 用户
        """
        hashed_password = get_password_hash(user_in.password)
        user = User(email = user_in.email, password = hashed_password,name=user_in.name)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
        

    def get_by_email(self,email:str) -> Optional[User]:
        """根据email查询用户

        Args:
            email (str): 邮箱

        Returns:
            Optional[User]: 用户
        """
        return self.db.query(User).filter(User.email == email).first()

    def authenticate(self,email:str,password: str) -> User:
        """用户验证

        Args:
            email (str): 邮箱
            password (str): 密码

        Returns:
            User: 用户
        """
        user = self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user    
