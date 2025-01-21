from datetime import timedelta
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.schemas.user import UserLogin, UserLoginResponse, TokenPayload
from app.crud import user as user_crud
from app.core.security import verify_password, create_access_token
from app.core.config import settings

router = APIRouter(prefix="/login", tags=["login"])

@router.post("/", response_model=UserLoginResponse)
async def login(db: SessionDep, login_data: UserLogin):

    user = user_crud.get_user_by_email(db=db, email=login_data.email)
    if user is None or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid creds, please try again");

    token_expiry_time = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = TokenPayload(user_id=user.id)
    return UserLoginResponse(token=create_access_token(token_payload.model_dump(), token_expiry_time))