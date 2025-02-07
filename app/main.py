from fastapi import FastAPI

from app.core.config.config import settings
from app.api.main import main_router
from app.core.config.llm.llm import LLMService
from app.core.config.config import settings
from app.core.config.logging_config import setup_logging
from app.middleware.exception_middleware import ExceptionMiddleware
from app.middleware.logging_middleware import LoggingMiddleware

setup_logging()

app = FastAPI(
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(ExceptionMiddleware)
app.add_middleware(LoggingMiddleware)

app.include_router(main_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    # raise Exception("An error occurred")
    llm = LLMService()
   
    response = llm.greet()
    return {"message": response.content}