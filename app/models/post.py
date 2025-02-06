
from datetime import datetime
from sqlalchemy import  ForeignKey, String, Text, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List, Optional, TYPE_CHECKING


import uuid
import enum

from app.core.config.db import Base
from app.models.base_model_mixin import BaseModelMixin
from app.models.comment import Comment

if TYPE_CHECKING:
    from app.models.user import User
    

class PostStatus(str,enum.Enum):
    PUBLISHED = "PUBLISHED"
    DRAFT = "DRAFT"
    

class Post(Base, BaseModelMixin):
    __tablename__ = 'posts'

    id: Mapped[uuid.UUID] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=PostStatus.DRAFT.value)
    _tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now()) 
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    author_id: Mapped[uuid.UUID] = mapped_column(String, ForeignKey('users.id'), nullable=False)

    author: Mapped['User'] = relationship('User', back_populates='posts')
    comments: Mapped[List['Comment']] = relationship('Comment', back_populates='post', lazy="select")
    
    @property
    def tags_list(self) -> List[str]:
        return self._tags.split(',') if self._tags else []

    @tags_list.setter
    def tags_list(self, value: List[str]):
        self._tags = ','.join(value)