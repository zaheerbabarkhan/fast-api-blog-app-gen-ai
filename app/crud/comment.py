import logging
from sqlalchemy.orm import Session, joinedload
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreateRequest
from app.exceptions.exceptions import DatabaseExeption

logger = logging.getLogger(__name__)

class CommentCRUD:
    """
    CRUD operations for Comment model.
    """

    def __init__(self, db: Session):
        """
        Initialize CommentCRUD with a database session.
        
        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db

    def create_comment(self, commenter: User, post_id: str, comment_data: CommentCreateRequest) -> Comment:
        """
        Create a new comment.
        
        Args:
            commenter (User): The user creating the comment.
            post_id (str): The ID of the post to comment on.
            comment_data (CommentCreateRequest): Data required to create a comment.
        
        Returns:
            Comment: The newly created comment.
        
        Raises:
            DatabaseException: If there is an error while creating the comment.
        """
        try:
            comment = Comment(
                post_id=post_id,
                commenter_id=commenter.id,
                content=comment_data.content,
            )
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            return comment
        except Exception as e:
            logger.exception("Database error while creating comment with data %s", comment_data)
            raise DatabaseExeption("Internal database error") from e

    def get_post_comments(self, post_id: str) -> list[Comment]:
        """
        Retrieve all comments for a post.
        
        Args:
            post_id (str): The ID of the post.
        
        Returns:
            list[Comment]: A list of comments for the post.
        
        Raises:
            DatabaseException: If there is an error while fetching the comments.
        """
        try:
            return self.db.query(Comment).options(joinedload(Comment.replies)).filter(Comment.post_id == post_id).all()
        except Exception as e:
            logger.exception("Database error while fetching comments for post with id %s", post_id)
            raise DatabaseExeption("Internal database error") from e

    def get_comment(self, comment_id: str) -> Comment:
        """
        Retrieve a comment by its ID.
        
        Args:
            comment_id (str): The ID of the comment.
        
        Returns:
            Comment: The comment with the given ID, or None if not found.
        
        Raises:
            DatabaseException: If there is an error while fetching the comment.
        """
        try:
            return self.db.query(Comment).filter(Comment.id == comment_id).first()
        except Exception as e:
            logger.exception("Database error while fetching comment with id %s", comment_id)
            raise DatabaseExeption("Internal database error") from e

    def reply_to_comment(self, replier: User, parent_comment: Comment, reply_data: CommentCreateRequest) -> Comment:
        """
        Reply to an existing comment.
        
        Args:
            replier (User): The user replying to the comment.
            parent_comment (Comment): The parent comment to reply to.
            reply_data (CommentCreateRequest): Data required to create the reply.
        
        Returns:
            Comment: The newly created reply comment.
        
        Raises:
            DatabaseException: If there is an error while creating the reply.
        """
        try:
            comment = Comment(
                post_id=parent_comment.post_id,
                parent_comment_id=parent_comment.id,
                commenter_id=replier.id,
                content=reply_data.content,
            )
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            logger.info("Reply created successfully: %s", comment.__dict__)
            return comment
        except Exception as e:
            logger.exception("Database error while replying to comment with data %s", reply_data)
            raise DatabaseExeption("Internal database error") from e

    def delete_comment(self, comment: Comment):
        """
        Soft delete a comment by its ID.
        
        Args:
            comment (Comment): The comment to delete.
        
        Raises:
            DatabaseException: If there is an error while deleting the comment.
        """
        try:
            comment.is_deleted = True
            self.db.commit()
            self.delete_replies(comment.id)
            logger.info("Comment and its replies deleted successfully: %s", comment.id)
        except Exception as e:
            logger.exception("Database error while deleting comment with id %s", comment.id)
            raise DatabaseExeption("Internal database error") from e
        
    def delete_replies(self, comment_id: str):
        """
        Soft delete all replies to a comment.
        
        Args:
            comment_id (str): The ID of the comment.
        
        Raises:
            DatabaseException: If there is an error while deleting the replies.
        """
        try:
            self.db.query(Comment).filter(Comment.parent_comment_id == comment_id).update({Comment.is_deleted: True}, synchronize_session=False)
            self.db.commit()
            logger.info("Replies deleted successfully for comment with id %s", comment_id)
        except Exception as e:
            logger.exception("Database error while deleting replies for comment with id %s", comment_id)
            raise DatabaseExeption("Internal database error") from e