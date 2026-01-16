"""应用入口"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import JSON
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.schemas.response import BaseResponse
from app.task.scheduler import start_scheduler
import faulthandler
import signal
import sys

import json


# 注册信号：收到 SIGUSR1 时自动打印当前所有线程的 Python 堆栈
faulthandler.register(signal.SIGUSR1, file=sys.stderr)


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    global scheduler
    scheduler = start_scheduler()
    print("定时任务已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
    print("定时任务已关闭")


# ========== Swagger验证 ==========
def custom_openapi():
    """自定义openapi配置，支持认证"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="FastAPI 应用 API 文档",
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "输入 JWT token，格式: Bearer <token> 或直接输入 token",
        }
    }
    public_paths = [
        "/api/v1/auth/login",
        "/api/v1/auth/getVerificateCode",
        "/api/v1/users",
    ]
    if "paths" in openapi_schema:
        for path, methods in openapi_schema["paths"].items():
            if any(path.endswith(public_path) for public_path in public_paths):
                continue

            for method in methods.values():
                if isinstance(method, dict):
                    if "security" not in method:
                        method["security"] = [{"HTTPBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# ========== CORS 配置 ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ========== 异常处理器 ==========


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器

    Args:
        request (Request): _description_
        exc (HTTPException): _description_

    Returns:
        _type_: _description_
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse.error_response(
            err_code=exc.status_code,
            err_message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """验证异常处理器"""
    errors = exc.errors()
    error_messages = []
    for e in errors:
        loc_str = ".".join(str(loc) for loc in e["loc"])
        error_messages.append(f"{loc_str}: {e['msg']}")
    error_msg = "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=BaseResponse.error_response(
            err_code=422, err_message=f"请求参数校验失败：{error_msg}"
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用的异常处理器"""
    import traceback

    print(f"未处理的异常：{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=BaseResponse.error_response(
            err_code=500, err_message="服务器内部错误"
        ).model_dump(),
    )


# ========== 响应包装中间件 ==========


@app.middleware("http")
async def response_wrapper_middleware(request: Request, call_next):
    """包装响应中间件

    Args:
        request (Request): _description_
        call_next (_type_): _description_

    Returns:
        _type_: _description_
    """
    response = await call_next(request)
    # 跳过一些特殊路径
    # 注意：不能对 "/" 使用 startswith，否则所有路径都会匹配
    if request.url.path in {"/", "/api/v1/ai/doubao/stream", "/api/v1/openapi.json"} or request.url.path.startswith(
        "/api/docs"
    ):
        print(response)
        return response

    if response.status_code >= 400:
        return response

    # 仅对 JSON 响应做统一包装；其余类型（如文件流）直接透传
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            response_data = json.loads(body.decode("utf-8"))
            if isinstance(response_data, dict) and "success" in response_data:
                headers = dict(response.headers)
                # 原 Content-Length 可能与新内容不符，删除让框架重算
                headers.pop("content-length", None)
                return JSONResponse(
                    status_code=response.status_code,
                    content=response_data,
                    headers=headers,
                )
            wrapped_data = BaseResponse.success_reponse(data=response_data).model_dump()
            headers = dict(response.headers)
            headers.pop("content-length", None)
            return JSONResponse(
                status_code=response.status_code,
                content=wrapped_data,
                headers=headers,
            )

        except (json.JSONDecodeError, UnicodeDecodeError):
            return response
    return response


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎进入{settings.APP_NAME}!",
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG
    )
