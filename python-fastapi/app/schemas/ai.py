from pydantic import BaseModel, Field
from app.common.enums import AIAction
from typing import Optional, Dict, Any, List, Literal

class DoubaoQuery(BaseModel):
    action: AIAction = Field(default=AIAction.CUSTOM)
    content: Optional[str] = Field(default=None)
    customPrompt: Optional[str] = Field(default=None)  

class Suggestion(BaseModel):
    id: str = Field(default="")
    node_id: str = Field(default="")
    message: str = Field(default="")
    rule_id: str = Field(default="")
    text_index: Optional[int] = Field(default=None)
    severity: Literal['error', 'warning', 'info'] = Field(default="info")
    fixCommand: Optional[Dict[str, Any]] = Field(default=None)
    meta: Optional[Dict[str, Any]] = Field(default={})
    

class CheckDocumentRequest(BaseModel):
    doc: Dict[str, Any] = Field(default={})
    rules: List[Dict[str, Any]] = Field(default=[])

class CheckDocumentResponse(BaseModel):
    suggestions: List[Suggestion] = Field(default=[])