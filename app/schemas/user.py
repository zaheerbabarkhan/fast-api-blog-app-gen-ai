from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator
import uuid

from app.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    user_name: str
    name: str
    email: EmailStr
    account_role: Optional[UserRole] = UserRole.READER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
        user_name: Optional[str] = None
        name: Optional[str] = None
        email: Optional[EmailStr] = None

        @model_validator(mode="after")
        def check_at_least_one_field(cls, values):
            values_dict = values.dict(exclude_unset=True)
            if not any(values_dict.values()):
                raise ValueError('Provide user_name or name or email to update')
            return values

class UserResponse(UserBase):
    id: uuid.UUID
    status: UserStatus
    account_role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    user_id: str

