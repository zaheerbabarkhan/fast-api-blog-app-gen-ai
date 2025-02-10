from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

import uuid

from app.core.config.database.db import Base
from app.models.base_model_mixin import BaseModelMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.post import Post

class SentimentEnum(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    INAPPROPRIATE = "Inappropriate"
    NOT_ANALYZED = "Not Analyzed"

class Comment(Base, BaseModelMixin):
    __tablename__ = 'comments'

    id: Mapped[uuid.UUID] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    post_id: Mapped[Optional[uuid.UUID]] = mapped_column(String, ForeignKey('posts.id'), nullable=True)
    parent_comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(String, ForeignKey('comments.id'), nullable=True)
    commenter_id: Mapped[uuid.UUID] = mapped_column(String, ForeignKey('users.id'), nullable=False)

    sentiment: Mapped[SentimentEnum] = mapped_column(String, default=SentimentEnum.NOT_ANALYZED)

    commenter: Mapped['User'] = relationship('User', back_populates='comments')
    post: Mapped['Post'] = relationship('Post', back_populates='comments')
    replies: Mapped[List['Comment']] = relationship('Comment', back_populates='parent_comment', remote_side=[parent_comment_id])
    parent_comment: Mapped[Optional['Comment']] = relationship('Comment', back_populates='replies', remote_side=[id])
