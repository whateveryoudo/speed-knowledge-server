from langchain_community.chat_models.tongyi import ChatTongyi
from app.ai.config import settings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_llm():
    return ChatTongyi(
        model=settings.QWEN_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
    )
