from uuid import UUID
from app.api.deps import SessionDep
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.crud.user import UserCRUD
from app.exceptions.exceptions import ResourceNotFoundException, AppBaseException, ResourceAlreadyExistsException
import logging

logger = logging.getLogger(__name__)

class UserService:
    """
    Service class for managing users. This class provides methods to create, retrieve, update, and delete users.
    """

    def __init__(self, db: SessionDep = SessionDep):
        """
        Initialize the UserService with a database session dependency.

        Args:
            db (SessionDep): Database session dependency
        """
        self.db = db
        self.user_crud = UserCRUD(db=self.db)

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data (UserCreate): Data required to create a user

        Returns:
            User: The created User object

        Raises:
            ResourceAlreadyExistsException: If a user with the same email already exists
            DatabaseException: If there is an error in the database operation
        """
        try:
            existing_user = self.user_crud.get_user_by_email(user_data.email)
            if existing_user:
                logger.error(f"User with email {user_data.email} already exists")
                raise ResourceAlreadyExistsException("User with this email already exists")
            return self.user_crud.create_user(user_data=user_data)
        except AppBaseException:
            raise

    def get_user(self, user_id: UUID) -> User:
        """
        Retrieve a user by their ID.

        Args:
            user_id (UUID): The UUID of the user

        Returns:
            User: The User object

        Raises:
            ResourceNotFoundException: If the user is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            user = self.user_crud.get_user(user_id=user_id)
            if not user:
                logger.error(f"User with id {user_id} not found")
                raise ResourceNotFoundException("User not found")
            return user
        except AppBaseException :
            raise

    def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """
        Update an existing user.

        Args:
            user_id (UUID): The UUID of the user to update
            user_data (UserUpdate): Data required to update the user

        Returns:
            User: The updated User object

        Raises:
            ResourceNotFoundException: If the user is not found
            ResourceAlreadyExistsException: If a user with the same email already exists
            DatabaseException: If there is an error in the database operation
        """
        try:
            user = self.user_crud.get_user(user_id)
            if not user:
                logger.error(f"User with id {user_id} not found when trying to update with update data {user_data.model_dump()}")
                raise ResourceNotFoundException("User not found")
            
            if user_data.email:
                existing_user = self.user_crud.get_user_by_email(user_data.email)
                
                if existing_user and existing_user.id != user_id:
                    logger.error(f"User with email {user_data.email} already exists and user with user id {user_id} is trying to update")
                    raise ResourceAlreadyExistsException("User with this email already exists")
            
            user = self.user_crud.update_user(user_id=user_id, update_data=user_data)
            return user
        except AppBaseException:
            raise

    def get_users(self) -> list[User]:
        """
        Retrieve all users.

        Returns:
            list[User]: A list of User objects

        Raises:
            DatabaseException: If there is an error in the database operation
        """
        try:
            return self.user_crud.get_users()
        except AppBaseException :
            raise

    def delete_user(self, user_id: UUID) -> User:
        """
        Delete a user by their ID.

        Args:
            user_id (UUID): The UUID of the user to delete

        Raises:
            ResourceNotFoundException: If the user is not found
            DatabaseException: If there is an error in the database operation
        """
        try:
            user = self.user_crud.get_user(user_id)
            if not user:
                raise ResourceNotFoundException("User not found")
            
            return self.user_crud.delete_user(user)
        
        except ResourceNotFoundException:
            raise
        except AppBaseException:
            raise