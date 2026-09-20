"""api 路由汇总"""

from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.endpoints import (
    auth,
    user,
    knowledge,
    team,
    space,
    attachment,
    document,
    collect,
    dashboard,
    notification,
    internal,
    search,
    resource,
    resource_invitation,
    resource_access_request,
    resource_collaboration,
)

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
api_router.include_router(resource_invitation.router, prefix="/resource-invitation")
api_router.include_router(resource.router, prefix="/resource")
api_router.include_router(notification.router, prefix="/notification")
api_router.include_router(internal.router, prefix="/internal")
api_router.include_router(search.router, prefix="/search")
api_router.include_router(resource_access_request.router, prefix="/access-request")
api_router.include_router(resource_collaboration.router, prefix="/resource-collaboration")
# AI 依赖在 [dependency-groups].ai；未 ENABLE_AI 时不要顶层 import，否则缺包会启动失败
if settings.ENABLE_AI:
    from app.api.v1.endpoints.ai import doubao, robot

    api_router.include_router(doubao.router, prefix="/ai/doubao")
    api_router.include_router(robot.router, prefix="/ai/robot")