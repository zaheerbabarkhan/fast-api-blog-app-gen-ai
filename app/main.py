from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config.config import settings
from app.api.main import main_router
from app.core.config.llm.llm import LLMService
from app.core.config.config import settings
from app.core.config.logging_config import setup_logging
from app.middlewares.exception_middleware import ExceptionMiddleware
from app.middlewares.logging_middleware import LoggingMiddleware

setup_logging()

app = FastAPI(
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )
# app.add_middleware(ExceptionMiddleware)
app.add_middleware(LoggingMiddleware)

app.include_router(main_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    # raise Exception("An error occurred")
    llm = LLMService()
   
    response = llm.greet()
    return {"message": response.content}