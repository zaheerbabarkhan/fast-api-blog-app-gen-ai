from uuid import UUID

from app.api.deps import SessionDep
from app.models.post import Post, PostStatus
from app.models.user import User, UserRole
from app.schemas.post import PostCreate, PostQAResponse, PostSuggestionsResponse, PostUpdate
from app.crud.post import PostCRUD
from app.exceptions.exceptions import AppBaseException, ForbiddenException, QAInitException, QAInvokeException, ResourceNotFoundException, DatabaseExeption, SuggestionInvokeException, SuggestionServiceInitException, SummarizationInitException, SummarizationInvokeException
from app.services.question_answer.question_answer import QuestionAnswerService
from app.services.suggestion import SuggestionService
from app.services.summarization import SummarizationService

class PostService:
    """
    Service class for managing blog posts. This class provides methods to create, retrieve, update, delete, and summarize posts.
    """

    def __init__(self, db: SessionDep = SessionDep):
        """
        Initialize the PostService with a database session dependency.

        Args:
            db (SessionDep): Database session dependency
        """
        self.db = db
        self.post_crud = PostCRUD(db=self.db)

    def create_post(self, author, post_data: PostCreate) -> Post:
        """
        Create a new post.

        Args:
            author: The author of the post
            post_data (PostCreate): Data required to create a post

        Returns:
            Post: The created Post object

        Raises:
            DatabaseException: If there is an error in the database operation
        """
        try:
            return self.post_crud.create_post(author=author, post_data=post_data)
        except DatabaseExeption as e:
            raise AppBaseException("Cannot create post") from e

    def get_post(self, post_id: UUID) -> Post:
        """
        Retrieve a post by its ID.

        Args:
            post_id (UUID): The UUID of the post

        Returns:
            Post: The Post object

        Raises:
            ResourceNotFoundException: If the post is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            post = self.post_crud.get_post(post_id=post_id)
            if not post:
                raise ResourceNotFoundException("Post not found")
            return post
        except DatabaseExeption as e:
            raise AppBaseException("Cannot get post") from e

    def update_post(self, post_id: UUID, post_data: PostUpdate) -> Post:
        """
        Update an existing post.

        Args:
            post_id (UUID): The UUID of the post to update
            post_data (PostUpdate): Data required to update the post

        Returns:
            Post: The updated Post object

        Raises:
            ResourceNotFoundException: If the post is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            post = self.post_crud.update_post(post_id=post_id, post_data=post_data)
            if not post:
                raise ResourceNotFoundException("Post not found")
            return post
        except DatabaseExeption as e:
            raise AppBaseException("Cannot update post") from e

    def get_posts(self) -> list[Post]:
        """
        Retrieve all posts.

        Returns:
            list[Post]: A list of Post objects

        Raises:
            DatabaseException: If there is an error in the database operation
        """
        try:
            return self.post_crud.get_posts()
        except DatabaseExeption as e:
            raise AppBaseException("Cannot get posts") from e

    def delete_post(self, post_id: UUID, current_user: User) -> Post:
        """
        Delete a post by its ID.

        Args:
            post_id (UUID): The UUID of the post to delete

        Raises:
            ResourceNotFoundException: If the post is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            post = self.post_crud.get_post(post_id)

            if not post:
                raise ResourceNotFoundException("Post not found")
            if post.author_id != current_user.id and current_user.user_role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
                raise ForbiddenException("You are not authorized to delete this post")
            self.post_crud.delete_post(post)
        except ResourceNotFoundException:
            raise
        except DatabaseExeption as e:
            raise AppBaseException("Cannot delete post") from e
        
    def summarize_post(self, post_id: UUID) -> str:
        """
        Summarize the content of a post by its ID.

        Args:
            post_id (UUID): The UUID of the post to summarize

        Returns:
            str: A summary of the post content

        Raises:
            ResourceNotFoundException: If the post is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            post = self.get_post(post_id)

            if post.status != PostStatus.PUBLISHED:
                raise ResourceNotFoundException("Post not found")
            summarizarion_service = SummarizationService()
            return summarizarion_service.summarize(post.content)
        except ResourceNotFoundException:
            raise
        except (SummarizationInitException, SummarizationInvokeException) as e:
            raise AppBaseException("Cannot summarize post") from e
        except DatabaseExeption:
            raise
    
    def chat_with_post(self, post_id: UUID, question: str, current_user: User) -> PostQAResponse:
        """
        Chat with a post by its ID.

        Args:
            post_id (UUID): The UUID of the post to chat with
            question (str): The question to ask the post
            current_user (User): The current user

        Returns:
            str: The response from the post

        Raises:
            ResourceNotFoundException: If the post is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            post = self.get_post(post_id)

            if post.status != PostStatus.PUBLISHED:
                raise ResourceNotFoundException("Post not found")
            
            chat = QuestionAnswerService(user_id=current_user.id, post_id=post_id, post_content=post.content, question=question)
            answer = chat.get_answer(question=question)
            return PostQAResponse(answer=answer)
        except ResourceNotFoundException:
            raise
        except(QAInitException, QAInvokeException) as e:
            raise AppBaseException("Cannot chat with post") from e
        except DatabaseExeption:
            raise AppBaseException("Cannot chat with post")

    

    def suggest_title_tags(self, content: str) -> PostSuggestionsResponse:
        """
        Suggest a title and tags for a post based on its content.

        Args:
            content (str): The content of the post

        Returns:
            PostSuggestionsResponse: The suggested title and tags

        Raises:
            DatabaseException: If there is an error in the database operation
        """
        try:

            suggestions = SuggestionService().suggest(content=content)
            return suggestions
        except (SuggestionServiceInitException, SuggestionInvokeException) as e:
            raise AppBaseException("Cannot get suggestions") from e