from sqlalchemy.orm import Session

from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate):
    user.password = get_password_hash(user.password)
    new_user = User(**user.model_dump())
    if user.user_role.value == UserRole.ADMIN.value or user.user_role.value == UserRole.AUTHOR.value:
        new_user.status = UserStatus.IN_ACTIVE.value
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)    
    return new_user



def update_user(db: Session, current_user: User, update_data: UserUpdate):
    update_values = update_data.model_dump(exclude_unset=True)
    for key, value in update_values.items():
        setattr(current_user, key, value)

    db.commit()
    return current_user 

def activate_user(db: Session, user: User) -> User:
    user.status = UserStatus.ACTIVE.value
    db.commit()
    return user

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User,user_id)

