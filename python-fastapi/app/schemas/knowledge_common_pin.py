from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.knowledge import KnowledgeResponse


class KnowledgeCommonPinBase(BaseModel):
    knowledge_id: str = Field(..., description="知识库ID")
    user_id: int = Field(..., description="用户ID")
    order_index: int = Field(..., description="排序索引")
    id: str = Field(..., description="主键")


class KnowledgeCommonPinResponse(KnowledgeCommonPinBase):
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    knowledge: KnowledgeResponse = Field(..., description="知识库信息")

    class Config:
        from_attributes = True