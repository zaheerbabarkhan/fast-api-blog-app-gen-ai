import logging

from uuid import UUID
from starlette.requests import Request


from app.api.deps import SessionDep
from app.crud.post import PostCRUD
from app.models.comment import Comment
from app.models.user import User, UserRole
from app.schemas.comment import CommentCreateRequest
from app.crud.comment import CommentCRUD
from app.exceptions.exceptions import AppBaseException, ForbiddenException, ResourceNotFoundException, DatabaseExeption

logger = logging.getLogger(__name__)

class CommentService:
    """
    Service class for managing comments. This class provides methods to create, retrieve, reply to, update, and delete comments.
    """

    def __init__(self, db: SessionDep):
        """
        Initialize the CommentService with a database session dependency.

        Args:
            db (SessionDep): Database session dependency
            request (Request): The current request object
        """
        self.db = db
        self.post_crud = PostCRUD(db=self.db)
        self.comment_crud = CommentCRUD(db=self.db)

    def create_comment(self, post_id: UUID, comment_data: CommentCreateRequest, author: User) -> Comment:
        """
        Create a new comment.

        Args:
            post_id (UUID): The ID of the post to comment on
            comment_data (CommentCreateRequest): Data required to create a comment
            author (User): The user creating the comment

        Returns:
            Comment: The created Comment object

        Raises:
            DatabaseException: If there is an error in the database operation
        """
        try:
            logger.info(f"Creating a new comment for post {post_id} by user {author.id}")
            return self.comment_crud.create_comment(commenter=author, post_id=str(post_id), comment_data=comment_data)
        except DatabaseExeption as e:
            logger.error(f"Error while creating comment: {str(e)}")
            raise AppBaseException("Cannot create comment") from e

    def get_post_comments(self, post_id: UUID) -> list[Comment]:
        """
        Retrieve all comments for a post.

        Args:
            post_id (UUID): The ID of the post

        Returns:
            list[Comment]: A list of Comment objects

        Raises:
            DatabaseException: If there is an error in the database operation
        """
        try:
            post = self.post_crud.get_post(post_id)
            if not post:
                raise ResourceNotFoundException("Post not found")
            
            logger.info(f"Retrieving comments for post {post_id}")
            return self.comment_crud.get_post_comments(post_id=str(post_id))
        except DatabaseExeption as e:
            logger.error(f"Error while retrieving comments for post {post_id}: {str(e)}")
            raise AppBaseException("Cannot get comments") from e

    def get_comment(self, comment_id: UUID) -> Comment:
        """
        Retrieve a comment by its ID.

        Args:
            comment_id (UUID): The ID of the comment

        Returns:
            Comment: The Comment object

        Raises:
            ResourceNotFoundException: If the comment is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            logger.info(f"Retrieving comment {comment_id}")
            comment = self.comment_crud.get_comment(comment_id=str(comment_id))
            if not comment:
                raise ResourceNotFoundException("Comment not found")
            return comment
        
        except ResourceNotFoundException as e:
            logger.warning(f"Comment {comment_id} not found: {str(e)}")
            raise
        
        except DatabaseExeption as e:
            raise AppBaseException("Cannot get comment") from e

    def reply_to_comment(self, comment_id: UUID, reply_data: CommentCreateRequest, author: User) -> Comment:
        """
        Reply to an existing comment.

        Args:
            post_id (UUID): The ID of the post the comment is associated with
            comment_id (UUID): The ID of the comment to reply to
            reply_data (CommentCreateRequest): Data required to create the reply
            author (User): The user replying to the comment

        Returns:
            Comment: The created reply Comment object

        Raises:
            ResourceNotFoundException: If the parent comment is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            logger.info(f"Replying to comment {comment_id} by user {author.id}")
            parent_comment = self.get_comment(comment_id)
            return self.comment_crud.reply_to_comment(replier=author, parent_comment=parent_comment, reply_data=reply_data)
        except ResourceNotFoundException as e:
            logger.warning(f"Parent comment {comment_id} not found: {str(e)}")
            raise
        except DatabaseExeption as e:
            raise AppBaseException("Cannot reply to comment") from e

    def delete_comment(self, comment_id: UUID, current_user: User) -> None:
        """
        Delete a comment by its ID.

        Args:
            comment_id (UUID): The ID of the comment to delete
            current_user (User): The current user

        Raises:
            ResourceNotFoundException: If the comment is not found
            ForbiddenException: If the user is not authorized to delete the comment
            DatabaseException: If there is an error in the database operation
        """
        try:
            logger.info(f"Deleting comment {comment_id} by user {current_user.id}")
            comment = self.get_comment(comment_id)

            if comment.commenter_id != current_user.id and current_user.user_role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
                raise ForbiddenException("You are not authorized to delete this comment")
            
            self.comment_crud.delete_comment(comment)
        
        except ResourceNotFoundException as e:
            logger.warning(f"Comment {comment_id} not found: {str(e)}")
            raise
        
        except ForbiddenException as e:
            logger.warning(f"User {current_user.id} not authorized to delete comment {comment_id}: {str(e)}")
            raise
        
        except DatabaseExeption as e:
            raise AppBaseException("Cannot delete comment") from e

    def update_comment(self, comment_id: UUID, comment_data: CommentCreateRequest, current_user: User) -> Comment:
        """
        Update a comment by its ID.

        Args:
            comment_id (UUID): The ID of the comment to update
            comment_data (CommentCreateRequest): Data required to update the comment
            current_user (User): The current user

        Returns:
            Comment: The updated Comment object

        Raises:
            ResourceNotFoundException: If the comment is not found
            ForbiddenException: If the user is not authorized to update the comment
            DatabaseException: If there is an error in the database operation
        """
        try:
            logger.info(f"Updating comment {comment_id} by user {current_user.id}")
            comment = self.get_comment(comment_id)
            
            if comment.commenter_id != current_user.id and current_user.user_role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
                raise ForbiddenException("You are not authorized to update this comment")
            
            comment.content = comment_data.content
            self.db.commit()
            self.db.refresh(comment)
            return comment
        
        except ResourceNotFoundException as e:
            logger.warning(f"Comment {comment_id} not found: {str(e)}")
            raise
        
        except ForbiddenException as e:
            logger.warning(f"User {current_user.id} not authorized to update comment {comment_id}: {str(e)}")
            raise
        
        except DatabaseExeption as e:
            raise AppBaseException("Cannot update comment") from e