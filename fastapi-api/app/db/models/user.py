import base64
import hashlib
import hmac
import re
from datetime import datetime
from typing import List, Optional

from app.db.base import session_getter
from app.db.models.base import (
    SQLModelSerializable,
    SQLModelSerializableTime,
    valid_email,
    valid_name,
    valid_password,
    valid_phone,
)
from pydantic import field_validator
from sqlalchemy import Column, DateTime, String, func, text
from sqlmodel import Field, SQLModel, select

# 默认普通用户角色的ID
DefaultRole = "user"
# 超级管理员角色ID
AdminRole = "admin"


class UserBase(SQLModelSerializable):
    user_name: str = Field(index=True, unique=True)
    phone_number: Optional[str] = Field(index=True)
    remark: Optional[str] = Field(index=False)
    last_login_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")), description="上次登录时间"
    )


class User(UserBase, SQLModelSerializableTime, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str = Field(default=DefaultRole)
    delete: int = Field(default=0)
    current_token: str = Field(sa_column=Column(String(length=512)), default="")
    password: str = Field(default="")
    salt: str = Field(default="", description="密码salt值")
    password_update_time: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
        description="密码最近的修改时间",
    )

    @property
    def is_admin(self):
        return self.role == AdminRole

    @classmethod
    def encrypt_password(cls, password: str, salt: str) -> str:
        """加密

        Args:
            password (Union[str, bytes]): 密码明文
            salt (Union[str, bytes]): 盐值

        Returns:
            str: 加密后的 Base64 编码字符串
        """
        if isinstance(password, str):
            password = bytes(password, encoding="utf-8")
        if isinstance(salt, str):
            salt = bytes(salt, encoding="utf-8")

        hashing = hmac.new(password, salt, hashlib.sha256)
        return base64.b64encode(hashing.digest()).decode("utf-8")


class UserRead(SQLModelSerializableTime, UserBase):
    id: Optional[int]
    role: Optional[str]


class UserLoginRead(UserRead):
    current_token: Optional[str]


class UserQuery(SQLModelSerializable):
    id: Optional[int]
    user_name: Optional[str]


class UserLogin(SQLModelSerializable):
    password: str
    phone_number: str
    # captcha_key: Optional[str]
    # captcha: Optional[str]


class UserCreate(SQLModelSerializable):
    user_name: Optional[str]
    phone_number: Optional[str]
    password: Optional[str]
    # captcha_key: Optional[str]
    # captcha: Optional[str]

    @field_validator("user_name")
    def validate_str(v):
        return valid_name(v)

    @field_validator("password")
    def valid_password(password: str):
        return valid_password(password)

    @field_validator("phone_number")
    def valid_phone(phone: str):
        return valid_phone(phone)

    # @field_validator('email')
    # def valid_email(v: str):
    #     return valid_email(v)


class UserUpdate(SQLModelSerializable):
    id: int
    delete: Optional[int] = 0
    user_name: Optional[str] = Field(default="")
    password: Optional[str] = Field(default="")


class UserDaoabb(UserBase):
    @classmethod
    def get_user(cls, user_id: int) -> User | None:
        with session_getter() as session:
            statement = select(User).where(User.id == user_id)
            return session.exec(statement).first()

    @classmethod
    def get_user_by_ids(cls, user_ids: List[int]) -> List[User] | None:
        with session_getter() as session:
            statement = select(User).where(User.id.in_(user_ids))
            return session.exec(statement).all()

    @classmethod
    def update_user(cls, user: User) -> User:
        with session_getter() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @classmethod
    def filter_users(cls, user_ids: List[int], keyword: str = None, page: int = 0, limit: int = 0) -> (List[User], int):
        statement = select(User)
        count_statement = select(func.count(User.id))
        if user_ids:
            statement = statement.where(User.id.in_(user_ids))
            count_statement = count_statement.where(User.id.in_(user_ids))
        if keyword:
            statement = statement.where(User.user_name.like(f"%{keyword}%"))
            count_statement = count_statement.where(User.user_name.like(f"%{keyword}%"))
        if page and limit:
            statement = statement.offset((page - 1) * limit).limit(limit)
        statement = statement.order_by(User.id.desc())
        with session_getter() as session:
            return session.exec(statement).all(), session.scalar(count_statement)

    @classmethod
    def get_unique_user_by_name(cls, user_name: str) -> User | None:
        with session_getter() as session:
            statement = select(User).where(User.user_name == user_name)
            return session.exec(statement).first()

    @classmethod
    def create_user(cls, db_user: User) -> User:
        with session_getter() as session:
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user

    @classmethod
    def add_user_and_default_role(cls, user: User) -> User:
        """
        新增用户，并添加默认角色
        """
        with session_getter() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            db_user_role = UserRole(user_id=user.id, role_id=DefaultRole)
            session.add(db_user_role)
            session.commit()
            session.refresh(user)
            return user

    @classmethod
    def add_user_and_admin_role(cls, user: User) -> User:
        """
        新增用户，并添加超级管理员角色
        """
        with session_getter() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            db_user_role = UserRole(user_id=user.id, role_id=AdminRole)
            session.add(db_user_role)
            session.commit()
            session.refresh(user)
            return user
