"""数据访问(渐进式，不会对所有模块都接入repository，目前主要是为了解决循环依赖的问题)"""

from app.repositories.base_repository import BaseRepository, SoftDeleteRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.resource_access_request_repository import ResourceAccessRequestRepository
from app.repositories.resource_grant_repository import ResourceGrantRepository
from app.repositories.permission_group_repository import PermissionGroupRepository

__all__ = [
    "KnowledgeRepository",
    "DocumentRepository",
    "BaseRepository",
    "SoftDeleteRepository",
    "ResourceAccessRequestRepository",
    "ResourceGrantRepository",
    "PermissionGroupRepository",
]
