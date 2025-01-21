from fastapi import APIRouter, HTTPException
from app.api.deps import SessionDep
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserLoginResponse
from app.crud import user as user_crud
from app.core.security import verify_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(db: SessionDep, user_data: UserCreate):
    user = user_crud.get_user_by_email(db=db, email=user_data.email)

    if user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return user_crud.create_user(db=db, user=user_data)



