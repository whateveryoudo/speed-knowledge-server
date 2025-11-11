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
        user = User(
            email=user_in.email,
            username=user_in.username,
            password=hashed_password,
            nickname=user_in.nickname
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
        

    def get_by_email(self, email: str) -> Optional[User]:
        """根据email查询用户

        Args:
            email (str): 邮箱

        Returns:
            Optional[User]: 用户
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """根据username查询用户

        Args:
            username (str): 用户名

        Returns:
            Optional[User]: 用户
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """根据邮箱或用户名查询用户

        Args:
            identifier (str): 邮箱或用户名

        Returns:
            Optional[User]: 用户
        """
        # 先尝试按邮箱查询
        user = self.get_by_email(identifier)
        if user:
            return user
        # 再尝试按用户名查询
        return self.get_by_username(identifier)

    def authenticate(self, identifier: str, password: str) -> Optional[User]:
        """用户验证，支持邮箱或用户名登录

        Args:
            identifier (str): 邮箱或用户名
            password (str): 密码

        Returns:
            Optional[User]: 用户，验证失败返回None
        """
        user = self.get_by_email_or_username(identifier)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user    
