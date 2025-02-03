from fastapi import FastAPI

from app.core.config import settings
from app.api.main import main_router
from app.genai.llm import LLMService
from app.core.config import settings

app = FastAPI(
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


app.include_router(main_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    print(settings.GROQ_MODEL_NAME)
    print(settings.GROQ_API_KEY)
    llm = LLMService()
   
    response = llm.generate_summary("Hello")
    return {"message": response.content}