from pydantic import BaseModel, Field
from app.common.enums import CollaboratorRole
from typing import Optional


class InternalQueryInDocumentValid(BaseModel):
    document_id: str = Field(..., description="文档ID")

