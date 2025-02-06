import sys
import os


# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config.database.db import engine, Base, SessionLocal
from app.core.config.config import settings

from app.models.user import User, UserRole
from app.models.post import Post
from app.models.comment import Comment

from app.crud import user as user_crud
from app.schemas.user import UserCreate


# Drop all tables
# Base.metadata.drop_all(bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Create a super admin user
super_admin = UserCreate(
    name=settings.SUPER_ADMIN_NAME,
    email=settings.SUPER_ADMIN_EMAIL,
    user_name=settings.SUPER_ADMIN_USER_NAME,
    password=settings.SUPER_ADMIN_PASSWORD,
    user_role=UserRole.SUPER_ADMIN,
)

# user_crud.create_user(SessionLocal(),super_admin)
print("Database tables created successfully!")
