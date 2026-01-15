from pydantic import BaseModel, Field
from datetime import datetime
class DocumentViewHistoryBase(BaseModel):
    """文档浏览历史基础结构(通用)"""
    document_id: str = Field(..., description="文档ID")
    viewed_datetime: datetime = Field(..., description="浏览时间")
    viewed_user_id: int = Field(..., description="浏览用户id")

class DocumentViewHistoryCreate(DocumentViewHistoryBase):
    """创建文档浏览历史"""
    pass