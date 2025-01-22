from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep, CurrentUser
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.crud import user as user_crud


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(db: SessionDep, user_data: UserCreate):
   
    user = user_crud.get_user_by_email(db=db, email=user_data.email)

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    return user_crud.create_user(db=db, user=user_data)


@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_user(db: SessionDep, current_user: CurrentUser, update_data: UserUpdate):
    if update_data.email:
        existing_user = user_crud.get_user_by_email(db=db, email=update_data.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    return user_crud.update_user(db=db, current_user=current_user, update_data=update_data)
