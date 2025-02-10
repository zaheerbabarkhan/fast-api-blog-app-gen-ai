import logging
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.exceptions.exceptions import DatabaseExeption

logger = logging.getLogger(__name__)

class UserCRUD:
    """
    CRUD operations for User model.
    """

    def __init__(self, db: Session):
        """
        Initialize UserCRUD with a database session.
        
        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data (UserCreate): Data required to create a user.
        
        Returns:
            User: The newly created user.
        
        Raises:
            DatabaseException: If there is an error while creating the user.
        """
        try:
            user_data.password = get_password_hash(user_data.password)
            new_user = User(**user_data.model_dump())

            if user_data.user_role == UserRole.ADMIN or user_data.user_role == UserRole.AUTHOR:
                new_user.status = UserStatus.IN_ACTIVE
            print("this is new user", new_user)
            new_user = User(**user_data.model_dump())
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except Exception as e:
            logger.exception("Database error while creating user with data %s", user_data)
            raise DatabaseExeption("Internal database error") from e

    def get_user(self, user_id: UUID) -> User:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id (UUID): The ID of the user to retrieve.
        
        Returns:
            User: The user with the given ID, or None if not found.
        
        Raises:
            DatabaseException: If there is an error while fetching the user.
        """
        try:
            user = self.db.get(User, str(user_id))
            print("the user is this2",user)
            return user
        except Exception as e:
            logger.exception(f"Database error while fetching user with id {user_id}")
            raise DatabaseExeption("Internal database error") from e

    def get_user_by_email(self, email: str) -> User:
        """
        Retrieve a user by their email.
        
        Args:
            email (str): The email of the user to retrieve.
        
        Returns:
            User: The user with the given email, or None if not found.
        
        Raises:
            DatabaseException: If there is an error while fetching the user.
        """
        try:
            user = self.db.query(User).filter(User.email == email).first()
            return user
        except Exception as e:
            logger.exception(f"Database error while fetching user with email {email}")
            raise DatabaseExeption("Internal database error") from e

    def update_user(self, user: User, update_data: UserUpdate) -> User:
        """
        Update an existing user.
        
        Args:
            user (User): The user to update.
            user_data (UserUpdate): Data to update the user with.
        
        Returns:
            User: The updated user,.
        
        Raises:
            DatabaseException: If there is an error while updating the user.
        """
        try:
            for field, value in update_data.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            self.db.commit()
            return user
        except Exception as e:
            logger.exception(f"Database error while updating user {user.id} with data {update_data.model_dump()}")
            raise DatabaseExeption("Internal database error") from e

    def get_users(self) -> list[User]:
        """
        Retrieve all users.
        
        Returns:
            List[User]: A list of all users.
        
        Raises:
            DatabaseException: If there is an error while fetching the users.
        """
        try:
            return self.db.query(User).all()
        except Exception as e:
            logger.exception("Database error while fetching users")
            raise DatabaseExeption("Internal database error") from e

    def delete_user(self, user: User) -> User:
        """
        Soft delete a user by their ID.
        
        Args:
            user_id (UUID): The ID of the user to delete.
        
        Returns:
            User: The deleted user, or None if not found.
        
        Raises:
            DatabaseException: If there is an error while deleting the user.
        """
        try:
            user.is_deleted = True
            self.db.commit()
            return user
        except Exception as e:
            logger.exception(f"Database error while deleting user {user.id}")
            raise DatabaseExeption("Internal database error") from e