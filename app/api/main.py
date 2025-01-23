from fastapi import APIRouter
from app.api.routes import user, login, post

main_router = APIRouter()

main_router.include_router(user.router)
main_router.include_router(login.router)
main_router.include_router(post.router)
