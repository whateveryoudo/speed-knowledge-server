from asyncio import streams
from app.core.config import settings
from fastapi import HTTPException, status
from app.schemas.ai import DoubaoQuery
from sqlalchemy.orm import Session
from volcenginesdkarkruntime import Ark
from app.common.enums import AIActionPromptDict, AIAction


class DoubaoService:
    def __init__(self):
        self.volc_endpoint = settings.VOLC_ENDPOINT
        self.volc_api_key = settings.VOLC_API_KEY
        self.volc_model = settings.VOLC_MODEL
    def get_stream_response(self, doubao_in: DoubaoQuery):
        client = Ark(
            base_url=self.volc_endpoint,
            api_key=self.volc_api_key,
        )
        if doubao_in.content is None or doubao_in.content.strip() == "":
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="内容不能为空"
            )
        system_prompt = (
            doubao_in.customPrompt
            if doubao_in.action == AIAction.CUSTOM
            and doubao_in.customPrompt is not None
            and doubao_in.customPrompt.strip() != ""
            else AIActionPromptDict[doubao_in.action]
        )
        response = client.chat.completions.create(
            model=self.volc_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": doubao_in.content},
            ],
            stream=True,
            temperature=0.7,
            top_p=0.9,
            timeout=30000,
        )
        return response
