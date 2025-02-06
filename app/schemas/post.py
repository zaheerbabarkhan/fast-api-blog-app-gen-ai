from datetime import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, model_validator

from app.models.post import PostStatus
from app.schemas.comment import CommentResponse
from app.schemas.user import UserResponse


class PostBase(BaseModel):
    title: str
    content: str
    tags_list: Optional[List[str]] = []
    status: PostStatus = PostStatus.DRAFT.value

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags_list: Optional[List[str]] = []
    status: Optional[PostStatus] = None

    @model_validator(mode="after")
    def check_at_least_one_field(cls, values):
        values_dict = values.dict(exclude_unset=True)
        if not any(values_dict.values()):
            raise ValueError('Provide title, content, tags_list or status to update.')
        return values

class PostResponse(PostBase):
    id: uuid.UUID
    author_id: uuid.UUID
    author: UserResponse

class PostListResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    author: UserResponse
    title: str
    tags_list: List[str]
    status: PostStatus
    created_at: datetime
    updated_at: datetime


class PostSummaryResponse(BaseModel):
    summary: str

class PostSuggestionsRequest(BaseModel):
    content: str

class PostSuggestionsResponse(BaseModel):
    title: str
    tags_list: List[str]

class PostQuestionAnswerRequest(BaseModel):
    question: str

