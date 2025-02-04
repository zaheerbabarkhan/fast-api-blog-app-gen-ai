from fastapi import APIRouter
from app.api.routes import user, login, post, user_admin, genai

main_router = APIRouter()

main_router.include_router(user.router)
main_router.include_router(login.router)
main_router.include_router(post.router)
main_router.include_router(genai.router)

main_router.include_router(user_admin.router, prefix="/backoffice")