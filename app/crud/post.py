from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models.post import Post
from app.schemas.post import PostCreate

def create_post(db: Session, author : CurrentUser, post_data: PostCreate):
    new_post = Post(**post_data.model_dump(), author_id=author.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def get_post(db: Session, post_id: str):
    return db.get(Post, post_id)