from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import LoginFormData
from app.schemas.user import UserLoginResponse
from app.services.login import LoginService
from app.exceptions.exceptions import UnauthorizedException, AppBaseException, AppBaseException

router = APIRouter(prefix="/login", tags=["Login"])

@router.post("/access-token", response_model=UserLoginResponse)
async def login(login_data: LoginFormData, login_service: LoginService = Depends()):
    """
    ## Authenticate a user and generate an access token.

    This route takes a JSON body that contains the login data.

    ### Request Body:
    - **username** (`str`): The username of the user.
    - **password** (`str`): The password of the user.

    ### Raises:
    - **HTTPException**: If the username or password is incorrect.
    - **HTTPException**: If there is a database error.

    ### Response Body:
    - **access_token** (`str`): The access token for the authenticated user.
    - **token_type** (`str`): The type of the token, which is "bearer".
    """
    try:
        return login_service.login(login_data=login_data)
    
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    except AppBaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")