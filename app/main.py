from fastapi import FastAPI

from app.core.config import settings
from app.api.main import main_router


app = FastAPI(
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


app.include_router(main_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    return {"message": "Hello World"}