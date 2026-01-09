"""api 路由汇总"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth,user,knowledge, attachment, document, collect
api_router = APIRouter()

api_router.include_router(auth.router, prefix = "/auth")
api_router.include_router(user.router, prefix = "/user")
api_router.include_router(knowledge.router, prefix = "/knowledge")
api_router.include_router(attachment.router, prefix = "/attachment")
api_router.include_router(document.router, prefix = "/document")
api_router.include_router(collect.router, prefix = "/collect")