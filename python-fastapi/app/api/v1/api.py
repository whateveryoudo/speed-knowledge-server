"""api 路由汇总"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    collaborator,
    auth,
    user,
    knowledge,
    team,
    space,
    attachment,
    document,
    collect,
    dashboard,
)
from app.api.v1.endpoints.ai import doubao

api_router = APIRouter()


api_router.include_router(dashboard.router, prefix="/dashboard")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(user.router, prefix="/user")
api_router.include_router(knowledge.router, prefix="/knowledge")
api_router.include_router(team.router, prefix="/team")
api_router.include_router(space.router, prefix="/space")
api_router.include_router(attachment.router, prefix="/attachment")
api_router.include_router(document.router, prefix="/document")
api_router.include_router(document.node_router, prefix="/document-node")
api_router.include_router(collect.router, prefix="/collect")
api_router.include_router(collaborator.router, prefix="/collaborator")
api_router.include_router(doubao.router, prefix="/ai/doubao")
