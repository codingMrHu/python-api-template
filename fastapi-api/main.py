# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-12 16:29:50
# @Version: 1.0
# @License: H
# @Desc: 
import traceback
from contextlib import asynccontextmanager

from app.api import router
from app.db.init_db import init_default_data
from app.settings import settings
from app.utils.http_middleware import CustomMiddleware
from app.utils.logger import configure
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.staticfiles import StaticFiles
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import applications
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger

async def handle_404_exception(req: Request, exc: StarletteHTTPException) -> ORJSONResponse:
    msg = {
        'status_code': status.HTTP_404_NOT_FOUND,
        'status_message': "Api Path Not Found!"
    }
    logger.error(f'{req.method} {req.url} {exc.status_code} {exc.detail} ')
    return ORJSONResponse(content=msg)

# async def handle_http_exception(req: Request, exc: HTTPException) -> ORJSONResponse:
#     msg = {
#         'status_code': exc.status_code,
#         'status_message': exc.detail['error'] if isinstance(exc.detail, dict) else exc.detail
#     }
#     logger.info(f'{req.method} {req.url} {exc.status_code} {exc.detail} ')
#     return ORJSONResponse(content=msg)


async def handle_request_validation_error(req: Request, exc: RequestValidationError) -> ORJSONResponse:
    msg = {'status_code': status.HTTP_422_UNPROCESSABLE_ENTITY, 'status_message': exc.errors()}
    logger.error(f'{req.method} {req.url} {exc.errors()} {exc.body}')
    return ORJSONResponse(content=msg)

async def handle_generic_exception(req: Request, exc: Exception) -> ORJSONResponse:
    msg = {'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR, 'status_message': 'Internal Server Error'}
    logger.error(f'{req.method} {req.url} Internal Server Error {traceback.format_exc()}')
    return ORJSONResponse(content=msg)

_EXCEPTION_HANDLERS = {
    # HTTPException: handle_http_exception,
    RequestValidationError: handle_request_validation_error,
    Exception: handle_generic_exception,
    StarletteHTTPException:handle_404_exception
}


# 生命周期管理，在应用启动和关闭时执行一些操作
@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize_services()
    init_default_data()
    yield
    # teardown_services()


# ----------docs 使用本地资源
def swagger_monkey_patch(*args, **kwargs):
    """
    Wrap the function which is generating the HTML for the /docs endpoint and
    overwrite the default values for the swagger js and css.
    """
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="/static/swagger/swagger-ui-bundle.min.js",
        swagger_css_url="/static/swagger/swagger-ui.min.css"
        )

# Actual monkey patch
applications.get_swagger_ui_html = swagger_monkey_patch

def create_app():
    """Create the FastAPI app and include the router."""

    app = FastAPI(
        default_response_class=ORJSONResponse,
        exception_handlers=_EXCEPTION_HANDLERS,
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory="static"), name="static")

    origins = [
        '*',
    ]

    @app.get('/health')
    async def get_health():
        return {'status': 'OKkk'}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_middleware(CustomMiddleware)

    @AuthJWT.load_config
    def get_config():
        from app.api.JWT import Settings
        return Settings()

    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(status_code=401, content={'detail': exc.message})

    app.include_router(router)
    return app

configure(settings.logger_conf)

app = create_app()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=7860, workers=1)
