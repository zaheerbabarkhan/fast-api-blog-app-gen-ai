from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel


class CommentCreateRequest(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: uuid.UUID
    content: str
    commenter_id: uuid.UUID
    post_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    parent_comment_id: Optional[uuid.UUID] = None
    
    
class CommentResponseWithReplies(CommentResponse):
    replies: List[CommentResponse] = []

class CommentUpdateRequest(BaseModel):
    content: str