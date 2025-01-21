from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.core.security import get_password_hash

from app.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate):
    user.password = get_password_hash(user.password)
    new_user = User(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


