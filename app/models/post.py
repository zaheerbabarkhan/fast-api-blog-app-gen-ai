
from datetime import datetime
from sqlalchemy import SMALLINT, ForeignKey, String, Text, ARRAY, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List, Optional
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

import uuid
import enum

from app.core.db import Base
from app.models.base_model_mixin import BaseModelMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class PostStatus(enum.Enum):
    PUBLISHED = "PUBLISHED"
    DRAFT = "DRAFT"

    def __int__(self):
        return self.value

class Post(Base, BaseModelMixin):
    __tablename__ = 'posts'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4()
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[int] = mapped_column(String(20), default=PostStatus.DRAFT.value)
    _tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now()) 
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    author: Mapped['User'] = relationship('User', back_populates='posts')

    @property
    def tags_list(self) -> List[str]:
        return self.tags.split(',') if self.tags else []

    @tags_list.setter
    def tags_list(self, value: List[str]):
        self.tags = ','.join(value)