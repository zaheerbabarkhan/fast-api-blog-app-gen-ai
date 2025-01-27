from typing import Optional, List
import uuid
from pydantic import BaseModel

from app.models.post import PostStatus


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    status: PostStatus = PostStatus.DRAFT.value

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    id: uuid.UUID
    author_id: uuid.UUID

