from uuid import UUID
from app.api.deps import SessionDep
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.crud.user import UserCRUD
from app.exceptions.exceptions import DatabaseExeption, ForbiddenException, ResourceNotFoundException, AppBaseException, ResourceAlreadyExistsException
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
        except DatabaseExeption as e:
            raise AppBaseException("Cannot get users") from e

    
    def activate_user(self, user_id: UUID, current_admin: User) -> User:
        """
        Activate a user.

        Args:
            user_id (UUID): The UUID of the user to activate

        Returns:
            User: The activated User object

        Raises:
            ResourceNotFoundException: If the user is not found
            ResourceAlreadyExistsException: If the user is already active
            ForbiddenException: If the current admin does not have permission to activate the user
            DatabaseException: If there is an error in the database operation
        """
        try:
            user = self.user_crud.get_user(user_id)
            if not user:
                logger.error(f"User with id {user_id} not found")
                raise ResourceNotFoundException("User not found")
            
            if user.status == UserStatus.ACTIVE.value:
                logger.error(f"User with id {user_id} is already active")
                raise ResourceAlreadyExistsException("User already active")
                
            if user.user_role == UserRole.ADMIN and current_admin.user_role != UserRole.SUPER_ADMIN:
                logger.error(f"User with id {current_admin.id} does not have permission to activate admin user with id {user_id}")
                raise ForbiddenException("Only super admin can activate admin")
            
            activated_user = self.user_crud.activate_user(user)
            logger.info(f"User with id {user_id} has been activated by admin with id {current_admin.id}")
            return activated_user
        
        except ResourceNotFoundException as e:
            logger.error(f"ResourceNotFoundException: {str(e)}")
            raise

        except ResourceAlreadyExistsException as e:
            logger.error(f"ResourceAlreadyExistsException: {str(e)}")
            raise

        except ForbiddenException as e:
            logger.error(f"ForbiddenException: {str(e)}")
            raise

        except DatabaseExeption as e:
            logger.error(f"DatabaseExeption: {str(e)}")
            raise AppBaseException("Cannot activate user") from e