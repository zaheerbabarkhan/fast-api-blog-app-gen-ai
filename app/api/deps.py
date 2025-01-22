from typing import Annotated
from sqlalchemy import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError    

import jwt

from app.core.db import get_db
from app.core.config import settings
from app.core import security
from app.models.user import AccountRole, User
from app.schemas.user import TokenPayload



reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(db: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_data = eval(payload["sub"])
        token_data = TokenPayload(user_id=user_data["user_id"])
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    user = db.get(User, token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inactive user")
    return user



CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_author(current_user: CurrentUser) -> User:
    if current_user.account_role != AccountRole.AUTHOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You need to have an author account for this."
        )
    return current_user

CurrentAuthor = [Annotated, Depends(get_current_author)]

def get_current_admin(current_user: CurrentUser) -> User:
    if current_user.account_role != AccountRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You need to have an author account for this."
        )
    return current_user 

CurrentAdmin = Annotated[User, Depends(get_current_admin)]