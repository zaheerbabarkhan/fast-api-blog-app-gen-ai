import json
import logging
import traceback
from typing import Union
import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

logger = logging.getLogger("app")

class RequestInfo:
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def method(self) -> str:
        return str(self.request.method)

    @property
    def route(self) -> str:
        return self.request["path"]

    @property
    def ip(self) -> str:
        return str(self.request.client.host)

    @property
    def url(self) -> str:
        return str(self.request.url)

    @property
    def host(self) -> str:
        return str(self.request.url.hostname)

    @property
    def headers(self) -> dict:
        return {key: value for key, value in self.request.headers.items()}

    @property
    def body(self) -> Union[dict, None]:
        return self.request.state.body

class RequestLog(BaseModel):
    req_id: str
    method: str
    route: str
    ip: str
    url: str
    host: str
    body: Union[dict, None]
    headers: dict
    duration_ms: float

class ErrorLog(BaseModel):
    req_id: str
    error_message: str

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.req_id = request_id

        request_body = await request.body()
        try:
            request.state.body = json.loads(request_body.decode("utf-8")) if request_body else None
        except json.JSONDecodeError:
            request.state.body = None

        try:
            # Log the request
            request_info = RequestInfo(request)
            request_log = RequestLog(
                req_id=request_id,
                method=request_info.method,
                route=request_info.route,
                ip=request_info.ip,
                url=request_info.url,
                host=request_info.host,
                body=request_info.body,
                headers=request_info.headers,
                duration_ms=0.0  # Placeholder, will be updated after response
            )
            

            # Process the request
            start_time = time.perf_counter()

            response = await call_next(request)

            # Calculate the duration
            process_time = time.perf_counter() - start_time
            duration_ms = process_time * 1000
            request_log.duration_ms = duration_ms
            logger.info(request_log.model_dump())

            return response

        except Exception as e:
            # Log the error
            error_log = ErrorLog(
                req_id=request_id,
                error_message=str(e),
            )
            logger.error(error_log.model_dump())
            logger.error(traceback.format_exc())