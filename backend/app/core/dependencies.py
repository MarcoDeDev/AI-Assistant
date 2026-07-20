from functools import lru_cache

from openai import OpenAI

from app.core.config import settings
from app.llm.base import BaseLLM
from app.llm.openai_llm import OpenAILLM
from app.services.chat_service import ChatService

@lru_cache
def get_openai_client() -> OpenAI:

    return OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


@lru_cache
def get_llm() -> BaseLLM:

    return OpenAILLM(
        client=get_openai_client(),
        model=settings.openai_model,
    )

def get_chat_service() -> ChatService:

    return ChatService(
        llm=get_llm(),
    )