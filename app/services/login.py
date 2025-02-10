from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import LoginFormData, SessionDep
from app.schemas.user import TokenPayload, UserLoginResponse
from app.crud.user import UserCRUD
from app.core.security import verify_password, create_access_token
from app.core.config.config import settings
from app.exceptions.exceptions import AppBaseException, UnauthorizedException
import logging

logger = logging.getLogger(__name__)

class LoginService:
    """
    Service class for handling user login and token generation.
    """

    def __init__(self, db: SessionDep = SessionDep):
        """
        Initialize the LoginService with a database session.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db = db
        self.user_crud = UserCRUD(db=self.db)

    def login(self, login_data: LoginFormData) -> UserLoginResponse:
        """
        Authenticate a user and generate an access token.

        Args:
            login_data (OAuth2PasswordRequestForm): The login data containing username and password.

        Returns:
            UserLoginResponse: The response containing the access token and token type.

        Raises:
            UnauthorizedException: If the user is not found or the password is incorrect.
            DatabaseException: If there is an error in the database operation.
        """
        try:
            user = self.user_crud.get_user_by_email(email=login_data.username)
            if user is None or not verify_password(login_data.password, user.password):
                logger.error("Invalid username or password for user with email %s", login_data.username)
                raise UnauthorizedException("Invalid username or password")

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            token_payload = TokenPayload(user_id=str(user.id))
            access_token = create_access_token(
                payload=token_payload, expires_delta=access_token_expires
            )
            return UserLoginResponse(access_token=access_token, token_type="bearer")
        except UnauthorizedException:
            raise
        except AppBaseException:
            raise
        except Exception as e:
            logger.exception("Internal server error while logging in user with email %s", login_data.username)
            raise BaseException("Internal server error") from e