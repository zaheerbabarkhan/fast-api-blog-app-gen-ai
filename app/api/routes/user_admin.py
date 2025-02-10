import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.api.deps import SessionDep, CurrentUser, get_current_admin
from app.exceptions.exceptions import AppBaseException, ForbiddenException, ResourceAlreadyExistsException, ResourceNotFoundException
from app.models.user import UserRole, UserStatus
from app.schemas.user import UserResponse
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Admin Users"])

@router.patch("/{user_id}/activate", response_model=UserResponse, dependencies=[Depends(get_current_admin)])
async def activate_user(curent_admin: CurrentUser, user_id: uuid.UUID, user_service: UserService = Depends()):
    """
    ## Activates a user.

    This route takes a user ID as a path parameter and activates the user.

    ### Path Parameters:
    - **user_id** (`str`): The ID of the user to be activated.

    ### Raises:
    - **HTTPException**: If the user ID is invalid. Status code: `400`.
    - **HTTPException**: If the user is not found. Status code: `404`.
    - **HTTPException**: If the user is already active. Status code: `409`.
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
        user = user_service.activate_user(user_id, curent_admin)
        return user
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ResourceAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to activate user, please try again later or contact support")


@router.get("/", response_model=List[UserResponse], dependencies=[Depends(get_current_admin)])
async def get_all_users(user_service: UserService = Depends()):
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
    try:
        users = user_service.get_users()
        return users
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to get users, please try again later or contact support") from e
