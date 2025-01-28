import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.api.deps import SessionDep, CurrentUser, get_current_admin
from app.models.user import UserRole, UserStatus
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.crud import user as user_crud

router = APIRouter(prefix="/users", tags=["Admin Users"])

@router.patch("/{user_id}/activate", response_model=UserResponse, dependencies=[Depends(get_current_admin)])
async def activate_user(db: SessionDep, curent_admin: CurrentUser, user_id: str):
    """
    ## Activates a user.

    This route takes a user ID as a path parameter and activates the user.

    ### Path Parameters:
    - **user_id** (`str`): The ID of the user to be activated.

    ### Raises:
    - **HTTPException**: If the user ID is invalid. Status code: `400`.
    - **HTTPException**: If the user is not found. Status code: `404`.
    - **HTTPException**: If the user is already active. Status code: `400`.
    - **HTTPException**: If the current admin does not have permission to activate the user. Status code: `403`.

    ### Response Body:
    - **id** (`uuid.UUID`): The ID of the activated user.
    - **user_name** (`str`): The username of the activated user.
    - **name** (`str`): The name of the activated user.
    - **email** (`EmailStr`): The email of the activated user.
    - **user_role** (`UserRole`): The role of the activated user. Possible values: `SUPER_ADMIN`, `ADMIN`, `AUTHOR`, `READER`.
    - **status** (`UserStatus`): The status of the activated user.
    """
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")
    
    user = user_crud.get_user_by_id(db=db, user_id=(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.status == UserStatus.ACTIVE.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already active")
        
    if user.user_role == UserRole.ADMIN and curent_admin.user_role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can activate admin")

    return user_crud.activate_user(db=db, user=user)



@router.get("/", response_model=List[UserResponse], dependencies=[Depends(get_current_admin)])
async def get_all_users(db: SessionDep):
    """
    ## Retrieves all users.

    This route does not take any parameters.

    ### Response Body:
    - **List[UserResponse]**: A list of users.
        - **id** (`uuid.UUID`): The ID of the user.
        - **user_name** (`str`): The username of the user.
        - **name** (`str`): The name of the user.
        - **email** (`EmailStr`): The email of the user.
        - **user_role** (`UserRole`): The role of the user. Possible values: `SUPER_ADMIN`, `ADMIN`, `AUTHOR`, `READER`.
        - **status** (`UserStatus`): The status of the user.
    """
    return user_crud.get_all_users(db=db)
