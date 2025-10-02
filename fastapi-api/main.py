# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-12 16:29:50
# @Version: 1.0
# @License: H
# @Desc:
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, applications, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import router
from app.api.errcode.base import BaseErrorCode
from app.api.resp import error_response
from app.db.init_db import init_default_data
from app.settings import settings
from app.utils.http_middleware import CustomMiddleware
from app.utils.logger import configure, logger


async def handle_404_exception(req: Request, exc: StarletteHTTPException) -> ORJSONResponse:
    response = error_response(
        code=status.HTTP_404_NOT_FOUND, message="Api Path Not Found!", detail=f"Requested path: {req.url.path}"
    )
    logger.error(f"{req.method} {req.url} {exc.code} {exc.detail} ")
    return ORJSONResponse(content=response.model_dump())


async def handle_http_exception(req: Request, exc: HTTPException) -> ORJSONResponse:
    error_detail = exc.detail["error"] if isinstance(exc.detail, dict) else exc.detail
    response = error_response(
        code=exc.status_code, message=error_detail, detail=f"HTTP Exception occurred at {req.url.path}"
    )
    logger.info(f"{req.method} {req.url} {exc.status_code} {exc.detail} ")
    return ORJSONResponse(content=response.model_dump())


async def handle_request_validation_error(req: Request, exc: RequestValidationError) -> ORJSONResponse:
    response = error_response(
        code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Request validation failed", detail=str(exc.errors())
    )
    logger.error(f"{req.method} {req.url} {exc.errors()} {exc.body}")
    return ORJSONResponse(content=response.model_dump())


async def handle_base_error_code(req: Request, exc: BaseErrorCode) -> ORJSONResponse:
    """处理自定义业务异常"""
    response = error_response(code=exc.code, message=exc.message, detail=f"Business error occurred at {req.url.path}")
    logger.info(f"{req.method} {req.url} {exc.code} {exc.message}")
    return ORJSONResponse(content=response.model_dump())


async def handle_generic_exception(req: Request, exc: Exception) -> ORJSONResponse:
    response = error_response(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Internal Server Error", detail=traceback.format_exc()
    )
    logger.error(f"{req.method} {req.url} Internal Server Error {traceback.format_exc()}")
    return ORJSONResponse(content=response.model_dump())


_EXCEPTION_HANDLERS = {
    BaseErrorCode: handle_base_error_code,
    HTTPException: handle_http_exception,
    RequestValidationError: handle_request_validation_error,
    Exception: handle_generic_exception,
    StarletteHTTPException: handle_404_exception,
}


# 生命周期管理，在应用启动和关闭时执行一些操作
@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize_services()
    init_default_data()
    yield
    # teardown_services()


def create_app():
    """Create the FastAPI app and include the router."""

    app = FastAPI(
        default_response_class=ORJSONResponse,
        exception_handlers=_EXCEPTION_HANDLERS,
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory="static"), name="static")

    origins = [
        "*",
    ]

    @app.get("/health")
    async def get_health():
        return {"status": "OKkk"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(CustomMiddleware)

    @AuthJWT.load_config
    def get_config():
        from app.api.JWT import Settings

        return Settings()

    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(code=401, content={"detail": exc.message})

    app.include_router(router)
    return app


configure(settings.logger_conf)

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860, workers=1)
