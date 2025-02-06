from datetime import timedelta
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep, LoginFormData
from app.schemas.user import UserLogin, UserLoginResponse, TokenPayload
from app.crud import user as user_crud
from app.core.security import verify_password, create_access_token
from app.core.config.config import settings

router = APIRouter(prefix="/login", tags=["Login"])

@router.post("/access-token", response_model=UserLoginResponse)
async def login(db: SessionDep, login_data: LoginFormData):

    user = user_crud.get_user_by_email(db=db, email=login_data.username)
    if user is None or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid creds, please try again");

    token_expiry_time = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = TokenPayload(user_id=str(user.id))
    
    return UserLoginResponse(access_token=create_access_token(token_payload.model_dump(), token_expiry_time))