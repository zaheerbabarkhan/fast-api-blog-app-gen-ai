
from sqlalchemy import SMALLINT, ForeignKey, String, Text, ARRAY
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List, Optional
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

import uuid
import enum

from app.core.db import Base
from app.models.base_model_mixin import BaseModelMixin
from app.models.user import User

class PostStatus(enum.Enum):
    PUBLISHED = 0
    DRAFT = 1

    def __int__(self):
        return self.value

class Post(Base, BaseModelMixin):
    __tablename__ = 'posts'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[int] = mapped_column(SMALLINT(), default=PostStatus.DRAFT.value)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    user: Mapped['User'] = relationship('User', back_populates='posts')