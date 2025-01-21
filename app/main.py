from fastapi import FastAPI

from app.core.config import settings
from app.core.db import get_db
from app.api.main import main_router
app = FastAPI()


app.include_router(main_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    return {"message": "Hello World"}