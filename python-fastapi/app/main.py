"""应用入口"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import JSON
from app.core.config import settings
from app.api.v1.api import api_router
from app.schemas.response import BaseResponse
import json

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
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
    skip_paths = ["/api/docs", "/"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return response

    # 跳过非json响应
    if isinstance(response, StreamingResponse):
        return response

    if response.status_code >= 400:
        return response

    if isinstance(response, JSONResponse):
        try:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            response_data = json.loads(body.decode("utf-8"))
            if isinstance(response_data, dict) and "success" in response_data:
                return JSONResponse(
                    status_code=response.status_code,
                    content=response_data,
                    headers=dict(response.headers),
                )
            wrapped_data = BaseResponse.success_reponse(data=response_data).model_dump()
            return JSONResponse(
                status_code=response.status_code,
                content=wrapped_data,
                headers=dict(response.headers),
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
