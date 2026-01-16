from pydantic import BaseModel, Field
from app.common.enums import AIAction
from typing import Optional

class DoubaoQuery(BaseModel):
    action: AIAction = Field(default=AIAction.CUSTOM)
    content: Optional[str] = Field(default=None)
    customPrompt: Optional[str] = Field(default=None)    