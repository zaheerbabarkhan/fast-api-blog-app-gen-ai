from typing import Annotated
from sqlalchemy import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError    

import logging
import jwt

from app.core.config.database.db import get_db
from app.core.config.config import settings
from app.core import security
from app.models.user import UserRole, User
from app.exceptions.exceptions import AppBaseException, ResourceNotFoundException
from app.crud.user import UserCRUD

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
LoginFormData = Annotated[OAuth2PasswordRequestForm, Depends()]

def get_current_user(token: TokenDep, db: SessionDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_data = payload.get("sub")
        user_id = user_data.split('=')[1].strip("'")
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {str(e)}",
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token validation error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error while decoding token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error",
        )
    
    try:
        
        user = db.get(User, user_id)
        
        if user is None:
            raise ResourceNotFoundException("User not found")
        
        return user
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    
    except AppBaseException:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Not able to fetch user. Please try again later or contact support.",
        )
    



CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_author(current_user: CurrentUser) -> User:
    if current_user.user_role != UserRole.AUTHOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You need to have an author account for this."
        )
    return current_user


def get_current_admin(current_user: CurrentUser) -> User:
    if current_user.user_role.value == UserRole.ADMIN.value or current_user.user_role.value == UserRole.SUPER_ADMIN.value:
        return current_user 
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You need to have an admin account for this."
        )
