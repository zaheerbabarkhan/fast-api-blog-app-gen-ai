from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, func
from sqlalchemy.dialects.postgresql import UUID

import uuid
import enum

from app.models.base_model_mixin import BaseModelMixin
from app.models.post import Post
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.comment import Comment

class UserRole(str, enum.Enum):
        SUPER_ADMIN = "SUPER_ADMIN"
        ADMIN = "ADMIN"
        AUTHOR = "AUTHOR"
        READER = "READER"

        def __str__(self):
            return self.value

class UserStatus(enum.Enum):
    IN_ACTIVE = "IN_ACTIVE"
    ACTIVE = "ACTIVE"

    def __int__(self):                                   
        return self.value

class User(Base, BaseModelMixin):
    __tablename__= "users"

    id: Mapped[uuid.UUID] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    user_name: Mapped[str] = mapped_column(String(20), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default=UserStatus.ACTIVE.value)
    _user_role: Mapped[str] = mapped_column("user_role", String(50), default=UserRole.READER.value)
    created_at: Mapped[datetime] = mapped_column(default=func.now()) 
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now()) 
    
    @property
    def user_role(self) -> UserRole:
        return UserRole(self._user_role)

    @user_role.setter
    def user_role(self, value: UserRole):
        self._user_role = value.value

    posts: Mapped[List['Post']] = relationship('Post', back_populates='author')
    comments: Mapped[List['Comment']] = relationship('Comment', back_populates='commenter')