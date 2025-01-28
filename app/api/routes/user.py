from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep, CurrentUser
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.crud import user as user_crud


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(db: SessionDep, user_data: UserCreate):
    """
    ## Creates a new user.

    This route takes a JSON body that contains the user data.

    ### Request Body:
    - **user_name** (`str`): The username of the user.
    - **name** (`str`): The name of the user.
    - **email** (`EmailStr`): The email of the user.
    - **user_role** (`Optional[UserRole]`): The role of the user. Possible values: `SUPER_ADMIN`, `ADMIN`, `AUTHOR`, `READER`.
    - **password** (`str`): The password of the user.

    ### Raises:
    - **HTTPException**: If the email is already registered.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the created user.
    - **user_name** (`str`): The username of the created user.
    - **name** (`str`): The name of the created user.
    - **email** (`EmailStr`): The email of the created user.
    - **user_role** (`UserRole`): The role of the created user. Possible values: `SUPER_ADMIN`, `ADMIN`, `AUTHOR`, `READER`.
    - **status** (`UserStatus`): The status of the created user.
    """
    user = user_crud.get_user_by_email(db=db, email=user_data.email)

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    return user_crud.create_user(db=db, user=user_data)


@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: CurrentUser):
    """
    ## Reads the current authenticated user.

    This route does not take any parameters.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the current user.
    - **user_name** (`str`): The username of the current user.
    - **name** (`str`): The name of the current user.
    - **email** (`EmailStr`): The email of the current user.
    - **user_role** (`UserRole`): The role of the current user. Possible values: `SUPER_ADMIN`, `ADMIN`, `AUTHOR`, `READER`.
    - **status** (`UserStatus`): The status of the current user.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_user(db: SessionDep, current_user: CurrentUser, update_data: UserUpdate):
    """
    ## Updates the current authenticated user.

    This route takes a JSON body that contains the updated user data.

    ### Request Body:
    - **user_name** (`Optional[str]`): The updated username of the user.
    - **name** (`Optional[str]`): The updated name of the user.
    - **email** (`Optional[EmailStr]`): The updated email of the user.

    ### Raises:
    - **HTTPException**: If the email is already registered by another user.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the updated user.
    - **user_name** (`str`): The username of the updated user.
    - **name** (`str`): The name of the updated user.
    - **email** (`EmailStr`): The email of the updated user.
    - **user_role** (`UserRole`): The role of the updated user. Possible values: `SUPER_ADMIN`, `ADMIN`, `AUTHOR`, `READER`.
    - **status** (`UserStatus`): The status of the updated user.
    """
    if update_data.email:
        existing_user = user_crud.get_user_by_email(db=db, email=update_data.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    
    return user_crud.update_user(db=db, current_user=current_user, update_data=update_data)

