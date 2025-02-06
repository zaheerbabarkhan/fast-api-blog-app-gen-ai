from sqlalchemy.orm import Session, joinedload

from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreateRequest 

def create_comment(db: Session, commenter: User, post_id: str, comment_data: CommentCreateRequest) -> Comment:
    comment = Comment(
        post_id=post_id,
        commenter_id=commenter.id,
        content=comment_data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_post_comments(db: Session, post_id: str) -> list[Comment]:
    return db.query(Comment).options(joinedload(Comment.replies)).filter(Comment.post_id == post_id).all()

def get_comment(db: Session, comment_id: str) -> Comment:
    return db.query(Comment).filter(Comment.id == comment_id).first()

def reply_to_comment(db: Session, replier: User, parent_comment: Comment,reply_data: CommentCreateRequest) -> Comment:
    comment = Comment(
        post_id=parent_comment.post_id,
        parent_comment_id=parent_comment.id,
        commenter_id=replier.id,
        content=reply_data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    print("this is the comment", comment.__dict__)
    return comment

def delete_comment(db: Session, comment: Comment):
    # comment.is_deleted = True
    # db.commit()
    # Set is_deleted to True for the comment and all its replies in the database
    db.query(Comment).filter(
        (Comment.id == comment.id) | (Comment.parent_comment_id == comment.id)
    ).update({Comment.is_deleted: True}, synchronize_session=False)
    db.commit()
    return

def update_comment(db: Session, comment: Comment, comment_data: CommentCreateRequest) -> Comment:
    comment.content = comment_data.content
    db.commit()
    return comment