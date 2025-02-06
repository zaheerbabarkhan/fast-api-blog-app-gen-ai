from fastapi import FastAPI

from app.core.config.config import settings
from app.api.main import main_router
from app.core.config.llm import LLMService
from app.core.config.config import settings

app = FastAPI(
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


app.include_router(main_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():

    llm = LLMService()
   
    response = llm.generate_summary("Hello")
    return {"message": response.content}