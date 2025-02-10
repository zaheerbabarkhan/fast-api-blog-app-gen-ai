import logging

from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from app.api.deps import CurrentUser
from app.models.comment import Comment
from app.models.post import Post, PostStatus
from app.schemas.post import PostCreate
from app.exceptions.exceptions import DatabaseExeption


logger = logging.getLogger(__name__)

class PostCRUD:
    """
    CRUD operations for Post model.
    """

    def __init__(self, db: Session):
        """
        Initialize PostCRUD with a database session.
        
        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db

    
    def create_post(self, author: CurrentUser, post_data: PostCreate):
        """
        Create a new post.
        
        Args:
            author (CurrentUser): The author of the post.
            post_data (PostCreate): Data required to create a post.
        
        Returns:
            Post: The newly created post.
        
        Raises:
            DatabaseException: If there is an error while creating the post.
        """
        try:
            new_post = Post(**post_data.model_dump(), author_id=author.id)
            self.db.add(new_post)
            self.db.commit()
            self.db.refresh(new_post)
            return new_post
        except Exception as e:
            logger.exception("Database error while creating post with data %s", post_data)
            raise DatabaseExeption("Internal database error", ) from e

    
    def get_post(self, post_id: UUID):
        """
        Retrieve a post by its ID.
        
        Args:
            post_id (UUID): The ID of the post to retrieve.
        
        Returns:
            Post: The post with the given ID, or None if not found.
        
        Raises:
            DatabaseException: If there is an error while fetching the post.
        """
        try:
            post = self.db.query(Post).filter(Post.id == str(post_id), Post.status == PostStatus.PUBLISHED).first()
            return post
        except Exception as e:
            logger.exception(f"Database error while fetching post with id {post_id}")
            raise DatabaseExeption("Internal database error") from e

   
    def update_post(self, post_id: UUID, post_data: PostCreate):
        """
        Update an existing post.
        
        Args:
            post_id (UUID): The ID of the post to update.
            post_data (PostCreate): Data to update the post with.
        
        Returns:
            Post: The updated post, or None if not found.
        
        Raises:
            DatabaseException: If there is an error while updating the post.
        """
        try:
            post = self.get_post(post_id)
            if not post:
                return None;
            for field, value in post_data.model_dump(exclude_unset=True).items():
                setattr(post, field, value)
            self.db.commit()
            return post
        
        except Exception as e:
            logger.exception(f"Database error while updating post {post_id} with data {post_data.model_dump()}")
            raise DatabaseExeption("Internal database error") from e

   
    def get_posts(self):
        """
        Retrieve all published posts.
        
        Returns:
            List[Post]: A list of all published posts.
        
        Raises:
            DatabaseException: If there is an error while fetching the posts.
        """
        try:
            return self.db.query(Post).filter(Post.status == PostStatus.PUBLISHED).all()
        except Exception as e:
            logger.exception("Database error while fetching posts")
            raise DatabaseExeption("Internal database error") from e

    
    def delete_post(self, post: Post):
        """
        Soft delete a post by its ID.
        
        Args:
            post_id (UUID): The ID of the post to delete.
        
        Returns:
            Post: The deleted post, or None if not found.
        
        Raises:
            DatabaseException: If there is an error while deleting the post.
        """
        try:
            post.is_deleted = True
            self.db.query(Comment).filter(Comment.post_id == post.id).update({Comment.is_deleted: True}, synchronize_session=False)
            self.db.commit()
        except Exception as e:
            logger.exception(f"Database error while deleting post {post.id}")
            raise DatabaseExeption("Internal database error") from e
    