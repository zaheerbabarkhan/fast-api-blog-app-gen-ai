from sqlalchemy.orm import Session

from app.models.user import User, AccountRole
from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate):
    user.password = get_password_hash(user.password)
    new_user = User(**user.model_dump())

    if user.account_role == AccountRole.ADMIN.value or user.account_role == AccountRole.AUTHOR.value:
        new_user.is_active = False
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def update_user(db: Session, current_user: User, update_data: UserUpdate):
    update_values = update_data.model_dump(exclude_unset=True)
    for key, value in update_values.items():
        setattr(current_user, key, value)

    db.commit()
    return current_user 
