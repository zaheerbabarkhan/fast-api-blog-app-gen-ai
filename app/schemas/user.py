from pydantic import BaseModel, EmailStr
import uuid

class UserBase(BaseModel):
    user_name: str
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    user_id: uuid.UUID