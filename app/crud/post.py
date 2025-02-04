from sqlalchemy.orm import Session, joinedload

from app.api.deps import CurrentUser
from app.models.post import Post, PostStatus
from app.schemas.post import PostCreate

def create_post(db: Session, author : CurrentUser, post_data: PostCreate):
    new_post = Post(**post_data.model_dump(), author_id=author.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def get_post(db: Session, post_id: str):
    return db.query(Post).options(joinedload(Post.comments)).filter(Post.id == post_id and Post.status == PostStatus.PUBLISHED).first()

def update_post(db: Session, post: Post, post_data: PostCreate):
    for field, value in post_data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    return post

def get_posts(db: Session):
    return db.query(Post).filter(Post.status == PostStatus.PUBLISHED).all()